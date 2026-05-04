@echo off
title JJ Chess AI - Installing Dependencies

echo ========================================
echo    JJ Chess AI Assistant - Setup
echo ========================================
echo.

REM Check if uv is available
where uv >nul 2>&1
if %errorlevel%==0 (
    echo Using uv to create virtual environment...
    echo.
    
    REM Create virtual environment
    python -m venv venv
    
    REM Activate and install
    call venv\Scripts\activate.bat
    pip install --upgrade pip
    pip install kivy pillow opencv-python mss numpy requests
    
    echo.
    echo ========================================
    echo Installation complete!
    echo.
    echo To run the program:
    echo   call venv\Scripts\activate.bat
    echo   python main.py
    echo ========================================
) else (
    echo Using pip to install packages...
    echo.
    
    pip install --upgrade pip
    pip install kivy pillow opencv-python mss numpy requests --break-system-packages
    
    echo.
    echo ========================================
    echo Installation complete!
    echo.
    echo Now run: python main.py
    echo ========================================
)

echo.
pause
