import requests
import base64
import json
import cv2
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# URL ของ Ollama ที่รันอยู่บนเครื่องเรา (Default port)
OLLAMA_URL = "http://localhost:11434/api/generate"
# ชื่อโมเดลที่ pull มา
MODEL_NAME = "qwen3-vl:8b"

# Create session with connection pooling for faster requests
_session = None
def get_session():
    global _session
    if _session is None:
        _session = requests.Session()
        # Retry strategy for robustness
        retry_strategy = Retry(
            total=2,
            backoff_factor=0.1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=1, pool_maxsize=1)
        _session.mount("http://", adapter)
    return _session 

def analyze_image_local(image_cv2, prompt, jpeg_quality=75, max_size=(512, 384)):
    """
    รับภาพจาก OpenCV -> แปลงเป็น Base64 -> ส่งให้ Ollama -> คืนค่า JSON string
    
    Optimizations:
    - jpeg_quality: Lower quality (75) for faster encoding/transmission (default was 95)
    - max_size: Resize to smaller dimensions for faster processing
    """
    try:
        # 0. Resize to smaller dimensions if needed (faster processing)
        h, w = image_cv2.shape[:2]
        if w > max_size[0] or h > max_size[1]:
            scale = min(max_size[0] / w, max_size[1] / h)
            new_w = int(w * scale)
            new_h = int(h * scale)
            image_cv2 = cv2.resize(image_cv2, (new_w, new_h), interpolation=cv2.INTER_AREA)
        
        # 1. Convert OpenCV image to JPEG bytes with lower quality for speed
        encode_params = [cv2.IMWRITE_JPEG_QUALITY, jpeg_quality]
        _, buffer = cv2.imencode('.jpg', image_cv2, encode_params)
        jpg_as_text = base64.b64encode(buffer).decode('utf-8')

        # 2. Construct payload for Ollama API
        # เคล็ดลับ: โมเดลเล็กๆ ต้องการ Prompt ที่ตรงไปตรงมา สั้นๆ ง่ายๆ
        payload = {
            "model": MODEL_NAME,
            "prompt": prompt + " Respond strictly in JSON format only.",
            "images": [jpg_as_text],
            "stream": False, # สำคัญมาก: ต้องตั้งเป็น False เพื่อให้ได้คำตอบทีเดียว
            "format": "json"  # บังคับให้ Ollama พยายามตอบเป็น JSON (ฟีเจอร์ใหม่)
        }

        # 3. Send request to local Ollama instance (using session for connection reuse)
        session = get_session()
        response = session.post(OLLAMA_URL, json=payload, timeout=30) # timeout เผื่อเครื่องช้า
        response.raise_for_status()

        # 4. Parse response
        result_json = response.json()
        # Some models (like qwen3-vl) put JSON output in "thinking" field instead of "response"
        ai_text_response = result_json.get("response", "")
        if not ai_text_response or ai_text_response.strip() == "":
            ai_text_response = result_json.get("thinking", "{}")
        
        # พยายามแปลง String เป็น Python Dict
        # (โมเดลเล็กบางทีอาจจะตอบ JSON เพี้ยนๆ ต้องระวังตรงนี้ใน Hackathon)
        try:
            result = json.loads(ai_text_response)
            
            # Determine violation based on missing mandatory PPE items
            # Mandatory items: hard hat, safety vest, safety boots
            missing_ppe = result.get("missing_ppe", [])
            if isinstance(missing_ppe, str):
                # Handle case where missing_ppe might be a string
                missing_ppe = [missing_ppe] if missing_ppe else []
            
            # Check if any mandatory items are missing
            mandatory_items = ["hard hat", "helmet", "safety vest", "high-visibility", "safety boots", "boots"]
            has_mandatory_violation = any(
                any(mandatory in str(item).lower() for mandatory in mandatory_items)
                for item in missing_ppe
            )
            
            # Set violation based on missing mandatory items
            result["violation"] = has_mandatory_violation
            
            # Update reason only if violation detected, remove reason if safe
            if has_mandatory_violation:
                if "reason" not in result:
                    result["reason"] = f"Missing mandatory PPE: {', '.join(missing_ppe)}"
            else:
                # Remove reason for safe cases
                result.pop("reason", None)
            
            return result
        except json.JSONDecodeError:
             print("⚠️ AI did not return valid JSON. Using raw text.")
             # Hack: ถ้าแกะ JSON ไม่ได้ ให้ถือว่าผิดกฎไว้ก่อน หรือ return ค่า default
             return {"violation": True, "reason": "AI JSON Error: " + ai_text_response, "missing_ppe": []}

    except Exception as e:
        print(f"❌ Error calling local AI: {e}")
        return {"violation": True, "error": str(e)}

# --- Test Zone (รันเทสตรงนี้ก่อน) ---
if __name__ == "__main__":
    # หารูป test.jpg มาวางไว้ที่เดียวกับไฟล์นี้
    test_img = cv2.imread("testo.png") 
    if test_img is None:
        print("หาไฟล์รูป testo.png ไม่เจอ")
        exit()

    # Import centralized prompt
    from config import SAFETY_PROMPT
    
    result = analyze_image_local(test_img, SAFETY_PROMPT)
    print("\n--- Final Result ---")
    # Only show reason if there's a violation
    if result.get("violation"):
        print(result)
    else:
        # Remove reason for safe cases in display
        display_result = {k: v for k, v in result.items() if k != "reason"}
        print(display_result)