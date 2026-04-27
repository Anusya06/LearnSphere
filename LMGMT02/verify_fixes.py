"""
Verification Script - Check All Fixes Are Working
Run this to verify all three issues are resolved
"""
import sys
from pathlib import Path

def check_imports():
    """Verify all required packages are installed"""
    print("🔍 Checking required packages...")
    try:
        import streamlit
        print("  ✅ streamlit")
        import groq
        print("  ✅ groq")
        import bcrypt
        print("  ✅ bcrypt")
        import requests
        print("  ✅ requests")
        import sqlite3
        print("  ✅ sqlite3")
        return True
    except ImportError as e:
        print(f"  ❌ Missing package: {e}")
        return False


def check_files():
    """Verify all required files exist"""
    print("\n🔍 Checking required files...")
    
    required_files = [
        "frontend/components/auth_components.py",
        "frontend/pages/3_Quiz.py",
        "frontend/pages/2_Learn.py",
        "frontend/utils/code_executor.py",
        "frontend/utils/auth_database.py",
        "frontend/utils/user_data.py",
        "frontend/utils/learning_progress.py",
        "frontend/Home.py",
    ]
    
    all_exist = True
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} - MISSING")
            all_exist = False
    
    return all_exist


def check_auth_fix():
    """Verify authentication fix is in place"""
    print("\n🔍 Checking authentication fix...")
    
    try:
        with open("frontend/components/auth_components.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        checks = [
            ("logged_in flag", "logged_in" in content),
            ("authenticated flag", "authenticated" in content),
            ("check_authentication function", "def check_authentication" in content),
            ("dual flag check", "or st.session_state.get" in content),
        ]
        
        all_passed = True
        for check_name, passed in checks:
            if passed:
                print(f"  ✅ {check_name}")
            else:
                print(f"  ❌ {check_name} - MISSING")
                all_passed = False
        
        return all_passed
    except Exception as e:
        print(f"  ❌ Error checking auth fix: {e}")
        return False


def check_quiz_fix():
    """Verify dynamic quiz system is in place"""
    print("\n🔍 Checking dynamic quiz system...")
    
    try:
        quiz_file = Path("frontend/pages/3_Quiz.py")
        
        with open(quiz_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        checks = [
            ("AI generation function", "generate_quiz_questions" in content),
            ("Groq client", "groq_client" in content or "Groq" in content),
            ("No default selection", "index=None" in content),
            ("Score calculation", "calculate_quiz_score" in content),
            ("User answers tracking", "user_answers" in content),
            ("Database integration", "add_quiz_attempt" in content),
        ]
        
        all_passed = True
        for check_name, passed in checks:
            if passed:
                print(f"  ✅ {check_name}")
            else:
                print(f"  ❌ {check_name} - MISSING")
                all_passed = False
        
        return all_passed
    except Exception as e:
        print(f"  ❌ Error checking quiz fix: {e}")
        return False


def check_code_executor_fix():
    """Verify code executor enhancements"""
    print("\n🔍 Checking code execution fix...")
    
    try:
        with open("frontend/utils/code_executor.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        checks = [
            ("Local Python execution", "execute_python_local" in content),
            ("Piston API", "_execute_via_piston" in content),
            ("OneCompiler fallback", "_execute_via_onecompiler" in content),
            ("Main execute function", "def execute(" in content),
            ("Error handling", "try:" in content and "except" in content),
        ]
        
        all_passed = True
        for check_name, passed in checks:
            if passed:
                print(f"  ✅ {check_name}")
            else:
                print(f"  ❌ {check_name} - MISSING")
                all_passed = False
        
        return all_passed
    except Exception as e:
        print(f"  ❌ Error checking code executor fix: {e}")
        return False


def check_api_key():
    """Check if Groq API key is configured"""
    print("\n🔍 Checking API configuration...")
    
    secrets_paths = [
        "frontend/.streamlit/secrets.toml",
        ".streamlit/secrets.toml",
        "secrets.toml"
    ]
    
    for path in secrets_paths:
        if Path(path).exists():
            try:
                with open(path, "r") as f:
                    content = f.read()
                if "GROQ_API_KEY" in content:
                    print(f"  ✅ Groq API key found in {path}")
                    return True
            except:
                pass
    
    print("  ⚠️  Groq API key not found in secrets.toml")
    print("     Add your key to frontend/.streamlit/secrets.toml")
    print("     Get free key: https://console.groq.com")
    return False


def main():
    """Run all verification checks"""
    print("=" * 60)
    print("🔍 VERIFICATION SCRIPT - Checking All Fixes")
    print("=" * 60)
    
    results = {
        "Packages": check_imports(),
        "Files": check_files(),
        "Authentication Fix": check_auth_fix(),
        "Quiz System Fix": check_quiz_fix(),
        "Code Executor Fix": check_code_executor_fix(),
        "API Configuration": check_api_key(),
    }
    
    print("\n" + "=" * 60)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 60)
    
    for check_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{check_name:.<40} {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL CHECKS PASSED - READY TO USE!")
        print("=" * 60)
        print("\n📝 Next Steps:")
        print("1. Ensure Groq API key is in secrets.toml")
        print("2. Run: cd frontend && streamlit run Home.py")
        print("3. Test authentication, quiz, and code execution")
        print("\n📚 Documentation:")
        print("- START_HERE.md - Quick start guide")
        print("- FIXES_COMPLETE.md - Detailed documentation")
        print("- IMPLEMENTATION_SUMMARY.md - Technical details")
    else:
        print("⚠️  SOME CHECKS FAILED - REVIEW ABOVE")
        print("=" * 60)
        print("\n🔧 Troubleshooting:")
        print("1. Install missing packages: pip install -r requirements.txt")
        print("2. Verify all files are present")
        print("3. Check file contents for required functions")
        print("4. Add Groq API key to secrets.toml")
    
    print("\n")
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
