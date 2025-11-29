"""
Centralized Configuration for Safety Monitoring System
All prompts and configuration are defined here for consistency across all modules.
"""

# --- Safety Prompt for Manufacturing Factory ---
# Model only reports what it sees, violation determined in code based on missing mandatory items
SAFETY_PROMPT = """Analyze visible persons in this manufacturing factory image. Check ONLY what you can clearly see:
1. Hard hat/helmet on head (mandatory)
2. Safety glasses (if near machinery/hazards)
3. Safety gloves (if near machinery/hazards)

Rules: Only report missing items that are clearly visible. If uncertain or not visible, do not include in missing_ppe list.
Output JSON only: {"reason": "brief description of what you see", "missing_ppe": ["list only clearly missing items"]}
Example: {"reason": "Worker wearing hard hat and vest, boots not visible", "missing_ppe": ["safety boots"]}"""

# --- Configuration Constants ---
# Video processing settings
DEFAULT_VIDEO_SOURCE = "Good.mp4"
AI_CHECK_INTERVAL = 1  # Check every N seconds
FRAME_SKIP_RATE = 2  # Skip frames between AI checks (read every Nth frame)
RESIZE_WIDTH = 512   # Smaller resolution for faster processing
RESIZE_HEIGHT = 384  # Smaller resolution for faster processing

# AI engine settings
JPEG_QUALITY = 75  # Lower quality for faster encoding/transmission
MAX_IMAGE_SIZE = (512, 384)  # Maximum image dimensions for processing

