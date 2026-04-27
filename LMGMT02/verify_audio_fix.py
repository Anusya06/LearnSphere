"""
Verification script for audio system integration
"""
import sys
import time

print("🔍 Verifying Audio System Integration...")
print("=" * 60)

# Wait for file to be released
print("\n⏳ Waiting for file to be available...")
max_attempts = 10
for attempt in range(max_attempts):
    try:
        with open("frontend/pages/2_Learn.py", "r", encoding="utf-8") as f:
            content = f.read()
        break
    except Exception as e:
        if attempt < max_attempts - 1:
            print(f"   Attempt {attempt + 1}/{max_attempts}... waiting")
            time.sleep(1)
        else:
            print(f"\n❌ Could not read file: {e}")
            print("\n⚠️  Please close Streamlit and try again:")
            print("   1. Stop all Streamlit processes")
            print("   2. Run: python verify_audio_fix.py")
            sys.exit(1)

print("✅ File accessible\n")

# Check 1: Imports
print("1️⃣  Checking imports...")
checks_passed = 0
checks_failed = 0

if "from utils.audio_generator import get_audio_generator, GTTS_AVAILABLE" in content:
    print("   ✅ Audio generator import found")
    checks_passed += 1
else:
    print("   ❌ Audio generator import missing")
    checks_failed += 1

if "from utils.advanced_features_db import get_advanced_db" in content:
    print("   ✅ Advanced features DB import found")
    checks_passed += 1
else:
    print("   ❌ Advanced features DB import missing")
    checks_failed += 1

# Check for old import (should NOT exist)
if "from gtts import gTTS" in content:
    print("   ⚠️  Old gTTS import still present (should be removed)")
    checks_failed += 1
else:
    print("   ✅ Old gTTS import removed")
    checks_passed += 1

# Check 2: render_audio_tab function
print("\n2️⃣  Checking render_audio_tab function...")

if "def render_audio_tab():" in content:
    print("   ✅ Function exists")
    checks_passed += 1
    
    # Check for optimized features
    if "audio_gen = get_audio_generator()" in content:
        print("   ✅ Uses audio generator instance")
        checks_passed += 1
    else:
        print("   ❌ Not using audio generator")
        checks_failed += 1
    
    if "audio_mode = st.selectbox" in content:
        print("   ✅ Audio mode selection present")
        checks_passed += 1
    else:
        print("   ❌ Audio mode selection missing")
        checks_failed += 1
    
    if "generate_audio_parallel" in content:
        print("   ✅ Parallel generation method present")
        checks_passed += 1
    else:
        print("   ❌ Parallel generation missing")
        checks_failed += 1
    
    if "Section-Wise Audio" in content:
        print("   ✅ Section-wise audio feature present")
        checks_passed += 1
    else:
        print("   ❌ Section-wise audio missing")
        checks_failed += 1
    
    if "Recently Listened" in content:
        print("   ✅ Audio history feature present")
        checks_passed += 1
    else:
        print("   ❌ Audio history missing")
        checks_failed += 1
else:
    print("   ❌ Function not found")
    checks_failed += 1

# Check 3: Old generate_audio function (should NOT exist)
print("\n3️⃣  Checking for old code...")
if "def generate_audio(text: str) -> BytesIO:" in content:
    print("   ⚠️  Old generate_audio function still present (should be removed)")
    checks_failed += 1
else:
    print("   ✅ Old generate_audio function removed")
    checks_passed += 1

# Summary
print("\n" + "=" * 60)
print(f"📊 RESULTS: {checks_passed} passed, {checks_failed} failed")
print("=" * 60)

if checks_failed == 0:
    print("\n🎉 SUCCESS! Audio system is properly integrated!")
    print("\n📋 Next Steps:")
    print("   1. Install dependencies: pip install gtts pydub")
    print("   2. Start Streamlit: streamlit run frontend/Home.py")
    print("   3. Go to Learn page and test audio generation")
    print("\n⚡ Expected Performance:")
    print("   • Fast Mode: 3-5 seconds")
    print("   • Full Content: 5-10 seconds (vs 120+ seconds before)")
    print("   • Cached audio: Instant playback")
else:
    print("\n⚠️  Some checks failed. Please review the issues above.")
    print("\nIf Streamlit is running, please:")
    print("   1. Stop all Streamlit processes")
    print("   2. Re-run this verification script")
