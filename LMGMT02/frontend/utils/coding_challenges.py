"""
Coding Challenges System
AI-generated coding problems with validation and feedback
"""
import streamlit as st
from groq import Groq
import json
import sqlite3
from pathlib import Path
from datetime import datetime
import re


class CodingChallengeSystem:
    """Manage coding challenges and submissions"""
    
    def __init__(self):
        self.db_path = Path(__file__).parent.parent / "coding_challenges.db"
        self._init_database()
        
        try:
            self.client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        except KeyError:
            self.client = None
    
    def _init_database(self):
        """Initialize coding challenges database"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS challenges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                difficulty TEXT NOT NULL,
                language TEXT NOT NULL,
                starter_code TEXT,
                solution_code TEXT,
                test_cases TEXT,
                hints TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                challenge_id INTEGER NOT NULL,
                code TEXT NOT NULL,
                passed BOOLEAN DEFAULT 0,
                execution_time REAL,
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (challenge_id) REFERENCES challenges(id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_progress (
                user_id INTEGER NOT NULL,
                challenge_id INTEGER NOT NULL,
                completed BOOLEAN DEFAULT 0,
                attempts INTEGER DEFAULT 0,
                best_time REAL,
                completed_at TIMESTAMP,
                PRIMARY KEY (user_id, challenge_id),
                FOREIGN KEY (challenge_id) REFERENCES challenges(id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def generate_challenge(self, topic: str, difficulty: str, language: str = "Python", max_retries: int = 3):
        """
        Generate a coding challenge using AI with retry logic and fallback
        
        Args:
            topic: Challenge topic (e.g., "Palindrome", "Arrays")
            difficulty: Easy, Medium, or Hard
            language: Programming language
            max_retries: Maximum number of retry attempts
            
        Returns:
            dict: Challenge data or fallback challenge if generation fails
        """
        if not self.client:
            return self._get_fallback_challenge(topic, difficulty, language)
        
        # Language-specific formatting instructions
        formatting_rules = {
            "Python": """
- Use 4 spaces for indentation
- Follow PEP 8 style guide
- Use clear variable names
- Add type hints
- Multi-line format, never single-line""",
            "JavaScript": """
- Use 2 spaces for indentation
- Use camelCase for variables
- Use proper braces and semicolons
- Multi-line format with clear structure
- Example:
  function isPalindrome(s) {
      const reversed = s.split('').reverse().join('');
      return s === reversed;
  }""",
            "Java": """
- Use 4 spaces for indentation
- Full class structure with public static methods
- Proper braces and formatting
- Example:
  public class Solution {
      public static boolean isPalindrome(String s) {
          String reversed = new StringBuilder(s).reverse().toString();
          return s.equals(reversed);
      }
  }""",
            "C++": """
- Use 4 spaces for indentation
- Include necessary headers
- Use proper braces
- Example:
  #include <string>
  #include <algorithm>
  
  bool isPalindrome(string s) {
      string reversed = s;
      reverse(reversed.begin(), reversed.end());
      return s == reversed;
  }"""
        }
        
        format_instructions = formatting_rules.get(language, formatting_rules["Python"])
        
        # Attempt generation with retries
        for attempt in range(1, max_retries + 1):
            try:
                # Log attempt
                print(f"Challenge generation attempt {attempt}/{max_retries} for topic: {topic}")
                
                # Use simplified prompt on retry
                if attempt > 1:
                    challenge_data = self._generate_with_simplified_prompt(topic, difficulty, language, format_instructions)
                else:
                    challenge_data = self._generate_with_full_prompt(topic, difficulty, language, format_instructions)
                
                # Validate response
                if challenge_data and self._validate_challenge_structure(challenge_data):
                    print(f"✅ Challenge generated successfully on attempt {attempt}")
                    return challenge_data
                else:
                    print(f"⚠️ Attempt {attempt} failed validation")
                    
            except json.JSONDecodeError as e:
                print(f"❌ Attempt {attempt} - JSON parsing error: {e}")
            except Exception as e:
                print(f"❌ Attempt {attempt} - Error: {e}")
            
            # Wait before retry (exponential backoff)
            if attempt < max_retries:
                import time
                wait_time = 2 ** attempt  # 2, 4, 8 seconds
                print(f"⏳ Waiting {wait_time}s before retry...")
                time.sleep(wait_time)
        
        # All retries failed - use fallback
        print(f"⚠️ All {max_retries} attempts failed. Using fallback challenge.")
        return self._get_fallback_challenge(topic, difficulty, language)
    
    def _generate_with_full_prompt(self, topic: str, difficulty: str, language: str, format_instructions: str):
        """Generate challenge with full detailed prompt"""
        try:
            prompt = f"""Generate a coding challenge for: {topic}
