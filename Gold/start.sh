#!/bin/bash
# Quick Start Script for Gold Tier Automation System (Linux/Mac)

echo "============================================================"
echo "  GOLD TIER AUTOMATION SYSTEM - Quick Start"
echo "============================================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed or not in PATH!"
    echo "Please install Python 3 first."
    exit 1
fi

echo "[OK] Python detected: $(python3 --version)"
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "[WARNING] .env file not found!"
    echo "Please configure your environment variables before running."
    echo ""
else
    echo "[OK] .env file found"
fi

# Check if requirements are installed
echo "Checking dependencies..."
if ! python3 -c "import dotenv" &> /dev/null; then
    echo ""
    echo "[INFO] Installing dependencies..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to install dependencies!"
        exit 1
    fi
    echo "[OK] Dependencies installed"
else
    echo "[OK] Dependencies already installed"
fi

echo ""
echo "============================================================"
echo "  READY TO START"
echo "============================================================"
echo ""
echo "Choose an option:"
echo ""
echo "  1. Run Main Menu (Interactive)"
echo "  2. Run Gmail Watcher"
echo "  3. Run WhatsApp Watcher"
echo "  4. Run Reasoning Loop"
echo "  5. Run Agent Interface"
echo "  6. Run All Services (with PM2)"
echo "  7. Verify Setup"
echo "  0. Exit"
echo ""

read -p "Enter your choice: " choice

case $choice in
    1)
        echo ""
        echo "Starting Main Menu..."
        python3 main.py
        ;;
    2)
        echo ""
        echo "Starting Gmail Watcher..."
        python3 gmail_watcher.py
        ;;
    3)
        echo ""
        echo "Starting WhatsApp Watcher..."
        python3 whatsapp_watcher.py
        ;;
    4)
        echo ""
        echo "Starting Reasoning Loop..."
        python3 reasoning_loop.py
        ;;
    5)
        echo ""
        echo "Starting Agent Interface..."
        python3 agent_interface.py
        ;;
    6)
        echo ""
        echo "Starting All Services with PM2..."
        pm2 start ecosystem.config.js
        pm2 save
        echo ""
        echo "Services started! Use 'pm2 monit' to monitor."
        ;;
    7)
        echo ""
        echo "Verifying Gold Tier Setup..."
        python3 verify_gold_tier.py
        ;;
    0)
        echo ""
        echo "Goodbye!"
        exit 0
        ;;
    *)
        echo ""
        echo "[ERROR] Invalid choice!"
        ;;
esac

echo ""
