@echo off
REM Quick Start Script for Gold Tier Automation System (Windows)

echo ============================================================
echo   GOLD TIER AUTOMATION SYSTEM - Quick Start
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

echo [OK] Python detected
echo.

REM Check if .env file exists
if not exist ".env" (
    echo [WARNING] .env file not found!
    echo Please configure your environment variables before running.
    echo.
) else (
    echo [OK] .env file found
)

REM Check if requirements are installed
echo Checking dependencies...
pip show python-dotenv >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [INFO] Installing dependencies...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install dependencies!
        pause
        exit /b 1
    )
    echo [OK] Dependencies installed
) else (
    echo [OK] Dependencies already installed
)

echo.
echo ============================================================
echo   READY TO START
echo ============================================================
echo.
echo Choose an option:
echo.
echo   1. Run Main Menu (Interactive)
echo   2. Run Gmail Watcher
echo   3. Run WhatsApp Watcher
echo   4. Run Reasoning Loop
echo   5. Run Agent Interface
echo   6. Run All Services (with PM2)
echo   7. Verify Setup
echo   0. Exit
echo.

set /p choice="Enter your choice: "

if "%choice%"=="1" (
    echo.
    echo Starting Main Menu...
    python main.py
) else if "%choice%"=="2" (
    echo.
    echo Starting Gmail Watcher...
    python gmail_watcher.py
) else if "%choice%"=="3" (
    echo.
    echo Starting WhatsApp Watcher...
    python whatsapp_watcher.py
) else if "%choice%"=="4" (
    echo.
    echo Starting Reasoning Loop...
    python reasoning_loop.py
) else if "%choice%"=="5" (
    echo.
    echo Starting Agent Interface...
    python agent_interface.py
) else if "%choice%"=="6" (
    echo.
    echo Starting All Services with PM2...
    pm2 start ecosystem.config.js
    pm2 save
    echo.
    echo Services started! Use 'pm2 monit' to monitor.
) else if "%choice%"=="7" (
    echo.
    echo Verifying Gold Tier Setup...
    python verify_gold_tier.py
) else if "%choice%"=="0" (
    echo.
    echo Goodbye!
    exit /b 0
) else (
    echo.
    echo [ERROR] Invalid choice!
)

echo.
pause
