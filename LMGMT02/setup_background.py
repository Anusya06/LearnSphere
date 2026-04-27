"""
Setup script for LearnSphere background image
Helps you place the background image in the correct location
"""

import os
import shutil
from pathlib import Path

def setup_background_image():
    """Setup background image for LearnSphere"""
    
    print("🎨 LearnSphere Background Image Setup")
    print("=" * 50)
    
    # Check if assets folder exists
    assets_dir = Path("assets")
    if not assets_dir.exists():
        print("📁 Creating assets directory...")
        assets_dir.mkdir(exist_ok=True)
        print("✅ Assets directory created")
    else:
        print("✅ Assets directory exists")
    
    # Check for background image
    bg_image = assets_dir / "ml_background.png"
    
    if bg_image.exists():
        print(f"✅ Background image found: {bg_image}")
        print(f"   Size: {bg_image.stat().st_size / 1024:.1f} KB")
    else:
        print(f"⚠️  Background image not found: {bg_image}")
        print("\n📋 To add your background image:")
        print("   1. Save your image as 'ml_background.png'")
        print("   2. Place it in the 'assets' folder")
        print("   3. Recommended size: 1920x1080 or higher")
        print("   4. Format: PNG, JPG, or JPEG")
        print("\n💡 You uploaded a futuristic AI learning image.")
        print("   Save it as 'assets/ml_background.png' to use it.")
    
    print("\n" + "=" * 50)
    print("🚀 Next Steps:")
    print("   1. Place your background image in assets/ml_background.png")
    print("   2. Run: streamlit run app.py")
    print("   3. Enjoy your professional background!")
    print("=" * 50)

if __name__ == "__main__":
    setup_background_image()
