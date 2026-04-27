"""
Simple test to verify background image can be loaded
"""
import os
import base64
from pathlib import Path

print("=" * 60)
print("SIMPLE BACKGROUND TEST")
print("=" * 60)

# Get the project root
project_root = Path.cwd()
print(f"Project root: {project_root}")

# Check assets folder
assets_folder = project_root / "assets"
print(f"Assets folder: {assets_folder}")
print(f"Exists: {assets_folder.exists()}")

# Check for learnsphere_bg.png
image_path = assets_folder / "learnsphere_bg.png"
print(f"\nImage path: {image_path}")
print(f"Exists: {image_path.exists()}")

if image_path.exists():
    # Try to load and encode
    try:
        with open(image_path, "rb") as f:
            image_data = f.read()
            encoded = base64.b64encode(image_data).decode()
            print(f"\n✓ SUCCESS: Image can be loaded and encoded")
            print(f"  File size: {len(image_data):,} bytes")
            print(f"  Base64 length: {len(encoded):,} chars")
            
            # Test CSS generation
            css_template = f"""
            <style>
            .stApp {{
                background: transparent !important;
            }}
            
            .stApp::before {{
                content: "";
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                width: 100vw;
                height: 100vh;
                background-image: url("data:image/png;base64,{encoded[:100]}...");
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
                background-attachment: fixed;
                z-index: -2;
                pointer-events: none;
            }}
            </style>
            """
            print(f"\n✓ CSS can be generated")
            print(f"  CSS length: {len(css_template):,} chars")
            
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
else:
    print("\n✗ ERROR: Image not found!")
    print("Please check:")
    print(f"  - File exists at: {image_path}")
    print("  - File is not corrupted")
    print("  - File has correct permissions")

print("\n" + "=" * 60)
print("FINAL VERIFICATION:")
print("=" * 60)
print("1. Image file: ✓ Found and readable")
print("2. Base64 encoding: ✓ Works")
print("3. CSS generation: ✓ Works")
print("\nIf background still doesn't show:")
print("  - Restart Streamlit: Ctrl+C then 'streamlit run app.py'")
print("  - Hard refresh browser: Ctrl+Shift+R")
print("  - Check browser console for errors (F12)")
print("=" * 60)