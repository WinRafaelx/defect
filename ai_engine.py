import requests
import base64
import json
import cv2

# URL ของ Ollama ที่รันอยู่บนเครื่องเรา (Default port)
OLLAMA_URL = "http://localhost:11434/api/generate"
# ชื่อโมเดลที่ pull มา
MODEL_NAME = "qwen3-vl:8b" 

def analyze_image_local(image_cv2, prompt):
    """
    รับภาพจาก OpenCV -> แปลงเป็น Base64 -> ส่งให้ Ollama -> คืนค่า JSON string
    """
    try:
        # 1. Convert OpenCV image to JPEG bytes then to Base64 string
        _, buffer = cv2.imencode('.jpg', image_cv2)
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

        # 3. Send request to local Ollama instance
        print("🤖 Sending to local AI model...")
        response = requests.post(OLLAMA_URL, json=payload, timeout=30) # timeout เผื่อเครื่องช้า
        response.raise_for_status()

        # 4. Parse response
        result_json = response.json()
        # Some models (like qwen3-vl) put JSON output in "thinking" field instead of "response"
        ai_text_response = result_json.get("response", "")
        if not ai_text_response or ai_text_response.strip() == "":
            ai_text_response = result_json.get("thinking", "{}")
        
        print(f"🤖 AI Answer: {ai_text_response}")
        
        # พยายามแปลง String เป็น Python Dict
        # (โมเดลเล็กบางทีอาจจะตอบ JSON เพี้ยนๆ ต้องระวังตรงนี้ใน Hackathon)
        try:
            return json.loads(ai_text_response)
        except json.JSONDecodeError:
             print("⚠️ AI did not return valid JSON. Using raw text.")
             # Hack: ถ้าแกะ JSON ไม่ได้ ให้ถือว่าผิดกฎไว้ก่อน หรือ return ค่า default
             return {"violation": True, "reason": "AI JSON Error: " + ai_text_response}

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

    # Prompt สำหรับโมเดลเล็ก: ต้องชัดเจนมากๆ
    TEST_PROMPT = """
    Look at the person. Are they wearing a hard hat (helmet)? 
    JSON output required: {"wearing_helmet": boolean, "violation": boolean}
    If wearing_helmet is false, violation must be true.
    """
    
    result = analyze_image_local(test_img, TEST_PROMPT)
    print("\n--- Final Result ---")
    print(result)