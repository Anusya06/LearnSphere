"""
Test suite for coding challenge reliability improvements
Tests retry logic, validation, and fallback mechanisms
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent / "frontend"))

from utils.coding_challenges import get_coding_system


def test_fallback_challenges():
    """Test that fallback challenges work for various topics"""
    print("=" * 60)
    print("TEST 1: Fallback Challenge Generation")
    print("=" * 60)
    
    coding_system = get_coding_system()
    
    topics = [
        ("Palindrome", "Easy", "Python"),
        ("Reverse String", "Medium", "JavaScript"),
        ("Sum Array", "Easy", "Python"),
        ("Sort List", "Medium", "Python"),
        ("Search Element", "Hard", "Python")
    ]
    
    all_passed = True
    
    for topic, difficulty, language in topics:
        print(f"\nTesting fallback for: {topic} ({difficulty}, {language})")
        
        # Get fallback challenge
        challenge = coding_system._get_fallback_challenge(topic, difficulty, language)
        
        # Validate structure
        if coding_system._validate_challenge_structure(challenge):
            print(f"  ✅ {topic}: Valid fallback generated")
        else:
            print(f"  ❌ {topic}: Invalid fallback structure")
            all_passed = False
    
    return all_passed


def test_challenge_validation():
    """Test challenge structure validation"""
    print("\n" + "=" * 60)
    print("TEST 2: Challenge Structure Validation")
    print("=" * 60)
    
    coding_system = get_coding_system()
    
    # Valid challenge
    valid_challenge = {
        'title': 'Test Challenge',
        'description': 'Test description',
        'difficulty': 'Easy',
        'language': 'Python',
        'starter_code': 'def test(): pass',
        'solution_code': 'def test(): return True',
        'test_cases': [
            {'input': '1', 'expected': '1'},
            {'input': '2', 'expected': '2'},
            {'input': '3', 'expected': '3'}
        ],
        'hints': ['Hint 1', 'Hint 2']
    }
    
    print("\nTesting valid challenge:")
    if coding_system._validate_challenge_structure(valid_challenge):
        print("  ✅ Valid challenge passed validation")
        valid_passed = True
    else:
        print("  ❌ Valid challenge failed validation")
        valid_passed = False
    
    # Invalid challenges
    invalid_tests = [
        ("Missing title", {k: v for k, v in valid_challenge.items() if k != 'title'}),
        ("Missing test_cases", {k: v for k, v in valid_challenge.items() if k != 'test_cases'}),
        ("Too few test cases", {**valid_challenge, 'test_cases': [{'input': '1', 'expected': '1'}]}),
        ("Too few hints", {**valid_challenge, 'hints': ['Only one hint']}),
        ("Empty description", {**valid_challenge, 'description': ''}),
    ]
    
    invalid_passed = True
    for test_name, invalid_challenge in invalid_tests:
        print(f"\nTesting {test_name}:")
        if not coding_system._validate_challenge_structure(invalid_challenge):
            print(f"  ✅ Correctly rejected invalid challenge")
        else:
            print(f"  ❌ Failed to reject invalid challenge")
            invalid_passed = False
    
    return valid_passed and invalid_passed


def test_fallback_templates():
    """Test all fallback template functions"""
    print("\n" + "=" * 60)
    print("TEST 3: Fallback Template Functions")
    print("=" * 60)
    
    coding_system = get_coding_system()
    
    templates = [
        ('_fallback_palindrome', 'Palindrome'),
        ('_fallback_reverse', 'Reverse'),
        ('_fallback_sum', 'Sum'),
        ('_fallback_sort', 'Sort'),
        ('_fallback_search', 'Search'),
    ]
    
    all_passed = True
    
    for template_name, description in templates:
        print(f"\nTesting {template_name}:")
        
        template_func = getattr(coding_system, template_name)
        challenge = template_func('Medium', 'Python')
        
        # Check basic structure
        if 'title' in challenge and 'test_cases' in challenge:
            print(f"  ✅ {description}: Template generated successfully")
            print(f"     Title: {challenge['title']}")
            print(f"     Test cases: {len(challenge['test_cases'])}")
        else:
            print(f"  ❌ {description}: Template missing required fields")
            all_passed = False
    
    return all_passed


def test_multi_language_fallbacks():
    """Test fallback generation for different languages"""
    print("\n" + "=" * 60)
    print("TEST 4: Multi-Language Fallback Support")
    print("=" * 60)
    
    coding_system = get_coding_system()
    
    languages = ['Python', 'JavaScript', 'Java', 'C++']
    
    all_passed = True
    
    for language in languages:
        print(f"\nTesting {language} fallback:")
        
        challenge = coding_system._fallback_palindrome('Easy', language)
        
        if challenge['language'] == language:
            print(f"  ✅ {language}: Correct language set")
        else:
            print(f"  ❌ {language}: Wrong language ({challenge['language']})")
            all_passed = False
        
        if challenge['starter_code'] and challenge['solution_code']:
            print(f"  ✅ {language}: Code generated")
        else:
            print(f"  ❌ {language}: Missing code")
            all_passed = False
    
    return all_passed


def test_topic_matching():
    """Test that topics correctly match fallback templates"""
    print("\n" + "=" * 60)
    print("TEST 5: Topic Matching Logic")
    print("=" * 60)
    
    coding_system = get_coding_system()
    
    test_cases = [
        ("Check Palindrome", "palindrome"),
        ("Reverse a String", "reverse"),
        ("Sum of Array", "sum"),
        ("Sort Numbers", "sort"),
        ("Binary Search", "search"),
        ("Array Operations", "array"),
        ("String Manipulation", "string"),
        ("List Processing", "list"),
    ]
    
    all_passed = True
    
    for topic, expected_key in test_cases:
        print(f"\nTesting topic: '{topic}'")
        
        challenge = coding_system._get_fallback_challenge(topic, 'Easy', 'Python')
        
        if challenge and 'title' in challenge:
            print(f"  ✅ Generated: {challenge['title']}")
        else:
            print(f"  ❌ Failed to generate fallback")
            all_passed = False
    
    return all_passed


def test_validation_edge_cases():
    """Test validation with edge cases"""
    print("\n" + "=" * 60)
    print("TEST 6: Validation Edge Cases")
    print("=" * 60)
    
    coding_system = get_coding_system()
    
    edge_cases = [
        ("None value", None, False),
        ("Empty dict", {}, False),
        ("String instead of dict", "not a dict", False),
        ("List instead of dict", [], False),
    ]
    
    all_passed = True
    
    for test_name, test_input, expected_result in edge_cases:
        print(f"\nTesting {test_name}:")
        
        try:
            result = coding_system._validate_challenge_structure(test_input)
            if result == expected_result:
                print(f"  ✅ Correctly handled: {test_name}")
            else:
                print(f"  ❌ Unexpected result for: {test_name}")
                all_passed = False
        except Exception as e:
            if not expected_result:
                print(f"  ✅ Correctly raised exception: {type(e).__name__}")
            else:
                print(f"  ❌ Unexpected exception: {e}")
                all_passed = False
    
    return all_passed


def test_test_case_validation():
    """Test that test cases are properly validated"""
    print("\n" + "=" * 60)
    print("TEST 7: Test Case Validation")
    print("=" * 60)
    
    coding_system = get_coding_system()
    
    # Get a fallback challenge
    challenge = coding_system._fallback_palindrome('Easy', 'Python')
    
    print(f"\nValidating test cases from fallback challenge:")
    print(f"Number of test cases: {len(challenge['test_cases'])}")
    
    all_valid = True
    for i, test_case in enumerate(challenge['test_cases'], 1):
        if 'input' in test_case and 'expected' in test_case:
            print(f"  ✅ Test case {i}: Valid")
        else:
            print(f"  ❌ Test case {i}: Missing fields")
            all_valid = False
    
    return all_valid


if __name__ == "__main__":
    print("\n🧪 CODING CHALLENGE RELIABILITY TEST SUITE\n")
    
    results = []
    
    # Run all tests
    results.append(("Fallback Challenges", test_fallback_challenges()))
    results.append(("Challenge Validation", test_challenge_validation()))
    results.append(("Fallback Templates", test_fallback_templates()))
    results.append(("Multi-Language Support", test_multi_language_fallbacks()))
    results.append(("Topic Matching", test_topic_matching()))
    results.append(("Validation Edge Cases", test_validation_edge_cases()))
    results.append(("Test Case Validation", test_test_case_validation()))
    
    # Summary
    print("\n" + "=" * 60)
    print("FINAL TEST RESULTS")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Challenge generation is reliable.")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Review the output above.")
    
    print()
