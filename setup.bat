@echo off
title WTTG2 Organizer - Setup Wizard
echo ==========================================
echo    WTTG2 ORGANIZER v2.0 - SETUP
echo ==========================================
echo.
echo [*] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] ERROR: Python is not installed or not in PATH!
    echo please install Python from python.org
    pause
    exit /b
)

echo [*] Installing required dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo [!] ERROR: Dependency installation failed!
    pause
    exit /b
)

echo.
echo ==========================================
echo    SETUP COMPLETE! 
echo    You can now run the app via Run.bat
echo ==========================================
echo.
pause
