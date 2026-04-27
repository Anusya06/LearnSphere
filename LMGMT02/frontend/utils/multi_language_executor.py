"""
Multi-Language Code Executor with Judge0 API
Supports 60+ languages via cloud execution - no local installation needed!
"""
import subprocess
import tempfile
import os
import json
import ast
from pathlib import Path
import time
import re
import requests
import base64


class MultiLanguageExecutor:
    """Execute code in multiple languages using Judge0 API"""
    
    # Judge0 language IDs
    LANGUAGE_IDS = {
        'python': 71,      # Python 3.8.1
        'javascript': 63,  # JavaScript (Node.js 12.14.0)
        'java': 62,        # Java (OpenJDK 13.0.1)
        'c': 50,           # C (GCC 9.2.0)
        'cpp': 54,         # C++ (GCC 9.2.0)
        'csharp': 51,      # C# (Mono 6.6.0.161)
        'go': 60,          # Go (1.13.5)
        'ruby': 72,        # Ruby (2.7.0)
        'php': 68,         # PHP (7.4.1)
        'swift': 83,       # Swift (5.2.3)
        'kotlin': 78,      # Kotlin (1.3.70)
        'rust': 73,        # Rust (1.40.0)
        'typescript': 74,  # TypeScript (3.7.4)
    }
    
    def __init__(self, use_judge0=True):
        self.timeout = 5  # 5 second timeout
        self.memory_limit = 256  # 256 MB memory limit
        self.use_judge0 = use_judge0
        
        # Judge0 API endpoint (free tier)
        self.judge0_url = "https://judge0-ce.p.rapidapi.com"
        
        # You can get a free API key from: https://rapidapi.com/judge0-official/api/judge0-ce
        # For now, using the public endpoint (limited requests)
        self.judge0_headers = {
            "content-type": "application/json",
            "X-RapidAPI-Key": os.getenv("RAPIDAPI_KEY", ""),  # Optional: Add your key
            "X-RapidAPI-Host": "judge0-ce.p.rapidapi.com"
        }
    
    def execute_with_tests(self, code: str, test_cases: list, language: str, expected_function: str = None) -> dict:
        """
        Execute code and validate against test cases
        
        Args:
            code: User's solution code
            test_cases: List of test cases with 'input' and 'expected'
            language: Programming language
            expected_function: Expected function name
            
        Returns:
            dict with test results
        """
        language_lower = language.lower()
        
        # Use Judge0 for all languages if enabled
        if self.use_judge0 and language_lower in self.LANGUAGE_IDS:
            return self._execute_with_judge0(code, test_cases, language_lower, expected_function)
        
        # Fallback to local execution for Python
        if language_lower == "python":
            return self._execute_python_tests(code, test_cases, expected_function)
        
        return {
            'passed': False,
            'message': f'⚠️ Language "{language}" requires Judge0 API or local installation',
            'results': [],
            'total_tests': len(test_cases),
            'passed_tests': 0
        }
    
    def _execute_with_judge0(self, code: str, test_cases: list, language: str, expected_function: str = None) -> dict:
        """Execute code using Judge0 API"""
        try:
            language_id = self.LANGUAGE_IDS.get(language)
            
            if not language_id:
                return {
                    'passed': False,
                    'message': f'Language "{language}" not supported by Judge0',
                    'results': [],
                    'total_tests': len(test_cases),
                    'passed_tests': 0
                }
            
            # Extract function name
            func_name = expected_function or self._extract_function_name(code, language)
            
            if not func_name:
                return {
                    'passed': False,
                    'message': 'No function found in code',
                    'results': [],
                    'total_tests': len(test_cases),
                    'passed_tests': 0
                }
            
            # Create test harness
            test_code = self._create_judge0_test_harness(code, func_name, test_cases, language)
            
            # Submit to Judge0
            submission_data = {
                "source_code": base64.b64encode(test_code.encode()).decode(),
                "language_id": language_id,
                "stdin": "",
                "expected_output": ""
            }
            
            # Submit code
            response = requests.post(
                f"{self.judge0_url}/submissions?base64_encoded=true&wait=true",
                json=submission_data,
                headers=self.judge0_headers,
                timeout=10
            )
            
            if response.status_code != 201 and response.status_code != 200:
                # Fallback to local execution for Python
                if language == 'python':
                    return self._execute_python_tests(code, test_cases, expected_function)
                
                return {
                    'passed': False,
                    'message': f'Judge0 API error: {response.status_code}. Using local execution fallback.',
                    'results': [],
                    'total_tests': len(test_cases),
                    'passed_tests': 0
                }
            
            result = response.json()
            
            # Check for compilation or runtime errors
            if result.get('status', {}).get('id') in [6, 11, 12, 13]:  # Compilation Error, Runtime Error, etc.
                error_msg = result.get('compile_output') or result.get('stderr') or result.get('message', 'Unknown error')
                if error_msg:
                    error_msg = base64.b64decode(error_msg).decode() if result.get('compile_output') else error_msg
                
                return {
                    'passed': False,
                    'message': f'Execution error:\n{error_msg}',
                    'results': [],
                    'total_tests': len(test_cases),
                    'passed_tests': 0
                }
            
            # Parse output
            stdout = result.get('stdout', '')
            if stdout:
                stdout = base64.b64decode(stdout).decode()
            
            # Parse test results
            return self._parse_test_results(stdout, test_cases)
            
        except requests.exceptions.RequestException as e:
            # Fallback to local execution for Python
            if language == 'python':
                print(f"Judge0 API unavailable, using local Python execution: {e}")
                return self._execute_python_tests(code, test_cases, expected_function)
            
            return {
                'passed': False,
                'message': f'Judge0 API unavailable. For Python, using local execution. For other languages, please try again.',
                'results': [],
                'total_tests': len(test_cases),
                'passed_tests': 0
            }
        except Exception as e:
            return {
                'passed': False,
                'message': f'Execution error: {str(e)}',
                'results': [],
                'total_tests': len(test_cases),
                'passed_tests': 0
            }
    
    def _create_judge0_test_harness(self, user_code: str, func_name: str, test_cases: list, language: str) -> str:
        """Create test harness for Judge0 execution"""
        if language == 'python':
            return self._create_python_judge0_harness(user_code, func_name, test_cases)
        elif language == 'javascript':
            return self._create_js_judge0_harness(user_code, func_name, test_cases)
        elif language == 'java':
            return self._create_java_judge0_harness(user_code, func_name, test_cases)
        else:
            return user_code
    
    def _create_python_judge0_harness(self, user_code: str, func_name: str, test_cases: list) -> str:
        """Create Python test harness for Judge0"""
        harness = f"{user_code}\n\n"
        harness += "import json\n\n"
        harness += "passed = 0\n"
        harness += f"total = {len(test_cases)}\n\n"
        
        for i, test in enumerate(test_cases, 1):
            test_input = test['input']
            expected = test['expected']
            
            harness += f"# Test {i}\n"
            harness += "try:\n"
            
            # Parse input
            parsed_input = self._safe_parse_input(test_input)
            if isinstance(parsed_input, tuple):
                harness += f"    result = {func_name}{test_input}\n"
            else:
                harness += f"    result = {func_name}({test_input})\n"
            
            harness += f"    expected = {expected}\n"
            harness += f"    if result == expected:\n"
            harness += f"        print('TEST_{i}_PASSED')\n"
            harness += f"        passed += 1\n"
            harness += f"    else:\n"
            harness += f"        print('TEST_{i}_FAILED')\n"
            harness += f"        print(f'Expected: {{expected}}, Got: {{result}}')\n"
            harness += "except Exception as e:\n"
            harness += f"    print('TEST_{i}_ERROR')\n"
            harness += f"    print(f'Error: {{e}}')\n\n"
        
        harness += f"print(f'TOTAL_PASSED: {{passed}}')\n"
        harness += f"print(f'TOTAL_TESTS: {{total}}')\n"
        
        return harness
    
    def _create_js_judge0_harness(self, user_code: str, func_name: str, test_cases: list) -> str:
        """Create JavaScript test harness for Judge0"""
        harness = f"{user_code}\n\n"
        harness += "let passed = 0;\n"
        harness += f"const total = {len(test_cases)};\n\n"
        
        for i, test in enumerate(test_cases, 1):
            test_input = test['input']
            expected = test['expected']
            
            js_input = self._convert_to_js_input(test_input)
            js_expected = self._convert_to_js_value(expected)
            input_display = test_input.replace('"', '\\"')
            
            harness += f"// Test {i}\n"
            harness += "try {\n"
            harness += f"    const result = {func_name}({js_input});\n"
            harness += f"    const expected = {js_expected};\n"
            harness += f"    if (JSON.stringify(result) === JSON.stringify(expected)) {{\n"
            harness += f"        console.log('TEST_{i}_PASSED');\n"
            harness += f"        passed++;\n"
            harness += f"    }} else {{\n"
            harness += f"        console.log('TEST_{i}_FAILED');\n"
            harness += f"        console.log('Expected: ' + JSON.stringify(expected) + ', Got: ' + JSON.stringify(result));\n"
            harness += f"    }}\n"
            harness += "} catch (e) {\n"
            harness += f"    console.log('TEST_{i}_ERROR');\n"
            harness += f"    console.log('Error: ' + e.message);\n"
            harness += "}\n\n"
        
        harness += "console.log('TOTAL_PASSED: ' + passed);\n"
        harness += "console.log('TOTAL_TESTS: ' + total);\n"
        
        return harness
    
    def _create_java_judge0_harness(self, user_code: str, func_name: str, test_cases: list) -> str:
        """Create Java test harness for Judge0"""
        # Extract class name
        class_match = re.search(r'class\s+(\w+)', user_code)
        class_name = class_match.group(1) if class_match else 'Solution'
        
        # Replace class name with Main for Judge0
        user_code_modified = re.sub(r'class\s+\w+', 'class Main', user_code)
        
        harness = f"{user_code_modified}\n\n"
        
        # Add main method if not present
        if 'public static void main' not in user_code:
            harness += "    public static void main(String[] args) {\n"
            harness += "        Main solution = new Main();\n"
            harness += f"        int passed = 0;\n"
            harness += f"        int total = {len(test_cases)};\n\n"
            
            for i, test in enumerate(test_cases, 1):
                test_input = test['input']
                expected = test['expected']
                
                java_input = self._convert_to_java_input(test_input)
                java_expected = self._convert_to_java_value(expected)
                
                harness += f"        // Test {i}\n"
                harness += "        try {\n"
                harness += f"            var result = solution.{func_name}({java_input});\n"
                harness += f"            var expected = {java_expected};\n"
                harness += f"            if (result.equals(expected)) {{\n"
                harness += f"                System.out.println(\"TEST_{i}_PASSED\");\n"
                harness += f"                passed++;\n"
                harness += f"            }} else {{\n"
                harness += f"                System.out.println(\"TEST_{i}_FAILED\");\n"
                harness += f"                System.out.println(\"Expected: \" + expected + \", Got: \" + result);\n"
                harness += f"            }}\n"
                harness += "        } catch (Exception e) {\n"
                harness += f"            System.out.println(\"TEST_{i}_ERROR\");\n"
                harness += f"            System.out.println(\"Error: \" + e.getMessage());\n"
                harness += "        }\n\n"
            
            harness += "        System.out.println(\"TOTAL_PASSED: \" + passed);\n"
            harness += "        System.out.println(\"TOTAL_TESTS: \" + total);\n"
            harness += "    }\n"
            harness += "}\n"
        
        return harness
    
    def _extract_function_name(self, code: str, language: str) -> str:
        """Extract function name from code based on language"""
        if language == 'python':
            functions = self._extract_python_functions(code)
            return functions[0] if functions else None
        elif language == 'javascript':
            return self._extract_js_function_name(code)
        elif language == 'java':
            return self._extract_java_method_name(code)
        return None
    
    def _execute_python_tests(self, code: str, test_cases: list, expected_function: str = None) -> dict:
        """Execute Python code with test cases"""
        try:
            # Extract top-level functions
            top_level_functions = self._extract_python_functions(code)
            
            if not top_level_functions:
                return {
                    'passed': False,
                    'message': 'No function definition found in code',
                    'results': [],
                    'total_tests': len(test_cases),
                    'passed_tests': 0
                }
            
            # Determine function to test
            if expected_function and expected_function in top_level_functions:
                func_name = expected_function
            else:
                func_name = top_level_functions[0]
            
            # Execute code in isolated namespace
            namespace = {}
            try:
                exec(code, namespace)
            except Exception as e:
                return {
                    'passed': False,
                    'message': f'Code execution error: {str(e)}',
                    'results': [],
                    'total_tests': len(test_cases),
                    'passed_tests': 0
                }
            
            if func_name not in namespace:
                return {
                    'passed': False,
                    'message': f'Function "{func_name}" not found',
                    'results': [],
                    'total_tests': len(test_cases),
                    'passed_tests': 0
                }
            
            func = namespace[func_name]
            
            # Get function signature
            import inspect
            sig = inspect.signature(func)
            param_count = len(sig.parameters)
            
            # Run test cases
            results = []
            all_passed = True
            
            for i, test in enumerate(test_cases, 1):
                try:
                    test_input = self._safe_parse_input(test['input'])
                    expected = self._safe_parse_input(test['expected'])
                    
                    # Smart function calling
                    if isinstance(test_input, tuple):
                        result = func(*test_input)
                    elif isinstance(test_input, list) and param_count > 1 and len(test_input) == param_count:
                        result = func(*test_input)
                    else:
                        result = func(test_input)
                    
                    passed = result == expected
                    all_passed = all_passed and passed
                    
                    results.append({
                        'test': i,
                        'passed': passed,
                        'input': str(test_input),
                        'expected': str(expected),
                        'got': str(result)
                    })
                    
                except Exception as e:
                    all_passed = False
                    results.append({
                        'test': i,
                        'passed': False,
                        'input': test.get('input', 'N/A'),
                        'error': str(e)
                    })
            
            return {
                'passed': all_passed,
                'message': '✅ All tests passed!' if all_passed else '❌ Some tests failed',
                'results': results,
                'total_tests': len(test_cases),
                'passed_tests': sum(1 for r in results if r['passed']),
                'function_tested': func_name
            }
            
        except Exception as e:
            return {
                'passed': False,
                'message': f'Validation error: {str(e)}',
                'results': [],
                'total_tests': len(test_cases),
                'passed_tests': 0
            }
    
    def _execute_java_tests(self, code: str, test_cases: list, expected_function: str = None) -> dict:
        """Execute Java code with test cases"""
        try:
            # Extract class name and method name
            class_name = self._extract_java_class_name(code)
            method_name = expected_function or self._extract_java_method_name(code)
            
            if not class_name:
                return {
                    'passed': False,
                    'message': 'No public class found in Java code',
                    'results': [],
                    'total_tests': len(test_cases),
                    'passed_tests': 0
                }
            
            if not method_name:
                return {
                    'passed': False,
                    'message': 'No public method found in Java code',
                    'results': [],
                    'total_tests': len(test_cases),
                    'passed_tests': 0
                }
            
            # Create test harness
            test_harness = self._create_java_test_harness(code, class_name, method_name, test_cases)
            
            # Execute in temporary directory
            with tempfile.TemporaryDirectory() as tmpdir:
                # Write test file
                test_file = Path(tmpdir) / f"{class_name}Test.java"
                test_file.write_text(test_harness)
                
                # Compile
                compile_result = subprocess.run(
                    ['javac', str(test_file)],
                    capture_output=True,
                    text=True,
                    timeout=self.timeout,
                    cwd=tmpdir
                )
                
                if compile_result.returncode != 0:
                    return {
                        'passed': False,
                        'message': f'Compilation error:\n{compile_result.stderr}',
                        'results': [],
                        'total_tests': len(test_cases),
                        'passed_tests': 0
                    }
                
                # Execute
                run_result = subprocess.run(
                    ['java', f'{class_name}Test'],
                    capture_output=True,
                    text=True,
                    timeout=self.timeout,
                    cwd=tmpdir
                )
                
                if run_result.returncode != 0 and not run_result.stdout:
                    return {
                        'passed': False,
                        'message': f'Runtime error:\n{run_result.stderr}',
                        'results': [],
                        'total_tests': len(test_cases),
                        'passed_tests': 0
                    }
                
                # Parse results
                return self._parse_test_results(run_result.stdout, test_cases)
                
        except subprocess.TimeoutExpired:
            return {
                'passed': False,
                'message': f'⏱️ Execution timeout ({self.timeout}s)',
                'results': [],
                'total_tests': len(test_cases),
                'passed_tests': 0
            }
        except FileNotFoundError:
            return {
                'passed': False,
                'message': '❌ Java compiler (javac) not found. Please install Java JDK.',
                'results': [],
                'total_tests': len(test_cases),
                'passed_tests': 0
            }
        except Exception as e:
            return {
                'passed': False,
                'message': f'Execution error: {str(e)}',
                'results': [],
                'total_tests': len(test_cases),
                'passed_tests': 0
            }
    
    def _execute_javascript_tests(self, code: str, test_cases: list, expected_function: str = None) -> dict:
        """Execute JavaScript code with test cases"""
        try:
            # Extract function name
            func_name = expected_function or self._extract_js_function_name(code)
            
            if not func_name:
                return {
                    'passed': False,
                    'message': 'No function found in JavaScript code',
                    'results': [],
                    'total_tests': len(test_cases),
                    'passed_tests': 0
                }
            
            # Create test harness
            test_harness = self._create_js_test_harness(code, func_name, test_cases)
            
            # Execute in temporary directory
            with tempfile.TemporaryDirectory() as tmpdir:
                # Write test file
                test_file = Path(tmpdir) / "solution_test.js"
                test_file.write_text(test_harness)
                
                # Execute with Node.js
                run_result = subprocess.run(
                    ['node', str(test_file)],
                    capture_output=True,
                    text=True,
                    timeout=self.timeout,
                    cwd=tmpdir
                )
                
                if run_result.returncode != 0 and not run_result.stdout:
                    return {
                        'passed': False,
                        'message': f'Runtime error:\n{run_result.stderr}',
                        'results': [],
                        'total_tests': len(test_cases),
                        'passed_tests': 0
                    }
                
                # Parse results
                return self._parse_test_results(run_result.stdout, test_cases)
                
        except subprocess.TimeoutExpired:
            return {
                'passed': False,
                'message': f'⏱️ Execution timeout ({self.timeout}s)',
                'results': [],
                'total_tests': len(test_cases),
                'passed_tests': 0
            }
        except FileNotFoundError:
            return {
                'passed': False,
                'message': '❌ Node.js not found. Please install Node.js.',
                'results': [],
                'total_tests': len(test_cases),
                'passed_tests': 0
            }
        except Exception as e:
            return {
                'passed': False,
                'message': f'Execution error: {str(e)}',
                'results': [],
                'total_tests': len(test_cases),
                'passed_tests': 0
            }
    
    def _create_java_test_harness(self, user_code: str, class_name: str, method_name: str, test_cases: list) -> str:
        """Create Java test harness"""
        # Remove public class declaration from user code
        user_code_cleaned = re.sub(r'public\s+class\s+\w+\s*\{', 'class UserSolution {', user_code, count=1)
        
        test_code = f"""
{user_code_cleaned}

public class {class_name}Test {{
    public static void main(String[] args) {{
        UserSolution solution = new UserSolution();
        int passed = 0;
        int total = {len(test_cases)};
        
"""
        
        for i, test in enumerate(test_cases, 1):
            test_input = test['input']
            expected = test['expected']
            
            # Parse input for Java
            java_input = self._convert_to_java_input(test_input)
            java_expected = self._convert_to_java_value(expected)
            
            test_code += f"""
        // Test {i}
        try {{
            var result{i} = solution.{method_name}({java_input});
            var expected{i} = {java_expected};
            boolean passed{i} = result{i}.equals(expected{i});
            
            if (passed{i}) {{
                System.out.println("TEST_{i}_PASSED");
                passed++;
            }} else {{
                System.out.println("TEST_{i}_FAILED");
                System.out.println("INPUT: {test_input}");
                System.out.println("EXPECTED: " + expected{i});
                System.out.println("GOT: " + result{i});
            }}
        }} catch (Exception e) {{
            System.out.println("TEST_{i}_ERROR");
            System.out.println("ERROR: " + e.getMessage());
        }}
"""
        
        test_code += f"""
        System.out.println("TOTAL_PASSED: " + passed);
        System.out.println("TOTAL_TESTS: " + total);
    }}
}}
"""
        return test_code
    
    def _create_js_test_harness(self, user_code: str, func_name: str, test_cases: list) -> str:
        """Create JavaScript test harness"""
        test_code = f"""
{user_code}

let passed = 0;
const total = {len(test_cases)};

"""
        
        for i, test in enumerate(test_cases, 1):
            test_input = test['input']
            expected = test['expected']
            
            # Parse input for JavaScript
            js_input = self._convert_to_js_input(test_input)
            js_expected = self._convert_to_js_value(expected)
            
            # Escape quotes in input string for console.log
            input_display = test_input.replace('"', '\\"')
            
            test_code += f"""
// Test {i}
try {{
    const result{i} = {func_name}({js_input});
    const expected{i} = {js_expected};
    const passed{i} = JSON.stringify(result{i}) === JSON.stringify(expected{i});
    
    if (passed{i}) {{
        console.log("TEST_{i}_PASSED");
        passed++;
    }} else {{
        console.log("TEST_{i}_FAILED");
        console.log("INPUT: {input_display}");
        console.log("EXPECTED: " + JSON.stringify(expected{i}));
        console.log("GOT: " + JSON.stringify(result{i}));
    }}
}} catch (e) {{
    console.log("TEST_{i}_ERROR");
    console.log("ERROR: " + e.message);
}}

"""
        
        test_code += """
console.log("TOTAL_PASSED: " + passed);
console.log("TOTAL_TESTS: " + total);
"""
        return test_code
    
    def _parse_test_results(self, output: str, test_cases: list) -> dict:
        """Parse test execution output"""
        results = []
        passed_count = 0
        
        lines = output.strip().split('\n')
        
        for i in range(1, len(test_cases) + 1):
            test_passed = f"TEST_{i}_PASSED" in output
            test_failed = f"TEST_{i}_FAILED" in output
            test_error = f"TEST_{i}_ERROR" in output
            
            if test_passed:
                results.append({
                    'test': i,
                    'passed': True,
                    'input': test_cases[i-1]['input'],
                    'expected': test_cases[i-1]['expected'],
                    'got': test_cases[i-1]['expected']
                })
                passed_count += 1
            elif test_failed or test_error:
                # Extract error details
                error_msg = "Test failed"
                for line in lines:
                    if "ERROR:" in line:
                        error_msg = line.split("ERROR:")[-1].strip()
                        break
                
                results.append({
                    'test': i,
                    'passed': False,
                    'input': test_cases[i-1]['input'],
                    'error': error_msg
                })
        
        all_passed = passed_count == len(test_cases)
        
        return {
            'passed': all_passed,
            'message': '✅ All tests passed!' if all_passed else '❌ Some tests failed',
            'results': results,
            'total_tests': len(test_cases),
            'passed_tests': passed_count
        }
    
    def _extract_python_functions(self, code: str) -> list:
        """Extract top-level Python function names"""
        try:
            tree = ast.parse(code)
            functions = []
            
            for node in tree.body:
                if isinstance(node, ast.FunctionDef):
                    if not node.name.startswith('__'):
                        functions.append(node.name)
            
            return functions
        except:
            return []
    
    def _extract_java_class_name(self, code: str) -> str:
        """Extract public class name from Java code"""
        match = re.search(r'public\s+class\s+(\w+)', code)
        return match.group(1) if match else None
    
    def _extract_java_method_name(self, code: str) -> str:
        """Extract public method name from Java code"""
        match = re.search(r'public\s+(?:static\s+)?\w+\s+(\w+)\s*\(', code)
        return match.group(1) if match else None
    
    def _extract_js_function_name(self, code: str) -> str:
        """Extract function name from JavaScript code"""
        # Try function declaration
        match = re.search(r'function\s+(\w+)\s*\(', code)
        if match:
            return match.group(1)
        
        # Try arrow function
        match = re.search(r'(?:const|let|var)\s+(\w+)\s*=\s*\(', code)
        if match:
            return match.group(1)
        
        return None
    
    def _safe_parse_input(self, input_str: str):
        """Safely parse test input"""
        input_str = input_str.strip()
        
        try:
            return ast.literal_eval(input_str)
        except (ValueError, SyntaxError):
            if (input_str.startswith('"') and input_str.endswith('"')) or \
               (input_str.startswith("'") and input_str.endswith("'")):
                return input_str[1:-1]
            return input_str
    
    def _convert_to_java_input(self, input_str: str) -> str:
        """Convert test input to Java format"""
        try:
            value = self._safe_parse_input(input_str)
            
            if isinstance(value, str):
                return f'"{value}"'
            elif isinstance(value, bool):
                return str(value).lower()
            elif isinstance(value, (int, float)):
                return str(value)
            elif isinstance(value, list):
                return ', '.join(self._convert_to_java_value(str(v)) for v in value)
            elif isinstance(value, tuple):
                return ', '.join(self._convert_to_java_value(str(v)) for v in value)
            else:
                return str(value)
        except:
            return input_str
    
    def _convert_to_java_value(self, value_str: str) -> str:
        """Convert expected value to Java format"""
        try:
            value = self._safe_parse_input(value_str)
            
            if isinstance(value, str):
                return f'"{value}"'
            elif isinstance(value, bool):
                return 'Boolean.valueOf(' + str(value).lower() + ')'
            elif isinstance(value, int):
                return f'Integer.valueOf({value})'
            elif isinstance(value, float):
                return f'Double.valueOf({value})'
            else:
                return f'"{value}"'
        except:
            return f'"{value_str}"'
    
    def _convert_to_js_input(self, input_str: str) -> str:
        """Convert test input to JavaScript format"""
        try:
            value = self._safe_parse_input(input_str)
            
            if isinstance(value, str):
                return f'"{value}"'
            elif isinstance(value, bool):
                return str(value).lower()
            elif isinstance(value, (int, float)):
                return str(value)
            elif isinstance(value, list):
                return json.dumps(value)
            elif isinstance(value, tuple):
                return ', '.join(json.dumps(v) if isinstance(v, str) else str(v) for v in value)
            else:
                return json.dumps(value)
        except:
            return input_str
    
    def _convert_to_js_value(self, value_str: str) -> str:
        """Convert expected value to JavaScript format"""
        try:
            value = self._safe_parse_input(value_str)
            
            if isinstance(value, str):
                return f'"{value}"'
            elif isinstance(value, bool):
                return str(value).lower()
            elif isinstance(value, (int, float)):
                return str(value)
            elif isinstance(value, (list, dict)):
                return json.dumps(value)
            else:
                return f'"{value}"'
        except:
            return f'"{value_str}"'


def get_multi_language_executor():
    """Get multi-language executor instance with Judge0 enabled"""
    return MultiLanguageExecutor(use_judge0=True)
