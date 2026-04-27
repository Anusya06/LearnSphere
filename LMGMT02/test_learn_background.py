"""
Diagnostic script to test Learn page background image loading
"""
import os
import base64
from pathlib import Path

print("=" * 60)
print("LEARN PAGE BACKGROUND IMAGE DIAGNOSTIC")
print("=" * 60)

# Get current working directory
cwd = os.getcwd()
print(f"\n1. Current Working Directory: {cwd}")

# Check if assets folder exists
assets_path = os.path.join(cwd, "assets")
print(f"\n2. Assets folder path: {assets_path}")
print(f"   Assets folder exists: {os.path.exists(assets_path)}")

# List files in assets folder
if os.path.exists(assets_path):
    print(f"\n3. Files in assets folder:")
    for file in os.listdir(assets_path):
        file_path = os.path.join(assets_path, file)
        file_size = os.path.getsize(file_path)
        print(f"   - {file} ({file_size:,} bytes)")

# Test different path combinations
print(f"\n4. Testing path combinations from frontend/pages/2_Learn.py:")

test_paths = [
    "../../assets/learn_bg.png",
    "../assets/learn_bg.png", 
    "assets/learn_bg.png",
    "../../assets/learnsphere_bg.png",
    "../assets/learnsphere_bg.png",
    "assets/learnsphere_bg.png"
]

# Simulate being in frontend/pages/ directory
learn_page_dir = os.path.join(cwd, "frontend", "pages")
print(f"   Learn page directory: {learn_page_dir}")

for rel_path in test_paths:
    full_path = os.path.normpath(os.path.join(learn_page_dir, rel_path))
    exists = os.path.exists(full_path)
    print(f"   {'✓' if exists else '✗'} {rel_path} -> {full_path}")

# Test the correct path
correct_path = os.path.join(cwd, "assets", "learn_bg.png")
print(f"\n5. Correct absolute path: {correct_path}")
print(f"   File exists: {os.path.exists(correct_path)}")

if os.path.exists(correct_path):
    # Try to load and encode the image
    try:
        with open(correct_path, "rb") as f:
            image_data = f.read()
            encoded = base64.b64encode(image_data).decode()
            print(f"   ✓ Successfully loaded and encoded image")
            print(f"   Base64 length: {len(encoded)} characters")
            print(f"   First 100 chars: {encoded[:100]}...")
    except Exception as e:
        print(f"   ✗ Error loading image: {e}")

print("\n" + "=" * 60)
print("RECOMMENDATION:")
print("=" * 60)
print("The image should be loaded using the project root as base.")
print("From frontend/pages/2_Learn.py, use: '../../assets/learn_bg.png'")
print("=" * 60)
