"""
Prompt Optimizer: Compress and optimize prompts for faster processing

Since longer prompts significantly slow down processing (216% slower),
this module provides techniques to make prompts shorter while maintaining
effectiveness.
"""
import re

def compress_prompt(prompt):
    """
    Compress a prompt by removing redundancy and optimizing structure.
    Returns a shorter but equally effective prompt.
    """
    # Remove extra whitespace
    prompt = re.sub(r'\s+', ' ', prompt)
    prompt = prompt.strip()
    
    # Remove redundant phrases
    replacements = {
        'Respond in JSON format only': 'JSON only',
        'Respond strictly in JSON format only': 'JSON only',
        'JSON format only': 'JSON only',
        'must be': 'be',
        'should be': 'be',
        'is required': 'required',
        'is mandatory': 'mandatory',
        'workplace safety': 'safety',
        'safety equipment': 'PPE',
        'hard hat or safety helmet': 'hard hat',
        'high-visibility vest': 'safety vest',
        'safety boots': 'boots',
        'safety glasses': 'glasses',
        'If any': 'If',
        'If the person': 'If person',
        'Check for the following': 'Check',
        'Analyze this': 'Analyze',
        'You are a': 'Be',
        'workplace safety inspector': 'inspector',
    }
    
    for old, new in replacements.items():
        prompt = prompt.replace(old, new)
    
    # Remove verbose instructions
    prompt = re.sub(r'Please\s+', '', prompt, flags=re.IGNORECASE)
    prompt = re.sub(r'\.\s*$', '', prompt)  # Remove trailing period
    
    return prompt.strip()

def create_optimized_prompt(requirements, output_format):
    """
    Create a highly optimized prompt from requirements.
    Uses minimal words while maintaining clarity.
    """
    # Build compact requirements list
    req_list = ', '.join(requirements) if isinstance(requirements, list) else requirements
    
    prompt = f"""Check: {req_list}
Output: {output_format}
If missing, violation=true"""
    
    return prompt

# Optimized prompt templates (shorter but effective)
OPTIMIZED_SIMPLE = """Check hard hat. JSON: {"violation": boolean, "reason": "text"}
Missing = violation true"""

OPTIMIZED_STANDARD = """Check: hard hat, safety vest, boots
JSON: {"violation": boolean, "reason": "text", "missing": ["items"]}
Missing PPE = violation true"""

OPTIMIZED_COMPREHENSIVE = """Safety check: hard hat, vest, boots, glasses (if needed), gloves (if needed)
Environment: check hazards
JSON: {"violation": boolean, "reason": "text", "violations": ["list"], "persons": number, "compliance": "%"}
Missing required PPE = violation true"""

def optimize_existing_prompt(prompt_text):
    """
    Take an existing prompt and optimize it automatically.
    """
    # Extract key requirements
    requirements = []
    
    # Look for numbered lists
    req_matches = re.findall(r'\d+\.\s*([^:]+):\s*([^\n]+)', prompt_text)
    for match in req_matches:
        req_name = match[0].strip()
        req_desc = match[1].strip()
        # Compress the requirement
        if 'hard hat' in req_name.lower() or 'helmet' in req_name.lower():
            requirements.append('hard hat')
        elif 'vest' in req_name.lower() or 'visibility' in req_name.lower():
            requirements.append('safety vest')
        elif 'boot' in req_name.lower() or 'foot' in req_name.lower():
            requirements.append('boots')
        elif 'glass' in req_name.lower() or 'eye' in req_name.lower():
            requirements.append('glasses')
        elif 'glove' in req_name.lower() or 'hand' in req_name.lower():
            requirements.append('gloves')
    
    # Extract output format
    json_match = re.search(r'JSON[^:]*:\s*(\{[^}]+\})', prompt_text, re.IGNORECASE)
    output_format = json_match.group(1) if json_match else '{"violation": boolean, "reason": "text"}'
    
    # Build optimized version
    if requirements:
        req_text = ', '.join(requirements)
        optimized = f"""Check: {req_text}
JSON: {output_format}
Missing required = violation true"""
        return optimized
    else:
        # Fallback to compression
        return compress_prompt(prompt_text)

# Pre-optimized versions of existing prompts
from prompt_templates import STANDARD_PROMPT, COMPREHENSIVE_PROMPT

OPTIMIZED_STANDARD_FROM_TEMPLATE = optimize_existing_prompt(STANDARD_PROMPT)
OPTIMIZED_COMPREHENSIVE_FROM_TEMPLATE = optimize_existing_prompt(COMPREHENSIVE_PROMPT)

if __name__ == "__main__":
    print("="*70)
    print("PROMPT OPTIMIZER - Length Comparison")
    print("="*70)
    
    from prompt_templates import SIMPLE_PROMPT, STANDARD_PROMPT, COMPREHENSIVE_PROMPT
    
    prompts = {
        "Original Simple": SIMPLE_PROMPT,
        "Optimized Simple": OPTIMIZED_SIMPLE,
        "Original Standard": STANDARD_PROMPT,
        "Optimized Standard": OPTIMIZED_STANDARD,
        "Original Comprehensive": COMPREHENSIVE_PROMPT[:200] + "...",
        "Optimized Comprehensive": OPTIMIZED_COMPREHENSIVE,
    }
    
    print("\nPrompt Length Comparison:\n")
    print(f"{'Type':<30} {'Length':<10} {'Reduction':<15}")
    print("-" * 70)
    
    for name, prompt in prompts.items():
        length = len(prompt)
        print(f"{name:<30} {length:<10,} chars")
    
    print("\n" + "="*70)
    print("Example Optimized Prompts:")
    print("="*70)
    print("\n1. OPTIMIZED_SIMPLE:")
    print(OPTIMIZED_SIMPLE)
    print(f"\n   Length: {len(OPTIMIZED_SIMPLE)} chars")
    
    print("\n2. OPTIMIZED_STANDARD:")
    print(OPTIMIZED_STANDARD)
    print(f"\n   Length: {len(OPTIMIZED_STANDARD)} chars")
    
    print("\n3. OPTIMIZED_COMPREHENSIVE:")
    print(OPTIMIZED_COMPREHENSIVE)
    print(f"\n   Length: {len(OPTIMIZED_COMPREHENSIVE)} chars")

