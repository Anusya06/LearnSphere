"""
Test the background function from Learn page
"""
import sys
from pathlib import Path
import os
import base64

# Add the frontend directory to path
sys.path.append(str(Path(__file__).parent / "frontend"))

# Mock streamlit for testing
class MockStreamlit:
    def markdown(self, html, unsafe_allow_html):
        print(f"CSS injected (length: {len(html)} chars)")
        # Extract and show first 200 chars of CSS
        lines = html.split('\n')
        for i, line in enumerate(lines[:20]):
            if line.strip():
                print(f"  {i+1:2d}: {line[:100]}...")
    
    def toast(self, message, icon):
        print(f"Toast: {icon} {message}")

# Create mock st object
st = MockStreamlit()

# Import the function from the Learn page
exec(open("frontend/pages/2_Learn.py").read().split("def set_learn_page_background():")[0])

# Now execute the function
print("=" * 60)
print("TESTING BACKGROUND FUNCTION")
print("=" * 60)

# Call the function
set_learn_page_background()

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
print("If you see 'CSS injected' above, the function is working.")
print("If you see '✓ Background image loaded', the image was found.")
print("\nNext steps:")
print("1. Restart Streamlit server")
print("2. Navigate to Learn page")
print("3. Use Ctrl+Shift+R to hard refresh browser")
print("=" * 60)