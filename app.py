from flask import Flask, render_template, Response, jsonify
import cv2
import threading
import time
from ai_engine import analyze_image_local # Import ฟังก์ชันที่เราเขียนเมื่อกี้

app = Flask(__name__)

# --- Global Variables (Hackathon style state management) ---
video_capture = None
current_frame = None
latest_ai_result = {"violation": False, "reason": "System Starting..."}
ai_processing = False  # Flag to prevent multiple simultaneous AI calls
lock = threading.Lock()

# --- Config ---
VIDEO_SOURCE = "warehose.mp4" # ใช้ไฟล์วิดีโอแทนกล้องจริง เพื่อความชัวร์ตอนเดโม
AI_CHECK_INTERVAL = 1 # ส่ง AI ตรวจทุกๆ 1 วินาที (เครื่องช้าให้เพิ่มเลขนี้)
FRAME_SKIP_RATE = 2  # Skip frames between AI checks (read every Nth frame)
RESIZE_WIDTH = 512   # Smaller resolution for faster processing (was 640)
RESIZE_HEIGHT = 384  # Smaller resolution for faster processing (was 480)

# --- Safety Prompt Configuration ---
# IMPORTANT: Longer prompts significantly slow down processing (216% slower!)
# Use optimized prompts for better performance while maintaining effectiveness

# Option 1: Use optimized prompts (RECOMMENDED - faster)
from prompt_templates import OPTIMIZED_SIMPLE, OPTIMIZED_STANDARD, OPTIMIZED_COMPREHENSIVE
SAFETY_PROMPT = OPTIMIZED_STANDARD  # Balanced: fast + detailed enough

# Option 2: Use simple inline prompt (fastest, least detailed)
# SAFETY_PROMPT = """
# Are they wearing a hard hat? 
# JSON format only: {"violation": boolean, "reason": "short text"}
# If no hard hat, violation is true.
# """

# Option 3: Use original longer prompts (slower but more detailed)
# from prompt_templates import STANDARD_PROMPT, COMPREHENSIVE_PROMPT
# SAFETY_PROMPT = STANDARD_PROMPT  # or COMPREHENSIVE_PROMPT

# Option 4: Build custom prompt
# from prompt_templates import build_custom_prompt
# SAFETY_PROMPT = build_custom_prompt(check_hard_hat=True, check_vest=True, check_boots=True)

def process_ai_async(frame, frame_num):
    """Process AI in background thread to avoid blocking video reading"""
    global latest_ai_result, ai_processing
    try:
        # Use optimize_prompt=True to automatically compress prompts for faster processing
        ai_result = analyze_image_local(
            frame, 
            SAFETY_PROMPT, 
            jpeg_quality=75, 
            max_size=(RESIZE_WIDTH, RESIZE_HEIGHT),
            optimize_prompt=True  # Enable prompt optimization for speed
        )
        with lock:
            latest_ai_result = ai_result
    except Exception as e:
        print(f"❌ AI processing error: {e}")
        with lock:
            latest_ai_result = {"violation": False, "reason": f"AI Error: {str(e)}"}
    finally:
        ai_processing = False

def video_loop():
    """Thread สำหรับอ่านวิดีโอและส่ง AI (Optimized with frame skipping)"""
    global current_frame, latest_ai_result, video_capture, ai_processing
    print(f"📹 Opening video file: {VIDEO_SOURCE}")
    video_capture = cv2.VideoCapture(VIDEO_SOURCE)
    
    if not video_capture.isOpened():
        print(f"❌ Error: Could not open video file {VIDEO_SOURCE}")
        return
    
    # Get video FPS to calculate optimal frame skipping
    video_fps = video_capture.get(cv2.CAP_PROP_FPS) or 30
    frames_to_skip = max(1, int(video_fps * AI_CHECK_INTERVAL / FRAME_SKIP_RATE))
    
    frame_count = 0
    frames_read = 0
    last_ai_check = time.time()

    while True:
        ret, frame = video_capture.read()
        if not ret:
            video_capture.set(cv2.CAP_PROP_POS_FRAMES, 0) # วนลูปวิดีโอ
            continue
        
        frames_read += 1
        
        # Skip frames to reduce processing load
        if frames_read % FRAME_SKIP_RATE != 0:
            continue
            
        frame_count += 1
        
        # Resize ภาพให้เล็กลงก่อนส่ง AI เพื่อความเร็ว (สำคัญสำหรับ Local model)
        small_frame = cv2.resize(frame, (RESIZE_WIDTH, RESIZE_HEIGHT), interpolation=cv2.INTER_AREA)

        with lock:
            current_frame = small_frame.copy()

        # --- AI Check Logic (Non-blocking) ---
        now = time.time()
        if now - last_ai_check >= AI_CHECK_INTERVAL and not ai_processing:
            ai_processing = True
            # Process AI in separate thread to avoid blocking video reading
            ai_thread = threading.Thread(target=process_ai_async, args=(small_frame, frame_count), daemon=True)
            ai_thread.start()
            last_ai_check = now # Reset เวลา
        
        # Reduced sleep since we're skipping frames
        time.sleep(0.01)

def generate_mjpeg():
    """Generator สำหรับส่งภาพไปแสดงบนเว็บ"""
    global current_frame
    while True:
        with lock:
            if current_frame is None: continue
            # วาดผลลัพธ์ลงบนภาพเลย (ง่ายสุดสำหรับ Hackathon)
            display_frame = current_frame.copy()
            
            status_text = "SAFE"
            color = (0, 255, 0) # Green
            if latest_ai_result.get("violation") == True:
                status_text = f"VIOLATION: {latest_ai_result.get('reason', '')}"
                color = (0, 0, 255) # Red
            
            cv2.putText(display_frame, status_text, (10, 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

            # Use lower quality for faster encoding
            encode_params = [cv2.IMWRITE_JPEG_QUALITY, 80]
            (flag, encodedImage) = cv2.imencode(".jpg", display_frame, encode_params)
            if not flag: continue
            
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
              bytearray(encodedImage) + b'\r\n')
        time.sleep(0.1)

# --- Flask Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_mjpeg(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/status')
def get_status():
    # API สำหรับ Frontend มาดึงสถานะ (ถ้าต้องการทำ UI แยก)
    with lock:
        return jsonify(latest_ai_result)

if __name__ == '__main__':
    # Start Video Thread
    t = threading.Thread(target=video_loop, daemon=True)
    t.start()
    
    # Start Flask server
    print("🚀 Server starting at http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)