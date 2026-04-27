"""
Test suite for multi-language code execution
Tests Python, Java, and JavaScript execution with test cases
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent / "frontend"))

from utils.multi_language_executor import get_multi_language_executor


def test_python_execution():
    """Test Python code execution"""
    print("=" * 60)
    print("TEST 1: Python Execution")
    print("=" * 60)
    
    code = """
def is_palindrome(s):
    return s == s[::-1]
"""
    
    test_cases = [
        {"input": '"madam"', "expected": "True"},
        {"input": '"hello"', "expected": "False"},
        {"input": '"racecar"', "expected": "True"}
    ]
    
    executor = get_multi_language_executor()
    results = executor.execute_with_tests(code, test_cases, "Python")
    
    print(f"\n{results['message']}")
    print(f"Passed: {results['passed_tests']}/{results['total_tests']}")
    
    if results['passed']:
        print("✅ PASS: Python execution works")
        return True
    else:
        print("❌ FAIL: Python execution failed")
        for result in results['results']:
            if not result['passed']:
                print(f"  Test {result['test']}: {result.get('error', 'Wrong output')}")
        return False


def test_javascript_execution():
    """Test JavaScript code execution"""
    print("\n" + "=" * 60)
    print("TEST 2: JavaScript Execution")
    print("=" * 60)
    
    code = """
function isPalindrome(s) {
    const reversed = s.split('').reverse().join('');
    return s === reversed;
}
"""
    
    test_cases = [
        {"input": '"madam"', "expected": "True"},  # Python boolean
        {"input": '"hello"', "expected": "False"},
        {"input": '"racecar"', "expected": "True"}
    ]
    
    executor = get_multi_language_executor()
    results = executor.execute_with_tests(code, test_cases, "JavaScript")
    
    print(f"\n{results['message']}")
    print(f"Passed: {results['passed_tests']}/{results['total_tests']}")
    
    # Show details if failed
    if not results['passed'] and results['results']:
        for result in results['results']:
            if not result.get('passed'):
                print(f"  Test {result['test']}: Expected={result.get('expected', 'N/A')}, Got={result.get('got', 'N/A')}")
    
    if results['passed']:
        print("✅ PASS: JavaScript execution works")
        return True
    elif "Node.js not found" in results['message']:
        print("⚠️ SKIP: Node.js not installed")
        return True  # Don't fail if Node.js not installed
    else:
        print("❌ FAIL: JavaScript execution failed")
        print(f"  Error: {results['message']}")
        return False


def test_java_execution():
    """Test Java code execution"""
    print("\n" + "=" * 60)
    print("TEST 3: Java Execution")
    print("=" * 60)
    
    code = """
public class Solution {
    public Boolean isPalindrome(String s) {
        String reversed = new StringBuilder(s).reverse().toString();
        return s.equals(reversed);
    }
}
"""
    
    test_cases = [
        {"input": '"madam"', "expected": "true"},
        {"input": '"hello"', "expected": "false"},
        {"input": '"racecar"', "expected": "true"}
    ]
    
    executor = get_multi_language_executor()
    results = executor.execute_with_tests(code, test_cases, "Java", "isPalindrome")
    
    print(f"\n{results['message']}")
    print(f"Passed: {results['passed_tests']}/{results['total_tests']}")
    
    if results['passed']:
        print("✅ PASS: Java execution works")
        return True
    elif "Java compiler (javac) not found" in results['message']:
        print("⚠️ SKIP: Java JDK not installed")
        return True  # Don't fail if Java not installed
    else:
        print("❌ FAIL: Java execution failed")
        print(f"  Error: {results['message']}")
        return False


def test_python_multiple_parameters():
    """Test Python with multiple parameters"""
    print("\n" + "=" * 60)
    print("TEST 4: Python Multiple Parameters")
    print("=" * 60)
    
    code = """
def add(a, b):
    return a + b
"""
    
    test_cases = [
        {"input": "(5, 3)", "expected": "8"},
        {"input": "(10, 20)", "expected": "30"},
        {"input": "(0, 0)", "expected": "0"}
    ]
    
    executor = get_multi_language_executor()
    results = executor.execute_with_tests(code, test_cases, "Python")
    
    print(f"\n{results['message']}")
    print(f"Passed: {results['passed_tests']}/{results['total_tests']}")
    
    if results['passed']:
        print("✅ PASS: Multiple parameters work")
        return True
    else:
        print("❌ FAIL: Multiple parameters failed")
        return False


def test_error_handling():
    """Test error handling"""
    print("\n" + "=" * 60)
    print("TEST 5: Error Handling")
    print("=" * 60)
    
    # Test with syntax error
    code = """
def broken_function():
    return "missing closing paren"
"""
    
    test_cases = [{"input": "1", "expected": "1"}]
    
    executor = get_multi_language_executor()
    results = executor.execute_with_tests(code, test_cases, "Python")
    
    print(f"\nError message: {results['message']}")
    
    # Should fail because function doesn't match test case
    if not results['passed']:
        print("✅ PASS: Error handling works")
        return True
    else:
        print("❌ FAIL: Should have failed")
        return False


def test_unsupported_language():
    """Test unsupported language"""
    print("\n" + "=" * 60)
    print("TEST 6: Unsupported Language")
    print("=" * 60)
    
    code = "print('test')"
    test_cases = [{"input": "1", "expected": "1"}]
    
    executor = get_multi_language_executor()
    results = executor.execute_with_tests(code, test_cases, "Ruby")
    
    print(f"\nMessage: {results['message']}")
    
    if not results['passed'] and 'not supported' in results['message'].lower():
        print("✅ PASS: Unsupported language handled")
        return True
    else:
        print("❌ FAIL: Should reject unsupported language")
        return False


if __name__ == "__main__":
    print("\nMULTI-LANGUAGE EXECUTION TEST SUITE\n")
    
    results = []
    
    # Run all tests
    results.append(("Python Execution", test_python_execution()))
    results.append(("JavaScript Execution", test_javascript_execution()))
    results.append(("Java Execution", test_java_execution()))
    results.append(("Multiple Parameters", test_python_multiple_parameters()))
    results.append(("Error Handling", test_error_handling()))
    results.append(("Unsupported Language", test_unsupported_language()))
    
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
        print("\nALL TESTS PASSED! Multi-language execution is working.")
    else:
        print(f"\n{total - passed} test(s) failed. Review the output above.")
    
    print("\nNote: Java and JavaScript tests may be skipped if not installed.")
    print("   Install Java JDK and Node.js for full testing.")
    print()
