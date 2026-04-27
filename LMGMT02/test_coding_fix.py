"""
Test script to verify the coding challenge test case fix
Tests the _safe_parse_input method and validate_code function
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent / "frontend"))

from utils.coding_challenges import get_coding_system


def test_safe_parse_input():
    """Test the safe input parser"""
    print("=" * 60)
    print("Testing _safe_parse_input method")
    print("=" * 60)
    
    coding_system = get_coding_system()
    
    test_cases = [
        # String inputs (the problematic case)
        ('madam', 'madam'),
        ('"madam"', 'madam'),
        ("'hello'", 'hello'),
        
        # Number inputs
        ('123', 123),
        ('45.67', 45.67),
        
        # Boolean inputs
        ('True', True),
        ('False', False),
        ('true', 'true'),  # String 'true'
        
        # List inputs
        ('[1, 2, 3]', [1, 2, 3]),
        ('["a", "b"]', ['a', 'b']),
        
        # Tuple inputs
        ('(1, 2)', (1, 2)),
        ('("x", "y")', ('x', 'y')),
    ]
    
    passed = 0
    failed = 0
    
    for input_str, expected in test_cases:
        try:
            result = coding_system._safe_parse_input(input_str)
            if result == expected:
                print(f"✅ PASS: '{input_str}' -> {repr(result)}")
                passed += 1
            else:
                print(f"❌ FAIL: '{input_str}' -> Expected {repr(expected)}, Got {repr(result)}")
                failed += 1
        except Exception as e:
            print(f"❌ ERROR: '{input_str}' -> {str(e)}")
            failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    print()


def test_palindrome_validation():
    """Test the actual palindrome validation scenario"""
    print("=" * 60)
    print("Testing Palindrome Challenge (The Original Problem)")
    print("=" * 60)
    
    # The solution code
    solution_code = """def is_palindrome(s: str) -> bool:
    return s == s[::-1]
"""
    
    # Test cases in the format AI generates
    test_cases = [
        {"input": "madam", "expected": "True"},
        {"input": "hello", "expected": "False"},
        {"input": "a", "expected": "True"},
        {"input": "abba", "expected": "True"},
        {"input": "python", "expected": "False"}
    ]
    
    print("\nTest Cases:")
    for i, test in enumerate(test_cases, 1):
        print(f"  Test {i}: input={test['input']}, expected={test['expected']}")
    
    print("\nRunning validation...")
    
    coding_system = get_coding_system()
    results = coding_system.validate_code(solution_code, test_cases, "Python")
    
    print(f"\n{results['message']}")
    print(f"Passed: {results.get('passed_tests', 0)}/{results.get('total_tests', 0)}")
    print()
    
    for test_result in results.get('results', []):
        if test_result.get('passed'):
            print(f"✅ Test {test_result['test']} Passed")
            print(f"   Input: {test_result['input']}")
            print(f"   Expected: {test_result['expected']}")
            print(f"   Got: {test_result['got']}")
        else:
            print(f"❌ Test {test_result['test']} Failed")
            print(f"   Input: {test_result.get('input', 'N/A')}")
            if 'error' in test_result:
                print(f"   Error: {test_result['error']}")
            else:
                print(f"   Expected: {test_result.get('expected', 'N/A')}")
                print(f"   Got: {test_result.get('got', 'N/A')}")
        print()
    
    return results['passed']


def test_number_challenge():
    """Test with number inputs"""
    print("=" * 60)
    print("Testing Number Challenge (Double Function)")
    print("=" * 60)
    
    solution_code = """def double_number(n: int) -> int:
    return n * 2
"""
    
    test_cases = [
        {"input": "5", "expected": "10"},
        {"input": "0", "expected": "0"},
        {"input": "-3", "expected": "-6"},
        {"input": "100", "expected": "200"}
    ]
    
    print("\nTest Cases:")
    for i, test in enumerate(test_cases, 1):
        print(f"  Test {i}: input={test['input']}, expected={test['expected']}")
    
    print("\nRunning validation...")
    
    coding_system = get_coding_system()
    results = coding_system.validate_code(solution_code, test_cases, "Python")
    
    print(f"\n{results['message']}")
    print(f"Passed: {results.get('passed_tests', 0)}/{results.get('total_tests', 0)}")
    print()
    
    for test_result in results.get('results', []):
        if test_result.get('passed'):
            print(f"✅ Test {test_result['test']} Passed")
        else:
            print(f"❌ Test {test_result['test']} Failed")
            if 'error' in test_result:
                print(f"   Error: {test_result['error']}")
        print()
    
    return results['passed']


def test_list_challenge():
    """Test with list inputs"""
    print("=" * 60)
    print("Testing List Challenge (Reverse List)")
    print("=" * 60)
    
    solution_code = """def reverse_list(lst: list) -> list:
    return lst[::-1]
"""
    
    test_cases = [
        {"input": "[1, 2, 3]", "expected": "[3, 2, 1]"},
        {"input": "[5]", "expected": "[5]"},
        {"input": "[]", "expected": "[]"},
        {"input": '["a", "b", "c"]', "expected": '["c", "b", "a"]'}
    ]
    
    print("\nTest Cases:")
    for i, test in enumerate(test_cases, 1):
        print(f"  Test {i}: input={test['input']}, expected={test['expected']}")
    
    print("\nRunning validation...")
    
    coding_system = get_coding_system()
    results = coding_system.validate_code(solution_code, test_cases, "Python")
    
    print(f"\n{results['message']}")
    print(f"Passed: {results.get('passed_tests', 0)}/{results.get('total_tests', 0)}")
    print()
    
    for test_result in results.get('results', []):
        if test_result.get('passed'):
            print(f"✅ Test {test_result['test']} Passed")
        else:
            print(f"❌ Test {test_result['test']} Failed")
            if 'error' in test_result:
                print(f"   Error: {test_result['error']}")
        print()
    
    return results['passed']


if __name__ == "__main__":
    print("\n🧪 CODING CHALLENGE FIX - TEST SUITE\n")
    
    # Test 1: Input parser
    test_safe_parse_input()
    
    # Test 2: Palindrome (the original problem)
    palindrome_passed = test_palindrome_validation()
    
    # Test 3: Number inputs
    number_passed = test_number_challenge()
    
    # Test 4: List inputs
    list_passed = test_list_challenge()
    
    # Summary
    print("=" * 60)
    print("FINAL RESULTS")
    print("=" * 60)
    print(f"Palindrome Challenge: {'✅ PASSED' if palindrome_passed else '❌ FAILED'}")
    print(f"Number Challenge: {'✅ PASSED' if number_passed else '❌ FAILED'}")
    print(f"List Challenge: {'✅ PASSED' if list_passed else '❌ FAILED'}")
    print()
    
    if palindrome_passed and number_passed and list_passed:
        print("🎉 ALL TESTS PASSED! The fix is working correctly.")
    else:
        print("⚠️ Some tests failed. Review the output above.")
    print()
