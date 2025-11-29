"""
Simple test script to demonstrate how ai_engine.py processes video frames from warehose.mp4
This shows the complete workflow without needing Flask.
"""
import cv2
import time
from ai_engine import analyze_image_local

# Configuration
VIDEO_SOURCE = "warehose.mp4"
AI_CHECK_INTERVAL = 2  # Check every 2 seconds
MAX_FRAMES_TO_PROCESS = 10  # Process only first 10 AI checks for demo
FRAME_SKIP_RATE = 2  # Skip frames between AI checks (read every Nth frame)
RESIZE_WIDTH = 512   # Smaller resolution for faster processing
RESIZE_HEIGHT = 384  # Smaller resolution for faster processing

# Safety prompt
SAFETY_PROMPT = """
Are they wearing a hard hat? 
JSON format only: {"violation": boolean, "reason": "short text"}
If no hard hat, violation is true.
"""

def main():
    print(f"📹 Processing video: {VIDEO_SOURCE}")
    
    video_capture = cv2.VideoCapture(VIDEO_SOURCE)
    
    if not video_capture.isOpened():
        print(f"❌ Error: Could not open video file {VIDEO_SOURCE}")
        return
    
    frame_count = 0
    frames_read = 0
    ai_check_count = 0
    last_ai_check = time.time()
    
    while ai_check_count < MAX_FRAMES_TO_PROCESS:
        ret, frame = video_capture.read()
        if not ret:
            video_capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue
        
        frames_read += 1
        
        # Skip frames to reduce processing load
        if frames_read % FRAME_SKIP_RATE != 0:
            continue
        
        frame_count += 1
        current_time = time.time()
        
        # Resize frame for faster processing (smaller resolution)
        small_frame = cv2.resize(frame, (RESIZE_WIDTH, RESIZE_HEIGHT), interpolation=cv2.INTER_AREA)
        
        # Check if it's time to send to AI
        if current_time - last_ai_check >= AI_CHECK_INTERVAL:
            ai_check_count += 1
            ai_result = analyze_image_local(small_frame, SAFETY_PROMPT, jpeg_quality=75, max_size=(RESIZE_WIDTH, RESIZE_HEIGHT))
            
            status = "VIOLATION" if ai_result.get("violation") else "SAFE"
            print(f"Check #{ai_check_count}: {status} - {ai_result.get('reason', '')}")
            
            last_ai_check = current_time
        
        # Small delay to simulate real-time processing
        time.sleep(0.01)
    
    video_capture.release()
    print(f"\n✅ Complete: {ai_check_count} AI checks performed")

if __name__ == "__main__":
    main()

