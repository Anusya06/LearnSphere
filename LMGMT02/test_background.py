"""
Test script to verify background image implementation
"""
import os
import base64

def test_background_image():
    """Test if background image can be loaded and encoded"""
    
    print("🎨 Testing Background Image Implementation")
    print("=" * 60)
    
    # Test paths
    test_paths = [
        "assets/ml image.jpg",
        "assets/ml_background.png",
        os.path.join("assets", "ml image.jpg"),
        os.path.join("assets", "ml_background.png")
    ]
    
    found = False
    for path in test_paths:
        print(f"\n📁 Testing path: {path}")
        
        if os.path.exists(path):
            print(f"   ✅ File exists!")
            
            try:
                with open(path, "rb") as f:
                    data = f.read()
                    encoded = base64.b64encode(data).decode()
                    
                print(f"   ✅ File readable")
                print(f"   ✅ Base64 encoding successful")
                print(f"   📊 File size: {len(data) / 1024:.1f} KB")
                print(f"   📊 Encoded size: {len(encoded) / 1024:.1f} KB")
                print(f"   📊 Encoded preview: {encoded[:50]}...")
                
                found = True
                print(f"\n   🎉 SUCCESS! Background image ready to use!")
                print(f"   📍 Using: {path}")
                break
                
            except Exception as e:
                print(f"   ❌ Error reading file: {e}")
        else:
            print(f"   ⚠️  File not found")
    
    if not found:
        print("\n" + "=" * 60)
        print("❌ No background image found!")
        print("\n📋 To fix this:")
        print("   1. Place your image in the 'assets' folder")
        print("   2. Name it 'ml image.jpg' or 'ml_background.png'")
        print("   3. Supported formats: JPG, PNG, JPEG")
        print("=" * 60)
        return False
    
    print("\n" + "=" * 60)
    print("✅ Background image test PASSED!")
    print("🚀 Your app is ready to run with the background image")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = test_background_image()
    
    if success:
        print("\n💡 Next step: Run your app with:")
        print("   streamlit run app.py")
    else:
        print("\n⚠️  Please add a background image before running the app")
