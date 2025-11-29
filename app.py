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
lock = threading.Lock()

# --- Config ---
VIDEO_SOURCE = "warehose.mp4" # ใช้ไฟล์วิดีโอแทนกล้องจริง เพื่อความชัวร์ตอนเดโม
AI_CHECK_INTERVAL = 1 # ส่ง AI ตรวจทุกๆ 1 วินาที (เครื่องช้าให้เพิ่มเลขนี้)

# --- The Hard-coded Prompt (สำหรับโมเดลเล็ก) ---
SAFETY_PROMPT = """
Are they wearing a hard hat? 
JSON format only: {"violation": boolean, "reason": "short text"}
If no hard hat, violation is true.
"""

def video_loop():
    """Thread สำหรับอ่านวิดีโอและส่ง AI"""
    global current_frame, latest_ai_result, video_capture
    print(f"📹 Opening video file: {VIDEO_SOURCE}")
    video_capture = cv2.VideoCapture(VIDEO_SOURCE)
    
    if not video_capture.isOpened():
        print(f"❌ Error: Could not open video file {VIDEO_SOURCE}")
        return
    
    print(f"✅ Video opened successfully. Processing frames...")
    print(f"🤖 AI will analyze frames every {AI_CHECK_INTERVAL} second(s)")
    
    frame_count = 0
    last_ai_check = time.time()

    while True:
        ret, frame = video_capture.read()
        if not ret:
            print("🔄 Video ended, looping back to start...")
            video_capture.set(cv2.CAP_PROP_POS_FRAMES, 0) # วนลูปวิดีโอ
            continue
            
        frame_count += 1
        
        # Resize ภาพให้เล็กลงก่อนส่ง AI เพื่อความเร็ว (สำคัญสำหรับ Local model)
        small_frame = cv2.resize(frame, (640, 480))

        with lock:
            current_frame = small_frame.copy()

        # --- AI Check Logic ---
        now = time.time()
        if now - last_ai_check > AI_CHECK_INTERVAL:
            print(f"\n📸 Frame #{frame_count}: Sending to AI engine...")
            # เรียกใช้ Local AI (ตรงนี้จะบล็อก Thread นี้สักพักนึง)
            ai_result = analyze_image_local(small_frame, SAFETY_PROMPT)
            
            print(f"✅ AI Result: {ai_result}")
            
            with lock:
                latest_ai_result = ai_result
            
            last_ai_check = now # Reset เวลา
        
        time.sleep(0.03) # ประมาณ 30 FPS

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

            (flag, encodedImage) = cv2.imencode(".jpg", display_frame)
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
    print("🚀 Local Server starting at http://0.0.0.0:5000")
    # host='0.0.0.0' เพื่อให้เครื่องอื่นในวง LAN เปิดดูได้ (ถ้าต้องการ)
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)