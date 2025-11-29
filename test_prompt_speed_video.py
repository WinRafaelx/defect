"""
Video-Based Benchmark: Test prompt length impact on video processing speed

This test processes actual video frames with different prompt lengths
to show real-world performance impact.
"""
import cv2
import time
from ai_engine import analyze_image_local
from prompt_templates import SIMPLE_PROMPT, STANDARD_PROMPT, COMPREHENSIVE_PROMPT

VIDEO_SOURCE = "warehose.mp4"
FRAMES_TO_TEST = 5  # Number of frames to test per prompt

# Define prompts of different lengths
PROMPTS = {
    "Tiny": "Check hard hat. JSON: {\"violation\": boolean}",
    "Small": SIMPLE_PROMPT,
    "Medium": STANDARD_PROMPT,
    "Large": COMPREHENSIVE_PROMPT,
}

def test_video_with_prompt(prompt_name, prompt_text, video_path, num_frames=5):
    """Test processing speed with video frames"""
    print(f"\n{'='*70}")
    print(f"Testing: {prompt_name} ({len(prompt_text):,} chars)")
    print(f"{'='*70}")
    
    video = cv2.VideoCapture(video_path)
    if not video.isOpened():
        print(f"❌ Could not open video: {video_path}")
        return None
    
    times = []
    frame_count = 0
    processed = 0
    
    while processed < num_frames:
        ret, frame = video.read()
        if not ret:
            video.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue
        
        frame_count += 1
        # Process every 10th frame to get varied frames
        if frame_count % 10 != 0:
            continue
        
        # Resize for processing
        small_frame = cv2.resize(frame, (512, 384), interpolation=cv2.INTER_AREA)
        
        print(f"  Frame {processed + 1}/{num_frames}...", end=" ", flush=True)
        start_time = time.time()
        
        try:
            result = analyze_image_local(
                small_frame,
                prompt_text,
                jpeg_quality=75,
                max_size=(512, 384)
            )
            elapsed = time.time() - start_time
            times.append(elapsed)
            status = "✓" if result.get("violation") is not None else "⚠"
            print(f"{status} {elapsed:.2f}s")
            processed += 1
        except Exception as e:
            print(f"✗ Error: {e}")
        
        if processed >= num_frames:
            break
    
    video.release()
    
    if times:
        return {
            "name": prompt_name,
            "length": len(prompt_text),
            "times": times,
            "avg": sum(times) / len(times),
            "min": min(times),
            "max": max(times)
        }
    return None

def main():
    print("="*70)
    print("VIDEO PROCESSING: PROMPT LENGTH vs SPEED BENCHMARK")
    print("="*70)
    print(f"\n📹 Video source: {VIDEO_SOURCE}")
    print(f"📊 Testing {FRAMES_TO_TEST} frames per prompt")
    print(f"🔄 Each prompt will be tested on the same video frames")
    
    results = []
    
    for prompt_name, prompt_text in PROMPTS.items():
        result = test_video_with_prompt(prompt_name, prompt_text, VIDEO_SOURCE, FRAMES_TO_TEST)
        if result:
            results.append(result)
        time.sleep(1)
    
    # Display results
    print("\n" + "="*70)
    print("RESULTS SUMMARY")
    print("="*70)
    
    if not results:
        print("❌ No valid results")
        return
    
    results.sort(key=lambda x: x["length"])
    
    print(f"\n{'Prompt':<15} {'Length':<12} {'Avg Time':<12} {'Min':<10} {'Max':<10}")
    print("-" * 70)
    
    baseline = results[0]["avg"] if results else None
    
    for r in results:
        diff = ""
        if baseline:
            pct = ((r["avg"] - baseline) / baseline) * 100
            diff = f" ({pct:+.1f}%)" if abs(pct) > 1 else ""
        
        print(f"{r['name']:<15} {r['length']:<12,} {r['avg']:.2f}s{diff:<12} {r['min']:.2f}s {r['max']:.2f}s")
    
    # Analysis
    if len(results) > 1:
        shortest = results[0]
        longest = results[-1]
        
        print(f"\n{'='*70}")
        print("ANALYSIS")
        print(f"{'='*70}")
        print(f"\n📊 Prompt length: {shortest['length']:,} → {longest['length']:,} chars ({longest['length']/shortest['length']:.1f}x)")
        print(f"⏱️  Processing time: {shortest['avg']:.2f}s → {longest['avg']:.2f}s")
        
        time_diff_pct = ((longest['avg'] - shortest['avg']) / shortest['avg']) * 100
        
        if abs(time_diff_pct) < 5:
            print(f"\n✅ CONCLUSION: Prompt length has MINIMAL impact ({abs(time_diff_pct):.1f}% difference)")
            print(f"   Even with {longest['length']/shortest['length']:.1f}x longer prompt, speed is nearly identical")
        else:
            print(f"\n⚠️  CONCLUSION: Prompt length has {abs(time_diff_pct):.1f}% impact")
            print(f"   This may be due to model processing overhead, not transmission")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    main()