Difficulty: {difficulty}
Language: {language}

Return ONLY valid JSON in this exact format:
{{
  "title": "Challenge title",
  "description": "Clear problem description with examples",
  "difficulty": "{difficulty}",
  "language": "{language}",
  "starter_code": "Function signature or starter code",
  "solution_code": "Working solution",
  "test_cases": [
    {{"input": "\\"test string\\"", "expected": "true"}},
    {{"input": "\\"another test\\"", "expected": "false"}},
    {{"input": "123", "expected": "456"}},
    {{"input": "[1, 2, 3]", "expected": "[3, 2, 1]"}},
    {{"input": "(5, 3)", "expected": "8"}}
  ],
  "hints": ["Hint 1", "Hint 2", "Hint 3"]
}}

CRITICAL FORMATTING REQUIREMENTS FOR {language}:
{format_instructions}

CRITICAL REQUIREMENTS FOR TEST CASES:
1. String inputs MUST be wrapped in escaped quotes: "\\"text\\"" not "text"
2. Number inputs should be plain: "123" not "\\"123\\""
3. List/array inputs: "[1, 2, 3]"
4. Tuple inputs for multiple parameters: "(5, 3)" for func(a, b)
5. Boolean outputs: "True" or "False" (Python) or "true"/"false" (JavaScript)

IMPORTANT CODE STRUCTURE RULES:
- NEVER generate single-line compressed code
- ALWAYS use proper multi-line formatting
- Use clear indentation (4 spaces for Python/Java/C++, 2 for JavaScript)
- Make code educational and readable
- Avoid overly clever one-liners
- Prioritize clarity over brevity

Example test cases for is_palindrome function:
{{"input": "\\"madam\\"", "expected": "True"}}
{{"input": "\\"hello\\"", "expected": "False"}}
{{"input": "\\"a\\"", "expected": "True"}}

Example test cases for add(a, b) function with multiple parameters:
{{"input": "(5, 3)", "expected": "8"}}
{{"input": "(10, 2)", "expected": "12"}}

Requirements:
- Clear problem statement with examples
- 5 test cases minimum
- Starter code with function signature only (no implementation)
- Working solution that passes all tests (properly formatted)
- 3 helpful hints
- Return ONLY JSON, no markdown or code blocks"""

            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": f"You are a coding challenge generator. Generate PROPERLY FORMATTED {language} code with clear multi-line structure. Return ONLY valid JSON with properly escaped strings in test cases."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2500,
                timeout=30  # 30 second timeout
            )
            
            content = response.choices[0].message.content.strip()
            
            # Clean markdown if present
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()
            
            challenge_data = json.loads(content)
            
            # Validate and fix test cases format
            if 'test_cases' in challenge_data:
                challenge_data['test_cases'] = self._validate_test_cases(challenge_data['test_cases'])
            
            # Extract expected function name for validation
            if 'starter_code' in challenge_data:
                challenge_data['expected_function'] = self._extract_function_name_from_challenge(
                    challenge_data['starter_code']
                )
            
            return challenge_data
            
        except Exception as e:
            print(f"Full prompt generation error: {e}")
            return None
    
    def _generate_with_simplified_prompt(self, topic: str, difficulty: str, language: str, format_instructions: str):
        """Generate challenge with simplified prompt (used on retry)"""
        try:
            simplified_prompt = f"""Create a {difficulty} coding challenge about {topic} in {language}.

