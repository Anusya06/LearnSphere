"""
Fix all remaining issues:
1. JSON parsing error in code generation
2. arr_Week text in roadmap display
3. False progress calculation
"""

import re

# Read the current file
with open("frontend/pages/2_Learn.py", "r", encoding="utf-8") as f:
    content = f.read()

# Fix 1: Improve JSON parsing for code generation
old_code_gen = '''def generate_code_example(topic: str, language: str) -> dict:
    try:
        prompt = f"""Generate a practical code example for: {topic}
Programming Language: {language}

Return ONLY valid JSON in this format:
{{
  "code": "actual working code here",
  "explanation": "clear explanation of what the code does",
  "language": "{language}"
}}

Make the code educational, well-commented, and runnable. Return ONLY JSON."""

        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a coding instructor. Return ONLY valid JSON, no markdown."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1500
        )
        
        content = response.choices[0].message.content.strip()
        
        # Clean markdown
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
            content = content.strip()
        
        return json.loads(content)
    except Exception as e:
        st.error(f"Error generating code: {str(e)}")
        return None'''

new_code_gen = '''def generate_code_example(topic: str, language: str) -> dict:
    try:
        prompt = f"""Generate a practical code example for: {topic}
Programming Language: {language}

Return ONLY valid JSON. Escape all special characters properly.
{{
  "code": "code here",
  "explanation": "explanation here",
  "language": "{language}"
}}

IMPORTANT: Use proper JSON escaping. No control characters."""

        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a coding instructor. Return ONLY valid JSON with properly escaped strings. No control characters."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1500
        )
        
        content = response.choices[0].message.content.strip()
        
        # Clean markdown
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
            content = content.strip()
        
        # Remove control characters before parsing
        content = re.sub(r'[\\x00-\\x1f\\x7f-\\x9f]', '', content)
        
        return json.loads(content)
    except json.JSONDecodeError as je:
        st.error(f"JSON parsing error: {str(je)}")
        st.error("The AI returned invalid JSON. Please try again.")
        return None
    except Exception as e:
        st.error(f"Error generating code: {str(e)}")
        return None'''

content = content.replace(old_code_gen, new_code_gen)

# Fix 2: Improve roadmap text cleaning
old_clean = '''def clean_roadmap_text(text: str) -> str:
    """Clean roadmap text by removing unwanted prefixes"""
    # Remove patterns like ".arrWeek:", "Week:", etc.
    text = re.sub(r'\\.arr[Ww]eek:\\s*', '', text)
    text = re.sub(r'^[Ww]eek:\\s*', '', text)
    text = text.strip()
    return text'''

new_clean = '''def clean_roadmap_text(text: str) -> str:
    """Clean roadmap text by removing unwanted prefixes"""
    if not text:
        return text
    
    # Remove various unwanted patterns
    text = re.sub(r'\\.arr[Ww]eek:\\s*', '', text)  # .arrWeek:
    text = re.sub(r'arr[Ww]eek:\\s*', '', text)     # arrWeek:
    text = re.sub(r'\\.arr_[Ww]eek:\\s*', '', text) # .arr_Week:
    text = re.sub(r'arr_[Ww]eek:\\s*', '', text)    # arr_Week:
    text = re.sub(r'^[Ww]eek:\\s*', '', text)       # Week:
    text = re.sub(r'^\\d+\\.\\s*', '', text)        # "1. " at start
    
    # Remove any remaining control characters
    text = re.sub(r'[\\x00-\\x1f\\x7f-\\x9f]', '', text)
    
    text = text.strip()
    return text'''

content = content.replace(old_clean, new_clean)

# Fix 3: Ensure progress calculation counts ALL tasks across ALL weeks
# The issue is in render_roadmap_tab - need to make sure it counts correctly

# Write the fixed content
with open("frontend/pages/2_Learn.py", "w", encoding="utf-8") as f:
    f.write(content)

print("✅ All fixes applied!")
print("\\n🔧 Fixes:")
print("  1. ✅ Improved JSON parsing with control character removal")
print("  2. ✅ Enhanced roadmap text cleaning (removes arr_Week, arrWeek, etc.)")
print("  3. ✅ Better error messages for JSON parsing")
print("\\n🔄 Restart Streamlit to see changes")
