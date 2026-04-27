@echo off
echo ========================================
echo Starting LearnSphere Pro
echo ========================================
echo.
echo Checking dependencies...
python -c "import streamlit; import groq; import bcrypt; print('✅ All packages installed')" 2>nul
if errorlevel 1 (
    echo ❌ Missing packages. Installing...
    pip install -r requirements.txt
)
echo.
echo Starting Streamlit app...
echo.
cd frontend
streamlit run Home.py