Return ONLY this JSON structure (no markdown):
{{
  "title": "Challenge title",
  "description": "Problem description",
  "difficulty": "{difficulty}",
  "language": "{language}",
  "starter_code": "Function signature",
  "solution_code": "Working solution",
  "test_cases": [
    {{"input": "test_input", "expected": "expected_output"}}
  ],
  "hints": ["Hint 1", "Hint 2", "Hint 3"]
}}

Format code properly:
{format_instructions}

Return ONLY valid JSON."""

            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": f"Return ONLY valid JSON. No markdown, no explanations."},
                    {"role": "user", "content": simplified_prompt}
                ],
                temperature=0.5,  # Lower temperature for more consistent output
                max_tokens=2000,
                timeout=30
            )
            
            content = response.choices[0].message.content.strip()
            
            # Clean markdown if present
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()
            
            challenge_data = json.loads(content)
            
            # Validate and fix test cases format
            if 'test_cases' in challenge_data:
                challenge_data['test_cases'] = self._validate_test_cases(challenge_data['test_cases'])
            
            # Extract expected function name for validation
            if 'starter_code' in challenge_data:
                challenge_data['expected_function'] = self._extract_function_name_from_challenge(
                    challenge_data['starter_code']
                )
            
            return challenge_data
            
        except Exception as e:
            print(f"Simplified prompt generation error: {e}")
            return None
    
    def _validate_challenge_structure(self, challenge_data: dict) -> bool:
        """
        Validate that challenge has all required fields
        
        Required fields:
        - title
        - description
        - difficulty
        - language
        - starter_code
        - solution_code
        - test_cases (list with at least 3 items)
        - hints (list with at least 2 items)
        """
        required_fields = [
            'title', 'description', 'difficulty', 'language',
            'starter_code', 'solution_code', 'test_cases', 'hints'
        ]
        
        # Check all required fields exist
        for field in required_fields:
            if field not in challenge_data:
                print(f"❌ Validation failed: Missing field '{field}'")
                return False
            
            # Check field is not empty
            if not challenge_data[field]:
                print(f"❌ Validation failed: Field '{field}' is empty")
                return False
        
        # Validate test_cases structure
        if not isinstance(challenge_data['test_cases'], list):
            print(f"❌ Validation failed: test_cases must be a list")
            return False
        
        if len(challenge_data['test_cases']) < 3:
            print(f"❌ Validation failed: Need at least 3 test cases, got {len(challenge_data['test_cases'])}")
            return False
        
        # Validate each test case has input and expected
        for i, test in enumerate(challenge_data['test_cases']):
            if 'input' not in test or 'expected' not in test:
                print(f"❌ Validation failed: Test case {i+1} missing 'input' or 'expected'")
                return False
        
        # Validate hints structure
        if not isinstance(challenge_data['hints'], list):
            print(f"❌ Validation failed: hints must be a list")
            return False
        
        if len(challenge_data['hints']) < 2:
            print(f"❌ Validation failed: Need at least 2 hints, got {len(challenge_data['hints'])}")
            return False
        
        print(f"✅ Challenge structure validation passed")
        return True
    
    def _get_fallback_challenge(self, topic: str, difficulty: str, language: str) -> dict:
        """
        Generate a fallback challenge when AI generation fails
        Returns a working challenge based on common patterns
        """
        print(f"🔄 Generating fallback challenge for topic: {topic}")
        
        # Fallback challenges by topic pattern
        fallback_templates = {
            "palindrome": self._fallback_palindrome,
            "reverse": self._fallback_reverse,
            "sum": self._fallback_sum,
            "array": self._fallback_array,
            "string": self._fallback_string,
            "list": self._fallback_list,
            "number": self._fallback_number,
            "sort": self._fallback_sort,
            "search": self._fallback_search,
        }
        
        # Find matching template
        topic_lower = topic.lower()
        for key, template_func in fallback_templates.items():
            if key in topic_lower:
                return template_func(difficulty, language)
        
        # Default fallback if no match
        return self._fallback_palindrome(difficulty, language)
    
    def _fallback_palindrome(self, difficulty: str, language: str) -> dict:
        """Fallback palindrome challenge"""
        if language == "Python":
            starter = "def is_palindrome(s: str) -> bool:\n    # Your code here\n    pass"
            solution = "def is_palindrome(s: str) -> bool:\n    return s == s[::-1]"
        elif language == "JavaScript":
            starter = "function isPalindrome(s) {\n    // Your code here\n}"
            solution = "function isPalindrome(s) {\n    const reversed = s.split('').reverse().join('');\n    return s === reversed;\n}"
        elif language == "Java":
            starter = "public class Solution {\n    public static boolean isPalindrome(String s) {\n        // Your code here\n        return false;\n    }\n}"
            solution = "public class Solution {\n    public static boolean isPalindrome(String s) {\n        String reversed = new StringBuilder(s).reverse().toString();\n        return s.equals(reversed);\n    }\n}"
        else:
            starter = "bool isPalindrome(string s) {\n    // Your code here\n    return false;\n}"
            solution = "bool isPalindrome(string s) {\n    string reversed = s;\n    reverse(reversed.begin(), reversed.end());\n    return s == reversed;\n}"
        
        return {
            'title': 'Check if String is Palindrome',
            'description': 'Write a function that checks if a given string is a palindrome. A palindrome is a word, phrase, or sequence that reads the same backward as forward.\n\nExample:\nInput: "madam"\nOutput: True\n\nInput: "hello"\nOutput: False',
            'difficulty': difficulty,
            'language': language,
            'starter_code': starter,
            'solution_code': solution,
            'test_cases': [
                {'input': '"madam"', 'expected': 'True'},
                {'input': '"hello"', 'expected': 'False'},
                {'input': '"racecar"', 'expected': 'True'},
                {'input': '"a"', 'expected': 'True'},
                {'input': '"ab"', 'expected': 'False'}
            ],
            'hints': [
                'Try reversing the string and comparing it with the original',
                'You can use string slicing in Python: s[::-1]',
                'Consider edge cases like single character strings'
            ],
            'expected_function': 'is_palindrome' if language == 'Python' else 'isPalindrome'
        }
    
    def _fallback_reverse(self, difficulty: str, language: str) -> dict:
        """Fallback reverse string/list challenge"""
        if language == "Python":
            starter = "def reverse_string(s: str) -> str:\n    # Your code here\n    pass"
            solution = "def reverse_string(s: str) -> str:\n    return s[::-1]"
        else:
            starter = "function reverseString(s) {\n    // Your code here\n}"
            solution = "function reverseString(s) {\n    return s.split('').reverse().join('');\n}"
        
        return {
            'title': 'Reverse a String',
            'description': 'Write a function that reverses a given string.\n\nExample:\nInput: "hello"\nOutput: "olleh"',
            'difficulty': difficulty,
            'language': language,
            'starter_code': starter,
            'solution_code': solution,
            'test_cases': [
                {'input': '"hello"', 'expected': '"olleh"'},
                {'input': '"world"', 'expected': '"dlrow"'},
                {'input': '"a"', 'expected': '"a"'},
                {'input': '""', 'expected': '""'},
                {'input': '"12345"', 'expected': '"54321"'}
            ],
            'hints': [
                'Use string slicing or built-in reverse methods',
                'Consider iterating from the end to the beginning',
                'Think about edge cases like empty strings'
            ],
            'expected_function': 'reverse_string' if language == 'Python' else 'reverseString'
        }
    
    def _fallback_sum(self, difficulty: str, language: str) -> dict:
        """Fallback sum challenge"""
        if language == "Python":
            starter = "def sum_list(numbers: list) -> int:\n    # Your code here\n    pass"
            solution = "def sum_list(numbers: list) -> int:\n    return sum(numbers)"
        else:
            starter = "function sumList(numbers) {\n    // Your code here\n}"
            solution = "function sumList(numbers) {\n    return numbers.reduce((a, b) => a + b, 0);\n}"
        
        return {
            'title': 'Sum of List Elements',
            'description': 'Write a function that calculates the sum of all elements in a list.\n\nExample:\nInput: [1, 2, 3, 4, 5]\nOutput: 15',
            'difficulty': difficulty,
            'language': language,
            'starter_code': starter,
            'solution_code': solution,
            'test_cases': [
                {'input': '[1, 2, 3, 4, 5]', 'expected': '15'},
                {'input': '[10, 20, 30]', 'expected': '60'},
                {'input': '[0]', 'expected': '0'},
                {'input': '[-1, 1]', 'expected': '0'},
                {'input': '[100]', 'expected': '100'}
            ],
            'hints': [
                'Use a loop to iterate through the list',
                'Python has a built-in sum() function',
                'Initialize a variable to store the running total'
            ],
            'expected_function': 'sum_list' if language == 'Python' else 'sumList'
        }
    
    def _fallback_array(self, difficulty: str, language: str) -> dict:
        """Fallback array challenge"""
        return self._fallback_sum(difficulty, language)
    
    def _fallback_string(self, difficulty: str, language: str) -> dict:
        """Fallback string challenge"""
        return self._fallback_palindrome(difficulty, language)
    
    def _fallback_list(self, difficulty: str, language: str) -> dict:
        """Fallback list challenge"""
        return self._fallback_reverse(difficulty, language)
    
    def _fallback_number(self, difficulty: str, language: str) -> dict:
        """Fallback number challenge"""
        return self._fallback_sum(difficulty, language)
    
    def _fallback_sort(self, difficulty: str, language: str) -> dict:
        """Fallback sort challenge"""
        if language == "Python":
            starter = "def sort_list(numbers: list) -> list:\n    # Your code here\n    pass"
            solution = "def sort_list(numbers: list) -> list:\n    return sorted(numbers)"
        else:
            starter = "function sortList(numbers) {\n    // Your code here\n}"
            solution = "function sortList(numbers) {\n    return numbers.sort((a, b) => a - b);\n}"
        
        return {
            'title': 'Sort a List',
            'description': 'Write a function that sorts a list of numbers in ascending order.\n\nExample:\nInput: [3, 1, 4, 1, 5]\nOutput: [1, 1, 3, 4, 5]',
            'difficulty': difficulty,
            'language': language,
            'starter_code': starter,
            'solution_code': solution,
            'test_cases': [
                {'input': '[3, 1, 4, 1, 5]', 'expected': '[1, 1, 3, 4, 5]'},
                {'input': '[5, 4, 3, 2, 1]', 'expected': '[1, 2, 3, 4, 5]'},
                {'input': '[1]', 'expected': '[1]'},
                {'input': '[2, 2, 2]', 'expected': '[2, 2, 2]'},
                {'input': '[-1, 0, 1]', 'expected': '[-1, 0, 1]'}
            ],
            'hints': [
                'Use built-in sorting functions',
                'Consider the time complexity of different sorting algorithms',
                'Handle edge cases like empty lists or single elements'
            ],
            'expected_function': 'sort_list' if language == 'Python' else 'sortList'
        }
    
    def _fallback_search(self, difficulty: str, language: str) -> dict:
        """Fallback search challenge"""
        if language == "Python":
            starter = "def find_element(numbers: list, target: int) -> int:\n    # Your code here\n    pass"
            solution = "def find_element(numbers: list, target: int) -> int:\n    return numbers.index(target) if target in numbers else -1"
        else:
            starter = "function findElement(numbers, target) {\n    // Your code here\n}"
            solution = "function findElement(numbers, target) {\n    const index = numbers.indexOf(target);\n    return index !== -1 ? index : -1;\n}"
        
        return {
            'title': 'Find Element in List',
            'description': 'Write a function that finds the index of a target element in a list. Return -1 if not found.\n\nExample:\nInput: [1, 2, 3, 4, 5], target=3\nOutput: 2',
            'difficulty': difficulty,
            'language': language,
            'starter_code': starter,
            'solution_code': solution,
            'test_cases': [
                {'input': '([1, 2, 3, 4, 5], 3)', 'expected': '2'},
                {'input': '([10, 20, 30], 20)', 'expected': '1'},
                {'input': '([5, 5, 5], 5)', 'expected': '0'},
                {'input': '([1, 2, 3], 10)', 'expected': '-1'},
                {'input': '([100], 100)', 'expected': '0'}
            ],
            'hints': [
                'Use a loop to check each element',
                'Return the index when you find the target',
                'Return -1 if you reach the end without finding it'
            ],
            'expected_function': 'find_element' if language == 'Python' else 'findElement'
        }
    
    def _validate_test_cases(self, test_cases: list) -> list:
        """
        Validate and fix test case formatting
        Ensures inputs are properly formatted for execution
        """
        validated = []
        
        for test in test_cases:
            if 'input' not in test or 'expected' not in test:
                continue
            
            # Keep test cases as-is since _safe_parse_input will handle them
            validated.append({
                'input': test['input'],
                'expected': test['expected']
            })
        
        return validated
    
    def save_challenge(self, challenge_data: dict) -> int:
        """Save challenge to database"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO challenges 
                (title, description, difficulty, language, starter_code, solution_code, test_cases, hints)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                challenge_data['title'],
                challenge_data['description'],
                challenge_data['difficulty'],
                challenge_data['language'],
                challenge_data['starter_code'],
                challenge_data['solution_code'],
                json.dumps(challenge_data['test_cases']),
                json.dumps(challenge_data['hints'])
            ))
            
            challenge_id = cursor.lastrowid
            conn.commit()
            return challenge_id
            
        except Exception as e:
            print(f"Error saving challenge: {e}")
            return None
        finally:
            conn.close()
    
    def get_challenge(self, challenge_id: int) -> dict:
        """Get challenge by ID"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT id, title, description, difficulty, language, 
                       starter_code, solution_code, test_cases, hints
                FROM challenges
                WHERE id = ?
            """, (challenge_id,))
            
            row = cursor.fetchone()
            
            if row:
                return {
                    'id': row[0],
                    'title': row[1],
                    'description': row[2],
                    'difficulty': row[3],
                    'language': row[4],
                    'starter_code': row[5],
                    'solution_code': row[6],
                    'test_cases': json.loads(row[7]),
                    'hints': json.loads(row[8])
                }
            return None
            
        except Exception as e:
            print(f"Error getting challenge: {e}")
            return None
        finally:
            conn.close()
    
    def get_challenges_by_difficulty(self, difficulty: str, limit: int = 10):
        """Get challenges by difficulty level"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT id, title, description, difficulty, language
                FROM challenges
                WHERE difficulty = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (difficulty, limit))
            
            challenges = []
            for row in cursor.fetchall():
                challenges.append({
                    'id': row[0],
                    'title': row[1],
                    'description': row[2],
                    'difficulty': row[3],
                    'language': row[4]
                })
            
            return challenges
            
        except Exception as e:
            print(f"Error getting challenges: {e}")
            return []
        finally:
            conn.close()
    
    def submit_solution(self, user_id: int, challenge_id: int, code: str, passed: bool, execution_time: float = 0):
        """Submit a solution"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        try:
            # Save submission
            cursor.execute("""
                INSERT INTO submissions (user_id, challenge_id, code, passed, execution_time)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, challenge_id, code, 1 if passed else 0, execution_time))
            
            # Update user progress
            cursor.execute("""
                INSERT INTO user_progress (user_id, challenge_id, completed, attempts, best_time, completed_at)
                VALUES (?, ?, ?, 1, ?, ?)
                ON CONFLICT(user_id, challenge_id) DO UPDATE SET
                    attempts = attempts + 1,
                    completed = CASE WHEN ? THEN 1 ELSE completed END,
                    best_time = CASE WHEN ? AND (best_time IS NULL OR ? < best_time) THEN ? ELSE best_time END,
                    completed_at = CASE WHEN ? THEN ? ELSE completed_at END
            """, (
                user_id, challenge_id, 1 if passed else 0, execution_time, datetime.now(),
                passed, passed, execution_time, execution_time,
                passed, datetime.now()
            ))
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"Error submitting solution: {e}")
            return False
        finally:
            conn.close()
    
    def get_user_stats(self, user_id: int) -> dict:
        """Get user coding challenge statistics"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        try:
            # Total completed
            cursor.execute("""
                SELECT COUNT(*) FROM user_progress
                WHERE user_id = ? AND completed = 1
            """, (user_id,))
            completed = cursor.fetchone()[0]
            
            # Total attempts
            cursor.execute("""
                SELECT SUM(attempts) FROM user_progress
                WHERE user_id = ?
            """, (user_id,))
            attempts = cursor.fetchone()[0] or 0
            
            # By difficulty
            cursor.execute("""
                SELECT c.difficulty, COUNT(*) 
                FROM user_progress up
                JOIN challenges c ON up.challenge_id = c.id
                WHERE up.user_id = ? AND up.completed = 1
                GROUP BY c.difficulty
            """, (user_id,))
            
            by_difficulty = {row[0]: row[1] for row in cursor.fetchall()}
            
            return {
                'completed': completed,
                'attempts': attempts,
                'easy': by_difficulty.get('Easy', 0),
                'medium': by_difficulty.get('Medium', 0),
                'hard': by_difficulty.get('Hard', 0)
            }
            
        except Exception as e:
            print(f"Error getting user stats: {e}")
            return {'completed': 0, 'attempts': 0, 'easy': 0, 'medium': 0, 'hard': 0}
        finally:
            conn.close()
    
    def _safe_parse_input(self, input_str: str):
        """
        Safely parse test input with proper type detection
        Handles strings, numbers, lists, tuples, booleans, etc.
        """
        # Remove extra whitespace
        input_str = input_str.strip()
        
        # Try to evaluate as Python literal
        try:
            # Use ast.literal_eval for safe evaluation
            import ast
            return ast.literal_eval(input_str)
        except (ValueError, SyntaxError):
            # If it fails, treat as string
            # Remove quotes if already present
            if (input_str.startswith('"') and input_str.endswith('"')) or \
               (input_str.startswith("'") and input_str.endswith("'")):
                return input_str[1:-1]
            # Return as string
            return input_str
    
    def _extract_top_level_functions(self, code: str) -> list:
        """
        Extract only top-level function names using AST parsing
        Ignores class methods like __init__, __str__, etc.
        """
        import ast
        
        try:
            tree = ast.parse(code)
            functions = []
            
            for node in ast.walk(tree):
                # Only get top-level function definitions
                if isinstance(node, ast.FunctionDef):
                    # Check if it's a top-level function (not inside a class)
                    # by checking if parent is Module
                    for parent in ast.walk(tree):
                        if isinstance(parent, ast.Module):
                            if node in parent.body:
                                # Exclude dunder methods
                                if not node.name.startswith('__'):
                                    functions.append(node.name)
            
            return functions
        except Exception as e:
            print(f"AST parsing error: {e}")
            return []
    
    def _extract_function_name_from_challenge(self, starter_code: str) -> str:
        """
        Extract the main function name from starter code
        Uses AST to find the primary function (not class methods)
        """
        functions = self._extract_top_level_functions(starter_code)
        
        if functions:
            # Return the first top-level function
            return functions[0]
        
        # Fallback to regex (but exclude __init__ and other dunder methods)
        import re
        func_match = re.search(r'def\s+(?!__\w+__)(\w+)\s*\(', starter_code)
        if func_match:
            return func_match.group(1)
        
        return None
    
    def validate_code(self, code: str, test_cases: list, language: str = "Python", expected_function: str = None) -> dict:
        """
        Validate code against test cases with multi-language support
        
        Supports:
        - Python (local execution)
        - Java (subprocess with javac/java)
        - JavaScript (subprocess with Node.js)
        
        Args:
            code: User's solution code
            test_cases: List of test cases
            language: Programming language
            expected_function: Expected function name (optional)
        """
        # Use multi-language executor for all languages
        from utils.multi_language_executor import get_multi_language_executor
        
        executor = get_multi_language_executor()
        return executor.execute_with_tests(code, test_cases, language, expected_function)


def get_coding_system():
    """Get coding challenge system instance"""
    return CodingChallengeSystem()
