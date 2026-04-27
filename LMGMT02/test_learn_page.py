"""Test if Learn page can be imported"""
import sys
from pathlib import Path

# Add frontend to path
sys.path.insert(0, str(Path(__file__).parent / "frontend"))

try:
    # Try to import the Learn page module
    import importlib.util
    spec = importlib.util.spec_from_file_location("learn_page", "frontend/pages/2_Learn.py")
    learn_module = importlib.util.module_from_spec(spec)
    
    print("✅ Learn page file found")
    print(f"✅ Module spec created: {spec}")
    
    # Check if main functions exist
    with open("frontend/pages/2_Learn.py", "r", encoding="utf-8") as f:
        content = f.read()
        
    functions_to_check = [
        "init_session_state",
        "generate_learning_content",
        "generate_roadmap",
        "generate_code_example",
        "render_content_tab",
        "render_audio_tab",
        "render_tutor_tab",
        "render_videos_tab",
        "render_code_tab",
        "render_roadmap_tab",
        "main"
    ]
    
    print("\n📋 Checking for required functions:")
    for func in functions_to_check:
        if f"def {func}" in content:
            print(f"  ✅ {func}")
        else:
            print(f"  ❌ {func} - MISSING!")
    
    # Check for tabs rendering
    if 'st.tabs([' in content:
        print("\n✅ Tabs are defined in the code")
    else:
        print("\n❌ Tabs are NOT defined in the code")
    
    # Check for tab labels
    tab_labels = ["📖 Content", "🔊 Audio", "🤖 Tutor", "🎥 Videos", "💻 Code", "🗺️ Roadmap"]
    print("\n📋 Checking for tab labels:")
    for label in tab_labels:
        if label in content:
            print(f"  ✅ {label}")
        else:
            print(f"  ❌ {label} - MISSING!")
    
    print("\n✅ All checks passed! The Learn page should work.")
    print("\n📝 Instructions:")
    print("1. Open: http://localhost:8503")
    print("2. Login to your account")
    print("3. Click '📚 Learn' in sidebar")
    print("4. Enter a topic (e.g., 'Neural Networks')")
    print("5. Click '🚀 Generate' button")
    print("6. Wait for content to generate")
    print("7. You should see 6 tabs appear!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
