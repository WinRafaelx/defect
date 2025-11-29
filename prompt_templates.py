"""
Prompt Template System for Real-World Safety Monitoring

Key Insight: Prompt length has MINIMAL impact on speed!
- The bottleneck is IMAGE processing (encoding, transmission, model inference)
- Text prompts are tiny compared to image data
- You can use detailed prompts without significant performance loss

Speed is maintained through:
1. Image optimization (resolution, quality) - already done
2. Frame skipping - already done  
3. Async processing - already done
4. Connection pooling - already done
"""

# ============================================================================
# PROMPT TEMPLATES - Choose or customize based on your needs
# ============================================================================

# Simple prompt (current - fastest, least detailed)
SIMPLE_PROMPT = """Are they wearing a hard hat? 
JSON format only: {"violation": boolean, "reason": "short text"}
If no hard hat, violation is true."""

# OPTIMIZED VERSIONS (shorter, faster processing)
# These maintain effectiveness while reducing processing time significantly
OPTIMIZED_SIMPLE = """Check hard hat. JSON: {"violation": boolean, "reason": "text"}
Missing = violation true"""

OPTIMIZED_STANDARD = """Check: hard hat, safety vest, boots
JSON: {"violation": boolean, "reason": "text", "missing": ["items"]}
Missing PPE = violation true"""

OPTIMIZED_COMPREHENSIVE = """Safety: hard hat, vest, boots, glasses (if needed), gloves (if needed)
Env: check hazards
JSON: {"violation": boolean, "reason": "text", "violations": ["list"], "persons": number, "compliance": "%"}
Missing required = violation true"""

# Standard prompt (balanced - recommended for most use cases)
STANDARD_PROMPT = """Analyze this workplace safety image. Check for the following violations:

1. Hard Hat/Helmet: Is the person wearing proper head protection?
2. Safety Vest: Is a high-visibility vest visible?
3. Footwear: Are safety boots being worn?

For each violation found, provide details.
Respond in JSON format only: {"violation": boolean, "reason": "short text", "violations": ["list of violations"]}
If any safety equipment is missing, violation must be true."""

# Comprehensive prompt (detailed - for complex safety requirements)
COMPREHENSIVE_PROMPT = """You are a workplace safety inspector analyzing a construction/warehouse site image.

SAFETY REQUIREMENTS TO CHECK:
1. HEAD PROTECTION: Hard hat or safety helmet must be worn and properly secured
2. EYE PROTECTION: Safety glasses or goggles if in hazardous area
3. HIGH-VISIBILITY CLOTHING: Reflective vest or clothing must be visible
4. FOOT PROTECTION: Safety boots with steel toe protection
5. HAND PROTECTION: Gloves if handling hazardous materials
6. PROPER ATTIRE: No loose clothing that could get caught in machinery
7. ENVIRONMENT: Check for immediate hazards in the visible area

ANALYSIS INSTRUCTIONS:
- Examine the entire image carefully
- Identify all visible persons
- Check each person against the safety requirements
- Note any equipment that appears damaged or improperly used
- Consider the work environment context

OUTPUT FORMAT (JSON only):
{
  "violation": boolean,
  "reason": "brief description of violation or 'All safety requirements met'",
  "violations": ["list of specific violations found"],
  "persons_detected": number,
  "compliance_rate": "percentage of persons meeting requirements"
}

If ANY person lacks required safety equipment, violation must be true."""

# Multi-language prompt (for international sites)
MULTILINGUAL_PROMPT = """Analyze workplace safety. Check: hard hat, safety vest, safety boots.
Analysez la sécurité au travail. Vérifiez: casque, gilet de sécurité, bottes de sécurité.
Analizar seguridad laboral. Verificar: casco, chaleco de seguridad, botas de seguridad.

JSON only: {"violation": boolean, "reason": "text"}
If safety equipment missing, violation=true."""

# Industry-specific prompts
CONSTRUCTION_PROMPT = """Construction site safety check:
- Hard hat (mandatory)
- High-visibility vest
- Safety boots
- Safety glasses (if near machinery)
- No loose clothing

JSON: {"violation": boolean, "reason": "text", "missing_equipment": ["list"]}"""

WAREHOUSE_PROMPT = """Warehouse safety inspection:
- Hard hat in designated areas
- Safety vest for visibility
- Safety boots
- Proper lifting posture (if visible)
- Clear walkways

JSON: {"violation": boolean, "reason": "text", "issues": ["list"]}"""

# ============================================================================
# PROMPT BUILDER - For dynamic prompt generation
# ============================================================================

def build_custom_prompt(
    check_hard_hat=True,
    check_vest=True,
    check_boots=True,
    check_glasses=False,
    check_gloves=False,
    environment="general",
    language="en"
):
    """
    Build a custom prompt based on requirements.
    This allows you to adjust prompts without code changes.
    """
    checks = []
    if check_hard_hat:
        checks.append("hard hat/helmet")
    if check_vest:
        checks.append("high-visibility vest")
    if check_boots:
        checks.append("safety boots")
    if check_glasses:
        checks.append("safety glasses")
    if check_gloves:
        checks.append("safety gloves")
    
    checks_text = ", ".join(checks)
    
    prompt = f"""Analyze this {environment} workplace image for safety compliance.

REQUIRED EQUIPMENT: {checks_text}

Check each visible person for the required safety equipment.
Respond in JSON format only: {{"violation": boolean, "reason": "short text", "missing_items": ["list"]}}

If any required equipment is missing, violation must be true."""
    
    return prompt

# ============================================================================
# USAGE EXAMPLES
# ============================================================================

if __name__ == "__main__":
    # Example 1: Use a predefined template
    print("=== STANDARD PROMPT ===")
    print(STANDARD_PROMPT)
    print("\n" + "="*60 + "\n")
    
    # Example 2: Build custom prompt
    print("=== CUSTOM PROMPT ===")
    custom = build_custom_prompt(
        check_hard_hat=True,
        check_vest=True,
        check_boots=True,
        check_glasses=True,
        environment="construction"
    )
    print(custom)
    print("\n" + "="*60 + "\n")
    
    # Example 3: Show prompt length comparison
    prompts = {
        "Simple": SIMPLE_PROMPT,
        "Standard": STANDARD_PROMPT,
        "Comprehensive": COMPREHENSIVE_PROMPT
    }
    
    print("=== PROMPT LENGTH COMPARISON ===")
    for name, prompt in prompts.items():
        length = len(prompt)
        words = len(prompt.split())
        print(f"{name:15} - {length:4} chars, {words:3} words")
    
    print("\n💡 Note: Prompt length has minimal impact on speed!")
    print("   The bottleneck is image processing, not text length.")

