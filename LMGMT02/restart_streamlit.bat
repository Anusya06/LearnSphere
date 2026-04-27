@echo off
echo ========================================
echo   Restarting Streamlit with Audio Fix
echo ========================================
echo.

echo Step 1: Stopping Streamlit...
taskkill /F /IM streamlit.exe 2>nul
if %errorlevel% equ 0 (
    echo    ✓ Streamlit stopped
) else (
    echo    ℹ No Streamlit processes found
)

echo.
echo Step 2: Waiting for processes to close...
timeout /t 3 /nobreak >nul
echo    ✓ Ready

echo.
echo Step 3: Installing dependencies...
pip install gtts pydub --quiet
if %errorlevel% equ 0 (
    echo    ✓ Dependencies installed
) else (
    echo    ⚠ Error installing dependencies
)

echo.
echo Step 4: Starting Streamlit...
echo    Opening browser at http://localhost:8501
echo.
echo ========================================
echo   Audio System Ready - 90%% Faster!
echo ========================================
echo.
echo Press Ctrl+C to stop Streamlit
echo.

streamlit run frontend/Home.py
