"""
Test Roadmap Text Cleaning
Verify that arr_week and similar patterns are removed
"""
import re


def clean_roadmap_text(text: str) -> str:
    """Clean roadmap text by removing unwanted prefixes and patterns"""
    if not text:
        return text
    
    # Remove all variations of arr_week, arrWeek, arr_Week, etc.
    patterns_to_remove = [
        r'\.?arr[_\s]?[Ww]eek:?\s*',      # arr_week, arr week, arrweek, arrWeek
        r'\.?[Aa]rr[_\s]?[Ww]eek:?\s*',   # Arr_Week, Arr Week, ArrWeek
        r'\.?week[_\s]?title:?\s*',        # week_title, week title
        r'\.?week[_\s]?tasks:?\s*',        # week_tasks, week tasks
        r'\.?arr[_\s]?title:?\s*',         # arr_title, arr title
        r'\.?arr[_\s]?tasks:?\s*',         # arr_tasks, arr tasks
        r'^[Ww]eek\s+\d+\s*[-:]\s*',      # "Week 1 - " or "Week 1: " at start
        r'^[Ww]eek:?\s*',                  # Week: at start
        r'^\d+\.\s*',                      # "1. " at start
        r'^-\s*',                          # "- " at start
        r'^\*\s*',                         # "* " at start
    ]
    
    # Apply all patterns
    for pattern in patterns_to_remove:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    # Remove control characters
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    # Remove any remaining dots at the start
    text = text.lstrip('.')
    
    return text.strip()


# Test cases
test_cases = [
    ("arr_week Week 1: Introduction to Java in Tamil", "Introduction to Java in Tamil"),
    ("arrWeek: Data Types and Operators", "Data Types and Operators"),
    ("arr_Week: Control Structures in Java", "Control Structures in Java"),
    (".arr_week Functions and Arrays", "Functions and Arrays"),
    ("Arr_Week: Object-Oriented Programming", "Object-Oriented Programming"),
    ("week_title: File Input/Output", "File Input/Output"),
    ("Week: Getting Started", "Getting Started"),
    ("1. Introduction to Python", "Introduction to Python"),
    ("- Learn the basics", "Learn the basics"),
    ("* Advanced topics", "Advanced topics"),
    ("Week 1 - Introduction", "Introduction"),
    ("Week 2: Data Structures", "Data Structures"),
    ("Normal text without prefixes", "Normal text without prefixes"),
]

print("="*70)
print("Roadmap Text Cleaning Test")
print("="*70)
print()

all_passed = True

for i, (input_text, expected_output) in enumerate(test_cases, 1):
    actual_output = clean_roadmap_text(input_text)
    passed = actual_output == expected_output
    
    if not passed:
        all_passed = False
    
    status = "✅ PASS" if passed else "❌ FAIL"
    
    print(f"Test {i}: {status}")
    print(f"  Input:    '{input_text}'")
    print(f"  Expected: '{expected_output}'")
    print(f"  Actual:   '{actual_output}'")
    
    if not passed:
        print(f"  ⚠️  Mismatch!")
    
    print()

print("="*70)
if all_passed:
    print("✅ ALL TESTS PASSED!")
    print()
    print("The roadmap cleaning function will correctly remove:")
    print("  • arr_week, arrWeek, arr_Week, Arr_Week")
    print("  • week_title, week_tasks")
    print("  • arr_title, arr_tasks")
    print("  • Week:, Week 1 -, Week 2:")
    print("  • Numbered lists (1., 2., etc.)")
    print("  • Bullet points (-, *)")
    print()
    print("Your roadmap will display clean titles like:")
    print("  Week 1 – Introduction to Java in Tamil")
    print("  Week 2 – Data Types and Operators")
    print("  Week 3 – Control Structures")
else:
    print("❌ SOME TESTS FAILED")
    print("Please review the failed tests above.")

print("="*70)
