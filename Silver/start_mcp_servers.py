"""
MCP Servers Startup Script
Starts both Email and Browser MCP servers
"""

import subprocess
import sys
import time
from threading import Thread


def start_email_server():
    """Start the MCP Email Server"""
    print("=" * 60)
    print("Starting MCP Email Server on port 8080...")
    print("=" * 60)
    subprocess.run([sys.executable, 'mcp_email_server.py'])


def start_browser_server():
    """Start the MCP Browser Server"""
    print("=" * 60)
    print("Starting MCP Browser Server on port 8081...")
    print("=" * 60)
    subprocess.run([sys.executable, 'mcp_browser_server.py'])


def main():
    """Start both MCP servers"""
    print("\n" + "=" * 60)
    print("Silver Tier MCP Servers")
    print("=" * 60)
    print("\nStarting MCP Servers...")
    print("\nNote: Press Ctrl+C to stop all servers")
    print("=" * 60 + "\n")

    # Start email server in a thread
    email_thread = Thread(target=start_email_server, daemon=True)
    email_thread.start()

    # Wait a moment for email server to initialize
    time.sleep(2)

    # Start browser server in a thread
    browser_thread = Thread(target=start_browser_server, daemon=True)
    browser_thread.start()

    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nShutting down all MCP servers...")
        print("All servers stopped.")


if __name__ == "__main__":
    main()
