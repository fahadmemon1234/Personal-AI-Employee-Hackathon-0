"""
Scheduler for Silver Tier Automation System
Runs reasoning_loop.py every 30 minutes
"""
import schedule
import time
import subprocess
import sys
from threading import Thread


def run_reasoning_loop():
    """Run the reasoning loop script"""
    try:
        print(f"Starting reasoning_loop.py at {time.strftime('%Y-%m-%d %H:%M:%S')}")
        result = subprocess.run([sys.executable, 'reasoning_loop.py'], 
                              capture_output=True, text=True, timeout=300)  # 5 minute timeout
        
        if result.returncode == 0:
            print(f"reasoning_loop.py completed successfully at {time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Output: {result.stdout[:500]}...")  # First 500 chars of output
        else:
            print(f"reasoning_loop.py failed at {time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Error: {result.stderr}")
    except subprocess.TimeoutExpired:
        print(f"reasoning_loop.py timed out at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    except Exception as e:
        print(f"Error running reasoning_loop.py: {str(e)}")


def run_scheduler():
    """Run the scheduler in the background"""
    # Schedule the reasoning loop to run every 30 minutes
    schedule.every(30).minutes.do(run_reasoning_loop)
    
    # Also run once immediately
    run_reasoning_loop()
    
    print("Scheduler started. Running reasoning_loop.py every 30 minutes.")
    print("Press Ctrl+C to stop the scheduler.")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nScheduler stopped by user.")


def start_scheduler_daemon():
    """Start the scheduler as a daemon thread"""
    scheduler_thread = Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    return scheduler_thread


if __name__ == "__main__":
    # Install schedule library if not already installed
    try:
        import schedule
    except ImportError:
        print("Installing schedule library...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'schedule'])
        import schedule
    
    # Run the scheduler
    run_scheduler()