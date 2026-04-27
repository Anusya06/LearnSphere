# 💻 Interactive Code Playground Guide

## Overview

The Code Playground is an advanced feature that transforms the Learn tab into an interactive multi-language coding environment. Users can generate, edit, and execute code in 5 programming languages directly within the platform.

## Supported Languages

1. **🐍 Python** - Executed locally with safety restrictions
2. **⚙️ C** - Executed via Piston API
3. **⚡ C++** - Executed via Piston API
4. **☕ Java** - Executed via Piston API
5. **🟨 JavaScript** - Executed via Piston API

## Features

### 1. Dynamic Multi-Language Code Generation

When you generate content for a topic, the AI automatically creates implementations in all 5 languages:

```
Topic: Binary Search
├── Python implementation
├── C implementation
├── C++ implementation
├── Java implementation
└── JavaScript implementation
```

Each implementation includes:
- Complete, runnable code
- Inline comments explaining logic
- Example usage/demo
- Proper imports/includes

### 2. Interactive Code Editor

Each language tab provides:
- **Editable code area** - Modify AI-generated code
- **Syntax highlighting** - Monospace font with proper formatting
- **Line numbers** - Easy code navigation
- **Auto-indentation** - Clean code structure

### 3. Code Execution

#### Python Execution (Local)
- Runs directly in the Streamlit app
- Safety restrictions prevent dangerous operations
- Instant execution with no API calls
- Supports: print, input, basic data structures, math operations

#### Other Languages (Piston API)
- C, C++, Java, JavaScript run via free Piston API
- Automatic compilation (for compiled languages)
- Execution with timeout protection
- Memory limit enforcement

### 4. Input Support

Programs requiring user input can use the **Program Input** section:
- Expandable input box
- Multi-line input support
- One value per line
- Automatically passed to stdin

Example:
```
Input:
5
10
15
```

### 5. Output Display

After execution, you'll see:
- **Success/Error indicator** with execution time
- **Output section** showing program stdout
- **Error section** showing compilation/runtime errors
- **Execution details** with language, time, and status

### 6. Code Management

Each editor provides:
- **▶️ Run Code** - Execute the current code
- **🔄 Reset** - Restore original AI-generated code
- **📥 Download** - Save code to your computer

### 7. Analytics Tracking

Every code execution is tracked:
- Topic being studied
- Language used
- Execution time
- Success/failure status
- Error messages (if any)

Access your coding stats in the Analytics tab.

## How to Use

### Step 1: Generate Content
1. Go to the Learn tab
2. Enter a topic (e.g., "Binary Search", "Neural Networks")
3. Select difficulty and depth
4. Click **🚀 Generate Content**

### Step 2: Navigate to Code Tab
1. Click the **💻 Code** tab
2. You'll see language tabs: Python | C | C++ | Java | JavaScript

### Step 3: Select Language
Click on any language tab to view its implementation

### Step 4: Edit Code (Optional)
Modify the code in the editor as needed

### Step 5: Add Input (If Needed)
If your program needs input:
1. Expand **📥 Program Input**
2. Enter values (one per line)

### Step 6: Run Code
1. Click **▶️ Run Code**
2. Wait for execution (usually 1-3 seconds)
3. View output and errors

### Step 7: Iterate
- Modify code and run again
- Try different languages
- Download working solutions

## Example Workflow

### Topic: Bubble Sort

**Generated Code (Python):**
```python
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr

# Example
numbers = [64, 34, 25, 12, 22, 11, 90]
print("Original:", numbers)
sorted_numbers = bubble_sort(numbers)
print("Sorted:", sorted_numbers)
```

**User Actions:**
1. Click **▶️ Run Code**
2. See output:
   ```
   Original: [64, 34, 25, 12, 22, 11, 90]
   Sorted: [11, 12, 22, 25, 34, 64, 90]
   ```
3. Switch to C++ tab
4. Run C++ version
5. Compare implementations

## Security Features

### Python (Local Execution)
- Restricted built-ins (no file I/O, no imports, no eval)
- Safe functions only: print, len, range, basic types
- No access to system resources
- Execution timeout protection

### External Languages (Piston API)
- Sandboxed execution environment
- Compile timeout: 10 seconds
- Run timeout: 3 seconds
- Memory limits enforced
- No network access
- No file system access

## Error Handling

### Compilation Errors (C/C++/Java)
```
❌ Execution failed after 0.234s

⚠️ Error:
Compilation Error:
main.cpp:5:1: error: expected ';' before '}' token
```

### Runtime Errors
```
❌ Execution failed after 0.156s

⚠️ Error:
Runtime Error:
ZeroDivisionError: division by zero
```

### Timeout Errors
```
❌ Execution failed after 3.001s

⚠️ Error:
Execution timeout - code took too long to run
```

## Best Practices

1. **Start Simple** - Test with basic examples first
2. **Add Comments** - Document your modifications
3. **Use Input Wisely** - Provide sample input for testing
4. **Check All Languages** - Compare different implementations
5. **Download Solutions** - Save working code for reference
6. **Learn from Errors** - Read error messages carefully

## Troubleshooting

### Code Won't Run
- Check for syntax errors
- Ensure all brackets/parentheses are closed
- Verify input format matches program expectations

### Timeout Errors
- Simplify algorithm
- Reduce input size
- Avoid infinite loops

### API Errors
- Wait a moment and try again
- Check internet connection
- Piston API may be temporarily unavailable

### No Output
- Ensure code has print statements
- Check if program expects input
- Verify logic is correct

## Technical Details

### Architecture
```
User Input → Code Editor → Execution Engine
                              ├── Python: Local exec()
                              └── Others: Piston API
                                    ↓
                              Output Display
                                    ↓
                              Analytics Storage
```

### API Endpoints
- **Piston API**: https://emkc.org/api/v2/piston/execute
- **Rate Limits**: Generous free tier
- **Timeout**: 15 seconds per request

### Storage
Code execution data stored in session state:
```python
{
    "topic": "Binary Search",
    "language": "python",
    "execution_time": 0.123,
    "success": True,
    "error_msg": None,
    "timestamp": "2026-03-06T10:30:00"
}
```

## Future Enhancements

Planned features:
- [ ] More languages (Rust, Go, TypeScript)
- [ ] Code sharing and collaboration
- [ ] Test case generation
- [ ] Performance benchmarking
- [ ] Code quality analysis
- [ ] Syntax error highlighting
- [ ] Auto-completion
- [ ] Code templates library

## Support

For issues or questions:
1. Check error messages carefully
2. Review this guide
3. Try regenerating content
4. Test with simpler code first

---

**Happy Coding! 🚀**
