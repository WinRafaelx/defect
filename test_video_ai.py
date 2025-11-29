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

# Safety prompt
SAFETY_PROMPT = """
Are they wearing a hard hat? 
JSON format only: {"violation": boolean, "reason": "short text"}
If no hard hat, violation is true.
"""

def main():
    print("=" * 60)
    print("VIDEO PROCESSING WITH AI ENGINE - DEMONSTRATION")
    print("=" * 60)
    print(f"\n📹 Opening video file: {VIDEO_SOURCE}")
    
    video_capture = cv2.VideoCapture(VIDEO_SOURCE)
    
    if not video_capture.isOpened():
        print(f"❌ Error: Could not open video file {VIDEO_SOURCE}")
        print("   Please make sure the file exists in the current directory.")
        return
    
    # Get video properties
    fps = video_capture.get(cv2.CAP_PROP_FPS)
    frame_count_total = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count_total / fps if fps > 0 else 0
    
    print(f"✅ Video opened successfully!")
    print(f"   - FPS: {fps:.2f}")
    print(f"   - Total frames: {frame_count_total}")
    print(f"   - Duration: {duration:.2f} seconds")
    print(f"\n🤖 AI will analyze frames every {AI_CHECK_INTERVAL} second(s)")
    print(f"   Processing first {MAX_FRAMES_TO_PROCESS} AI checks for demonstration...")
    print("\n" + "-" * 60)
    
    frame_count = 0
    ai_check_count = 0
    last_ai_check = time.time()
    
    print("\n🔄 Starting video processing loop...\n")
    
    while ai_check_count < MAX_FRAMES_TO_PROCESS:
        ret, frame = video_capture.read()
        if not ret:
            print("\n🔄 Video ended, looping back to start...")
            video_capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue
        
        frame_count += 1
        current_time = time.time()
        
        # Resize frame for faster processing
        small_frame = cv2.resize(frame, (640, 480))
        
        # Check if it's time to send to AI
        if current_time - last_ai_check >= AI_CHECK_INTERVAL:
            ai_check_count += 1
            print(f"\n{'='*60}")
            print(f"AI CHECK #{ai_check_count} (Frame #{frame_count})")
            print(f"{'='*60}")
            print(f"📸 Frame dimensions: {small_frame.shape[1]}x{small_frame.shape[0]}")
            print(f"⏰ Time: {current_time - last_ai_check:.2f}s since last check")
            
            # Call AI engine
            print("\n📤 Calling ai_engine.analyze_image_local()...")
            print(f"   Prompt: {SAFETY_PROMPT.strip()}")
            
            ai_result = analyze_image_local(small_frame, SAFETY_PROMPT)
            
            print(f"\n📥 AI Engine returned:")
            print(f"   Result: {ai_result}")
            
            # Display result
            if ai_result.get("violation"):
                print(f"   ⚠️  STATUS: VIOLATION DETECTED")
                print(f"   Reason: {ai_result.get('reason', 'N/A')}")
            else:
                print(f"   ✅ STATUS: SAFE")
                if "reason" in ai_result:
                    print(f"   Reason: {ai_result.get('reason', 'N/A')}")
            
            last_ai_check = current_time
            print(f"\n{'='*60}\n")
        
        # Small delay to simulate real-time processing
        time.sleep(0.01)
    
    video_capture.release()
    print("\n" + "=" * 60)
    print("DEMONSTRATION COMPLETE")
    print("=" * 60)
    print(f"\n📊 Summary:")
    print(f"   - Total frames read: {frame_count}")
    print(f"   - AI checks performed: {ai_check_count}")
    print(f"\n💡 To run the full Flask web application, use: python app.py")

if __name__ == "__main__":
    main()

