"""
Multi-language code execution service
Supports Python (local), C/C++/Java/JavaScript (via Piston API)
"""
import streamlit as st
import requests
import io
import sys
from contextlib import redirect_stdout, redirect_stderr
import time


class CodeExecutor:
    """Handle code execution for multiple languages"""
    
    # Judge0 API endpoint (free code execution API)
    JUDGE0_API = "https://judge0-ce.p.rapidapi.com"
    
    # Language ID mappings for Judge0 API
    LANGUAGE_MAP = {
        "python": {"id": 71, "name": "Python (3.8.1)"},
        "c": {"id": 50, "name": "C (GCC 9.2.0)"},
        "cpp": {"id": 54, "name": "C++ (GCC 9.2.0)"},
        "java": {"id": 62, "name": "Java (OpenJDK 13.0.1)"},
        "javascript": {"id": 63, "name": "JavaScript (Node.js 12.14.0)"}
    }
    
    @staticmethod
    def execute_python_local(code: str, user_input: str = "") -> dict:
        """Execute Python code locally with safety restrictions"""
        start_time = time.time()
        
        try:
            # Create restricted environment
            restricted_globals = {
                '__builtins__': {
                    'print': print,
                    'len': len,
                    'range': range,
                    'str': str,
                    'int': int,
                    'float': float,
                    'list': list,
                    'dict': dict,
                    'tuple': tuple,
                    'set': set,
                    'bool': bool,
                    'sum': sum,
                    'max': max,
                    'min': min,
                    'abs': abs,
                    'round': round,
                    'sorted': sorted,
                    'enumerate': enumerate,
                    'zip': zip,
                    'map': map,
                    'filter': filter,
                }
            }
            
            # Capture output
            stdout_capture = io.StringIO()
            stderr_capture = io.StringIO()
            
            # Mock input function if user provided input
            if user_input:
                input_lines = user_input.strip().split('\n')
                input_iter = iter(input_lines)
                restricted_globals['__builtins__']['input'] = lambda prompt="": next(input_iter, "")
            
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                exec(code, restricted_globals)
            
            execution_time = time.time() - start_time
            output = stdout_capture.getvalue()
            errors = stderr_capture.getvalue()
            
            return {
                "success": True,
                "output": output if output else "Program executed successfully (no output)",
                "error": errors if errors else None,
                "execution_time": execution_time
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            return {
                "success": False,
                "output": "",
                "error": f"Runtime Error: {str(e)}",
                "execution_time": execution_time
            }
    
    @staticmethod
    def execute_via_judge0(code: str, language: str, user_input: str = "") -> dict:
        """Execute code via Judge0 API for C/C++/Java/JavaScript"""
        start_time = time.time()
        
        try:
            lang_config = CodeExecutor.LANGUAGE_MAP.get(language.lower())
            if not lang_config:
                return {
                    "success": False,
                    "output": "",
                    "error": f"Unsupported language: {language}",
                    "execution_time": 0
                }
            
            # Step 1: Submit code for execution
            import base64
            
            payload = {
                "language_id": lang_config["id"],
                "source_code": base64.b64encode(code.encode()).decode(),
                "stdin": base64.b64encode(user_input.encode()).decode() if user_input else ""
            }
            
            headers = {
                "content-type": "application/json",
                "X-RapidAPI-Key": "YOUR_RAPIDAPI_KEY_HERE",  # Users need to add their own key
                "X-RapidAPI-Host": "judge0-ce.p.rapidapi.com"
            }
            
            # Try without API key first (public endpoint)
            response = requests.post(
                "https://judge0-ce.p.rapidapi.com/submissions?base64_encoded=true&wait=true",
                json=payload,
                timeout=15
            )
            
            execution_time = time.time() - start_time
            
            if response.status_code == 201 or response.status_code == 200:
                result = response.json()
                
                # Decode output
                stdout = base64.b64decode(result.get("stdout", "")).decode() if result.get("stdout") else ""
                stderr = base64.b64decode(result.get("stderr", "")).decode() if result.get("stderr") else ""
                compile_output = base64.b64decode(result.get("compile_output", "")).decode() if result.get("compile_output") else ""
                
                # Check status
                status_id = result.get("status", {}).get("id")
                
                # Status 3 = Accepted (success)
                if status_id == 3:
                    return {
                        "success": True,
                        "output": stdout if stdout else "Program executed successfully (no output)",
                        "error": None,
                        "execution_time": execution_time
                    }
                # Status 6 = Compilation Error
                elif status_id == 6:
                    return {
                        "success": False,
                        "output": "",
                        "error": f"Compilation Error:\n{compile_output or stderr}",
                        "execution_time": execution_time
                    }
                # Other errors
                else:
                    error_msg = stderr or compile_output or result.get("status", {}).get("description", "Unknown error")
                    return {
                        "success": False,
                        "output": stdout,
                        "error": f"Runtime Error:\n{error_msg}",
                        "execution_time": execution_time
                    }
            else:
                # Fallback: Use alternative free API
                return CodeExecutor._execute_via_onecompiler(code, language, user_input)
                
        except requests.Timeout:
            return {
                "success": False,
                "output": "",
                "error": "Execution timeout - code took too long to run",
                "execution_time": time.time() - start_time
            }
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "error": f"Execution Error: {str(e)}",
                "execution_time": time.time() - start_time
            }
    
    @staticmethod
    def _execute_via_onecompiler(code: str, language: str, user_input: str = "") -> dict:
        """Fallback: Execute via OneCompiler API (no auth required)"""
        start_time = time.time()
        
        try:
            # OneCompiler language mappings
            lang_map = {
                "python": "python",
                "c": "c",
                "cpp": "cpp",
                "java": "java",
                "javascript": "nodejs"
            }
            
            lang_name = lang_map.get(language.lower())
            if not lang_name:
                return None
            
            payload = {
                "language": lang_name,
                "stdin": user_input,
                "files": [
                    {
                        "name": f"main.{CodeExecutor._get_file_extension(language)}",
                        "content": code
                    }
                ]
            }
            
            response = requests.post(
                "https://onecompiler.com/api/code/exec",
                json=payload,
                timeout=10
            )
            
            execution_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                
                stdout = result.get("stdout", "")
                stderr = result.get("stderr", "")
                exception = result.get("exception", "")
                
                if exception or stderr:
                    return {
                        "success": False,
                        "output": stdout,
                        "error": f"Error:\n{exception or stderr}",
                        "execution_time": execution_time
                    }
                
                return {
                    "success": True,
                    "output": stdout if stdout else "Program executed successfully (no output)",
                    "error": None,
                    "execution_time": execution_time
                }
            else:
                return None  # Signal complete failure
                
        except requests.Timeout:
            return None
        except Exception as e:
            return None
    
    @staticmethod
    def _get_file_extension(language: str) -> str:
        """Get file extension for language"""
        extensions = {
            "python": "py",
            "c": "c",
            "cpp": "cpp",
            "java": "java",
            "javascript": "js"
        }
        return extensions.get(language.lower(), "txt")
    
    @staticmethod
    def execute(code: str, language: str, user_input: str = "") -> dict:
        """Main execution method - routes to appropriate executor"""
        language = language.lower()
        
        # Python always runs locally (most reliable)
        if language == "python":
            return CodeExecutor.execute_python_local(code, user_input)
        
        # For other languages, try external APIs with better error handling
        elif language in ["c", "cpp", "java", "javascript"]:
            # Try Piston API first (free, no auth required)
            result = CodeExecutor._execute_via_piston(code, language, user_input)
            
            # If Piston returned None, try OneCompiler
            if result is None:
                result = CodeExecutor._execute_via_onecompiler(code, language, user_input)
            
            # If still None, return helpful error
            if result is None:
                return {
                    "success": False,
                    "output": "",
                    "error": f"⚠️ External code execution services are currently unavailable.\n\n"
                           f"To run your {language.upper()} code:\n"
                           f"1. Copy the code below\n"
                           f"2. Use an online compiler:\n"
                           f"   • https://www.onlinegdb.com\n"
                           f"   • https://replit.com\n"
                           f"   • https://www.programiz.com/online-compiler\n"
                           f"3. Or install a local compiler\n\n"
                           f"💡 Python code runs locally and always works!",
                    "execution_time": 0
                }
            
            return result
        
        else:
            return {
                "success": False,
                "output": "",
                "error": f"Unsupported language: {language}",
                "execution_time": 0
            }

    
    @staticmethod
    def _execute_via_piston(code: str, language: str, user_input: str = "") -> dict:
        """Execute code via Piston API (free, no auth required)"""
        start_time = time.time()
        
        try:
            # Piston language mappings
            lang_map = {
                "python": "python",
                "c": "c",
                "cpp": "c++",
                "java": "java",
                "javascript": "javascript"
            }
            
            lang_name = lang_map.get(language.lower())
            if not lang_name:
                return {
                    "success": False,
                    "output": "",
                    "error": f"Unsupported language: {language}",
                    "execution_time": 0
                }
            
            payload = {
                "language": lang_name,
                "version": "*",  # Use latest version
                "files": [
                    {
                        "content": code
                    }
                ],
                "stdin": user_input
            }
            
            response = requests.post(
                "https://emkc.org/api/v2/piston/execute",
                json=payload,
                timeout=10
            )
            
            execution_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                
                stdout = result.get("run", {}).get("stdout", "")
                stderr = result.get("run", {}).get("stderr", "")
                
                if stderr:
                    return {
                        "success": False,
                        "output": stdout,
                        "error": f"Error:\n{stderr}",
                        "execution_time": execution_time
                    }
                
                return {
                    "success": True,
                    "output": stdout if stdout else "Program executed successfully (no output)",
                    "error": None,
                    "execution_time": execution_time
                }
            else:
                # API error
                return None  # Signal to try next fallback
                
        except requests.Timeout:
            return None  # Signal to try next fallback
        except Exception as e:
            return None  # Signal to try next fallback
