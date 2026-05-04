@echo off
chcp 65001 >nul
title JJ Chess AI - APK Build Script

echo ========================================
echo    JJ Chess AI Assistant - APK Builder
echo ========================================
echo.

REM Check if WSL is available
echo [Step 1] Checking WSL...
wsl --status >nul 2>&1
if errorlevel 1 (
    echo ERROR: WSL is not installed.
    echo Please install WSL by running: wsl --install
    echo Then restart your computer and run this script again.
    pause
    exit /b 1
)

echo WSL is available.

REM Check if Ubuntu is installed
echo.
echo [Step 2] Checking Ubuntu...
wsl -l | findstr /i "Ubuntu" >nul
if errorlevel 1 (
    echo ERROR: Ubuntu is not installed in WSL.
    echo Please install Ubuntu from Microsoft Store.
    pause
    exit /b 1
)

echo Ubuntu is installed.

REM Copy project to WSL
echo.
echo [Step 3] Copying project to WSL...
wsl -d Ubuntu -- bash -c "mkdir -p ~/jjchessai 2>/dev/null"
if exist "d:\chess-test" (
    xcopy /E /Y "d:\chess-test\*" "\\wsl$\Ubuntu\home\$(wsl -d Ubuntu -- bash -c 'echo $USER')\jjchessai\" >nul 2>&1
    echo Project copied to WSL.
)

REM Install buildozer in WSL
echo.
echo [Step 4] Installing buildozer in WSL...
wsl -d Ubuntu -- bash -c "cd ~/jjchessai && chmod +x build_apk.sh && ./build_apk.sh"

echo.
echo ========================================
echo Build process completed!
echo Check the bin/ directory for APK.
echo ========================================
pause