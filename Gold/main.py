#!/usr/bin/env python3
"""
Main Runner Script for Gold Tier Automation System
Provides a menu-driven interface to run different components
"""

import os
import sys
import subprocess
from pathlib import Path
from dotenv import load_dotenv

# Fix Unicode encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Load environment variables
load_dotenv()


def print_banner():
    """Print application banner"""
    print("\n" + "="*60)
    print("  GOLD TIER AUTOMATION SYSTEM")
    print("  Fully Autonomous AI Employee")
    print("="*60 + "\n")


def print_menu():
    """Print main menu"""
    print("Select a component to run:")
    print("-" * 40)
    print("1.  Gmail Watcher (Monitor Emails)")
    print("2.  WhatsApp Watcher (Monitor WhatsApp)")
    print("3.  Reasoning Loop (Process Requests)")
    print("4.  Agent Interface (Handle Approvals)")
    print("5.  LinkedIn Poster (Auto Posting)")
    print("6.  Scheduler (Task Scheduler)")
    print("7.  System Health Check")
    print("8.  CEO Briefing Generator")
    print("9.  Run All Services (Background)")
    print("10. Verify Gold Tier Setup")
    print("11. Run Final Tests")
    print("0.  Exit")
    print("-" * 40)


def run_script(script_name):
    """Run a Python script"""
    script_path = Path(script_name)

    if not script_path.exists():
        print(f"❌ Error: {script_name} not found!")
        return

    print(f"\n▶️  Running {script_name}...")
    print("Press Ctrl+C to stop\n")

    try:
        subprocess.run([sys.executable, str(script_path)], check=True)
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error running {script_name}: {e}")
    except KeyboardInterrupt:
        print(f"\n⏹️  Stopped {script_name}")


def check_env_setup():
    """Check if .env file exists and has required variables"""
    env_path = Path(".env")

    if not env_path.exists():
        print("⚠️  Warning: .env file not found!")
        print("Please configure your environment variables first.")
        return False

    # Check for critical variables
    critical_vars = [
        "ODOO_URL",
        "ODOO_DB",
        "ODOO_USERNAME",
        "GMAIL_CREDENTIALS_FILE"
    ]

    missing = []
    for var in critical_vars:
        if not os.getenv(var):
            missing.append(var)

    if missing:
        print(f"⚠️  Warning: Missing environment variables: {', '.join(missing)}")
        print("Some features may not work correctly.")
        return False

    print("✅ Environment variables configured!")
    return True


def run_all_services():
    """Run all services using PM2 or background processes"""
    print("\n🚀 Starting all services...")

    # Check if PM2 is available
    try:
        result = subprocess.run(["pm2", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("PM2 detected. Starting services with PM2...")
            subprocess.run(["pm2", "start", "ecosystem.config.js"])
            subprocess.run(["pm2", "save"])
            print("✅ All services started with PM2!")
            print("Use 'pm2 monit' to monitor services")
            print("Use 'pm2 logs' to view logs")
            print("Use 'pm2 stop all' to stop services")
            return
    except FileNotFoundError:
        pass

    print("PM2 not found. You can install it with: npm install -g pm2")
    print("\nAlternatively, you can run individual services manually.")


def main():
    """Main function"""
    print_banner()

    # Check environment setup
    check_env_setup()

    while True:
        print_menu()

        try:
            choice = input("\nEnter your choice (0-11): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\n👋 Goodbye!")
            sys.exit(0)

        print()

        if choice == "1":
            run_script("gmail_watcher.py")
        elif choice == "2":
            run_script("whatsapp_watcher.py")
        elif choice == "3":
            run_script("reasoning_loop.py")
        elif choice == "4":
            run_script("agent_interface.py")
        elif choice == "5":
            run_script("linkedin_poster.py")
        elif choice == "6":
            run_script("scheduler.py")
        elif choice == "7":
            run_script("check_system_health.py")
        elif choice == "8":
            run_script("ceo_briefing_skill.py")
        elif choice == "9":
            run_all_services()
        elif choice == "10":
            run_script("verify_gold_tier.py")
        elif choice == "11":
            run_script("final_test.py")
        elif choice == "0":
            print("\n👋 Goodbye!")
            sys.exit(0)
        else:
            print("❌ Invalid choice! Please enter a number between 0 and 11.")


if __name__ == "__main__":
    main()
