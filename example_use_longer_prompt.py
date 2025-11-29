"""
Quick Example: How to use longer prompts in your application

This shows the exact steps to switch from simple to comprehensive prompts.
"""

# ============================================================================
# STEP 1: Import the prompt templates (uncomment in app.py)
# ============================================================================
from prompt_templates import STANDARD_PROMPT, COMPREHENSIVE_PROMPT, build_custom_prompt

# ============================================================================
# STEP 2: Choose your prompt style
# ============================================================================

# Option A: Use Standard Prompt (recommended for most cases)
SAFETY_PROMPT = STANDARD_PROMPT

# Option B: Use Comprehensive Prompt (for detailed safety checks)
# SAFETY_PROMPT = COMPREHENSIVE_PROMPT

# Option C: Build Custom Prompt (for specific requirements)
# SAFETY_PROMPT = build_custom_prompt(
#     check_hard_hat=True,
#     check_vest=True,
#     check_boots=True,
#     check_glasses=True,
#     environment="warehouse"
# )

# Option D: Write Your Own (for complete control)
# SAFETY_PROMPT = """
# Your custom detailed prompt here...
# Can be as long as you need!
# """

# ============================================================================
# STEP 3: Use it in your code (same as before)
# ============================================================================
from ai_engine import analyze_image_local
import cv2

# Test with an image
test_image = cv2.imread("testo.png")
if test_image is not None:
    result = analyze_image_local(
        test_image, 
        SAFETY_PROMPT,
        jpeg_quality=75,
        max_size=(512, 384)
    )
    print("Result:", result)
else:
    print("No test image found")

# ============================================================================
# COMPARISON: See the difference
# ============================================================================
print("\n" + "="*60)
print("PROMPT LENGTH COMPARISON")
print("="*60)

prompts = {
    "Simple (current)": "Are they wearing a hard hat? JSON: {\"violation\": boolean}",
    "Standard": STANDARD_PROMPT,
    "Comprehensive": COMPREHENSIVE_PROMPT[:200] + "..."  # First 200 chars
}

for name, prompt in prompts.items():
    length = len(prompt)
    print(f"{name:20} - {length:4} characters")

print("\n💡 All prompts process at the same speed!")
print("   The bottleneck is image processing, not text length.")

