"""
Comprehensive test suite for all coding challenge fixes
Tests: __init__ detection, multiple parameters, AST parsing, formatting
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent / "frontend"))

from utils.coding_challenges import get_coding_system


def test_init_detection_fix():
    """Test that __init__ is not detected as the main function"""
    print("=" * 60)
    print("TEST 1: __init__ Detection Fix")
    print("=" * 60)
    
    # Code with class and __init__ method
    code_with_class = """
class ListNode:
    def __init__(self, x):
        self.val = x
        self.next = None

def add_two_numbers(l1, l2):
    dummy = ListNode(0)
    current = dummy
    carry = 0
    
    while l1 or l2 or carry:
        val1 = l1.val if l1 else 0
        val2 = l2.val if l2 else 0
        
        total = val1 + val2 + carry
        carry = total // 10
        current.next = ListNode(total % 10)
        current = current.next
        
        if l1:
            l1 = l1.next
        if l2:
            l2 = l2.next
    
    return dummy.next
"""
    
    coding_system = get_coding_system()
    
    # Extract top-level functions
    functions = coding_system._extract_top_level_functions(code_with_class)
    
    print(f"\nExtracted functions: {functions}")
    print(f"Expected: ['add_two_numbers']")
    
    if functions == ['add_two_numbers']:
        print("✅ PASS: Correctly identified 'add_two_numbers' and ignored '__init__'")
        return True
    else:
        print(f"❌ FAIL: Got {functions}, expected ['add_two_numbers']")
        return False


def test_multiple_parameters():
    """Test functions with multiple parameters"""
    print("\n" + "=" * 60)
    print("TEST 2: Multiple Parameters Support")
    print("=" * 60)
    
    # Function with two parameters
    code = """
def subtract(a, b):
    return a - b
"""
    
    # Test cases with tuple inputs
    test_cases = [
        {"input": "(5, 3)", "expected": "2"},
        {"input": "(10, 4)", "expected": "6"},
        {"input": "(100, 50)", "expected": "50"},
        {"input": "(0, 0)", "expected": "0"},
        {"input": "(-5, -3)", "expected": "-2"}
    ]
    
    print("\nTest Cases:")
    for i, test in enumerate(test_cases, 1):
        print(f"  Test {i}: subtract{test['input']} = {test['expected']}")
    
    print("\nRunning validation...")
    
    coding_system = get_coding_system()
    results = coding_system.validate_code(code, test_cases, "Python")
    
    print(f"\n{results['message']}")
    print(f"Passed: {results.get('passed_tests', 0)}/{results.get('total_tests', 0)}")
    
    if results['passed']:
        print("✅ PASS: All multiple parameter tests passed")
        return True
    else:
        print("❌ FAIL: Some tests failed")
        for test_result in results.get('results', []):
            if not test_result.get('passed'):
                print(f"  Test {test_result['test']}: {test_result.get('error', 'Wrong output')}")
        return False


def test_three_parameters():
    """Test functions with three parameters"""
    print("\n" + "=" * 60)
    print("TEST 3: Three Parameters Support")
    print("=" * 60)
    
    code = """
def add_three(a, b, c):
    return a + b + c
"""
    
    test_cases = [
        {"input": "(1, 2, 3)", "expected": "6"},
        {"input": "(10, 20, 30)", "expected": "60"},
        {"input": "(0, 0, 0)", "expected": "0"},
        {"input": "(-1, 1, 0)", "expected": "0"}
    ]
    
    print("\nTest Cases:")
    for i, test in enumerate(test_cases, 1):
        print(f"  Test {i}: add_three{test['input']} = {test['expected']}")
    
    coding_system = get_coding_system()
    results = coding_system.validate_code(code, test_cases, "Python")
    
    print(f"\n{results['message']}")
    print(f"Passed: {results.get('passed_tests', 0)}/{results.get('total_tests', 0)}")
    
    if results['passed']:
        print("✅ PASS: Three parameter function works correctly")
        return True
    else:
        print("❌ FAIL: Some tests failed")
        return False


def test_mixed_code_with_classes():
    """Test code with both classes and functions"""
    print("\n" + "=" * 60)
    print("TEST 4: Mixed Code (Classes + Functions)")
    print("=" * 60)
    
    code = """
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right
    
    def __str__(self):
        return f"TreeNode({self.val})"

