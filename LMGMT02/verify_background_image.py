"""
Verify background image exists and can be loaded
"""
import os
import base64
from pathlib import Path

print("=" * 60)
print("BACKGROUND IMAGE VERIFICATION")
print("=" * 60)

# Get current working directory
cwd = Path.cwd()
print(f"Current directory: {cwd}")

# Check assets folder
assets_path = cwd / "assets"
print(f"\nAssets folder: {assets_path}")
print(f"Exists: {assets_path.exists()}")

if assets_path.exists():
    print("\nFiles in assets folder:")
    for file in assets_path.iterdir():
        if file.is_file():
            print(f"  - {file.name} ({file.stat().st_size:,} bytes)")

# Test loading learnsphere_bg.png
image_path = assets_path / "learnsphere_bg.png"
print(f"\nLooking for: {image_path}")
print(f"Exists: {image_path.exists()}")

if not image_path.exists():
    print("\nWARNING: learnsphere_bg.png not found!")
    print("Checking for learn_bg.png instead...")
    image_path = assets_path / "learn_bg.png"
    print(f"Path: {image_path}")
    print(f"Exists: {image_path.exists()}")

if image_path.exists():
    try:
        with open(image_path, "rb") as f:
            image_data = f.read()
            encoded = base64.b64encode(image_data).decode()
            print(f"\n✓ SUCCESS: Image loaded and encoded")
            print(f"  File size: {len(image_data):,} bytes")
            print(f"  Base64 length: {len(encoded):,} characters")
            print(f"  First 50 chars: {encoded[:50]}...")
    except Exception as e:
        print(f"\n✗ ERROR loading image: {e}")
else:
    print("\n✗ ERROR: No background image found!")
    print("Please ensure you have either:")
    print("  - assets/learnsphere_bg.png")
    print("  - assets/learn_bg.png")
    print("in your project directory.")

print("\n" + "=" * 60)
print("RECOMMENDATION:")
print("=" * 60)
print("1. Make sure you have the image file in assets/ folder")
print("2. Restart Streamlit server after making changes")
print("3. Use Ctrl+Shift+R to hard refresh browser")
print("=" * 60)