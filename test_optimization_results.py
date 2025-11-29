"""
Test to show the speed improvement from prompt optimization
"""
import cv2
import time
from ai_engine import analyze_image_local
from prompt_templates import STANDARD_PROMPT, COMPREHENSIVE_PROMPT
from prompt_templates import OPTIMIZED_STANDARD, OPTIMIZED_COMPREHENSIVE
from prompt_optimizer import optimize_existing_prompt

TEST_IMAGE = "testo.png"
NUM_RUNS = 3

def test_prompt(prompt_name, prompt_text, image, num_runs=3):
    """Test a prompt and return average time"""
    times = []
    print(f"\nTesting: {prompt_name} ({len(prompt_text):,} chars)")
    
    for i in range(num_runs):
        print(f"  Run {i+1}/{num_runs}...", end=" ", flush=True)
        start = time.time()
        try:
            result = analyze_image_local(image, prompt_text, jpeg_quality=75, max_size=(512, 384))
            elapsed = time.time() - start
            times.append(elapsed)
            print(f"✓ {elapsed:.2f}s")
        except Exception as e:
            print(f"✗ Error: {e}")
    
    if times:
        return {
            "name": prompt_name,
            "length": len(prompt_text),
            "avg": sum(times) / len(times),
            "min": min(times),
            "max": max(times)
        }
    return None

def main():
    print("="*70)
    print("PROMPT OPTIMIZATION SPEED TEST")
    print("="*70)
    
    image = cv2.imread(TEST_IMAGE)
    if image is None:
        print(f"❌ Could not load {TEST_IMAGE}")
        return
    
    print(f"✅ Image loaded: {image.shape[1]}x{image.shape[0]}")
    
    # Test pairs: original vs optimized
    test_pairs = [
        ("Original Standard", STANDARD_PROMPT, "Optimized Standard", OPTIMIZED_STANDARD),
        ("Original Comprehensive", COMPREHENSIVE_PROMPT, "Optimized Comprehensive", OPTIMIZED_COMPREHENSIVE),
    ]
    
    results = []
    
    for orig_name, orig_prompt, opt_name, opt_prompt in test_pairs:
        # Test original
        orig_result = test_prompt(orig_name, orig_prompt, image, NUM_RUNS)
        if orig_result:
            results.append(orig_result)
        
        time.sleep(0.5)
        
        # Test optimized
        opt_result = test_prompt(opt_name, opt_prompt, image, NUM_RUNS)
        if opt_result:
            results.append(opt_result)
        
        time.sleep(0.5)
    
    # Display results
    print("\n" + "="*70)
    print("RESULTS")
    print("="*70)
    
    print(f"\n{'Prompt':<30} {'Length':<12} {'Avg Time':<12} {'Speedup':<15}")
    print("-" * 70)
    
    # Group by pairs
    for i in range(0, len(results), 2):
        if i + 1 < len(results):
            orig = results[i]
            opt = results[i + 1]
            
            speedup = ((orig["avg"] - opt["avg"]) / orig["avg"]) * 100
            speedup_str = f"{speedup:+.1f}%" if abs(speedup) > 1 else "~0%"
            
            print(f"{orig['name']:<30} {orig['length']:<12,} {orig['avg']:.2f}s")
            print(f"{opt['name']:<30} {opt['length']:<12,} {opt['avg']:.2f}s {'(' + speedup_str + ')':<15}")
            print()
    
    # Summary
    print("="*70)
    print("SUMMARY")
    print("="*70)
    
    for i in range(0, len(results), 2):
        if i + 1 < len(results):
            orig = results[i]
            opt = results[i + 1]
            
            length_reduction = ((orig["length"] - opt["length"]) / orig["length"]) * 100
            time_reduction = ((orig["avg"] - opt["avg"]) / orig["avg"]) * 100
            
            print(f"\n{orig['name']} → {opt['name']}:")
            print(f"  Length: {orig['length']:,} → {opt['length']:,} chars ({length_reduction:.1f}% reduction)")
            print(f"  Speed:  {orig['avg']:.2f}s → {opt['avg']:.2f}s ({time_reduction:+.1f}% faster)")
            
            if time_reduction > 10:
                print(f"  ✅ Significant speedup achieved!")
            elif time_reduction > 5:
                print(f"  ✓ Moderate speedup achieved")
            else:
                print(f"  ⚠️  Minimal speedup (may vary by model)")

if __name__ == "__main__":
    main()