def max_depth(root):
    if not root:
        return 0
    return 1 + max(max_depth(root.left), max_depth(root.right))
"""
    
    coding_system = get_coding_system()
    
    # Extract functions
    functions = coding_system._extract_top_level_functions(code)
    
    print(f"\nExtracted functions: {functions}")
    print(f"Expected: ['max_depth']")
    
    if 'max_depth' in functions and '__init__' not in functions and '__str__' not in functions:
        print("✅ PASS: Correctly identified 'max_depth' and ignored class methods")
        return True
    else:
        print(f"❌ FAIL: Incorrect function detection")
        return False


def test_language_support_message():
    """Test that non-Python languages show proper message"""
    print("\n" + "=" * 60)
    print("TEST 5: Language Support Messages")
    print("=" * 60)
    
    code = """
function isPalindrome(s) {
    return s === s.split('').reverse().join('');
}
"""
    
    test_cases = [
        {"input": '"hello"', "expected": "false"}
    ]
    
    coding_system = get_coding_system()
    
    # Test JavaScript
    results = coding_system.validate_code(code, test_cases, "JavaScript")
    
    print(f"\nJavaScript validation message:")
    print(f"  {results['message']}")
    
    if "Only Python validation is currently supported" in results['message']:
        print("✅ PASS: Clear message for unsupported language")
        return True
    else:
        print("❌ FAIL: Message not clear enough")
        return False


def test_expected_function_parameter():
    """Test that expected_function parameter works"""
    print("\n" + "=" * 60)
    print("TEST 6: Expected Function Parameter")
    print("=" * 60)
    
    # Code with multiple functions
    code = """
def helper_function(x):
    return x * 2

def main_solution(n):
    return helper_function(n) + 1
"""
    
    test_cases = [
        {"input": "5", "expected": "11"},
        {"input": "10", "expected": "21"}
    ]
    
    coding_system = get_coding_system()
    
    # Test with expected function specified
    results = coding_system.validate_code(code, test_cases, "Python", expected_function="main_solution")
    
    print(f"\nFunction tested: {results.get('function_tested', 'N/A')}")
    print(f"Expected: main_solution")
    
    if results.get('function_tested') == 'main_solution' and results['passed']:
        print("✅ PASS: Correctly tested specified function")
        return True
    else:
        print("❌ FAIL: Did not test correct function")
        return False


def test_palindrome_original():
    """Re-test the original palindrome problem"""
    print("\n" + "=" * 60)
    print("TEST 7: Original Palindrome Problem (Regression Test)")
    print("=" * 60)
    
    code = """
def is_palindrome(s: str) -> bool:
    return s == s[::-1]
"""
    
    test_cases = [
        {"input": "madam", "expected": "True"},
        {"input": "hello", "expected": "False"},
        {"input": "racecar", "expected": "True"}
    ]
    
    coding_system = get_coding_system()
    results = coding_system.validate_code(code, test_cases, "Python")
    
    print(f"\n{results['message']}")
    print(f"Passed: {results.get('passed_tests', 0)}/{results.get('total_tests', 0)}")
    
    if results['passed']:
        print("✅ PASS: Original problem still works")
        return True
    else:
        print("❌ FAIL: Regression detected")
        return False


if __name__ == "__main__":
    print("\n🧪 COMPREHENSIVE CODING CHALLENGE FIX TEST SUITE\n")
    
    results = []
    
    # Run all tests
    results.append(("__init__ Detection", test_init_detection_fix()))
    results.append(("Multiple Parameters", test_multiple_parameters()))
    results.append(("Three Parameters", test_three_parameters()))
    results.append(("Mixed Code (Classes)", test_mixed_code_with_classes()))
    results.append(("Language Support", test_language_support_message()))
    results.append(("Expected Function", test_expected_function_parameter()))
    results.append(("Palindrome Regression", test_palindrome_original()))
    
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
        print("\n🎉 ALL TESTS PASSED! All fixes are working correctly.")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Review the output above.")
    
    print()
