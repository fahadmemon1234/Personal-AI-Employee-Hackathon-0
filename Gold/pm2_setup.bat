@echo off
REM pm2_setup.bat - Script to install and configure PM2 for process management

echo Installing PM2...
npm install -g pm2-windows-service

if errorlevel 1 (
    echo Installing PM2 directly as Windows service installation failed...
    npm install -g pm2
)

REM Check if installation was successful
pm2 --version >nul 2>&1
if errorlevel 1 (
    echo PM2 installation failed. Please install Node.js and npm first.
    pause
    exit /b 1
)

echo PM2 installed successfully!

REM Navigate to the project directory
cd /d "%~dp0"

REM Start all processes defined in ecosystem.config.js
echo Starting all processes with PM2...
pm2 start ecosystem.config.js

REM Save the PM2 configuration for auto-start on boot
echo Saving PM2 configuration...
pm2 save

REM Enable PM2 startup script to run on system boot
echo Setting up PM2 startup script...
pm2 startup

echo PM2 setup complete!
echo Your processes are now running and will restart automatically on system boot.
echo.
echo Useful PM2 commands:
echo   pm2 status          ^- View status of all processes
echo   pm2 logs            ^- View logs of all processes
echo   pm2 restart all     ^- Restart all processes
echo   pm2 stop all        ^- Stop all processes
echo   pm2 delete all      ^- Delete all processes from PM2

pause