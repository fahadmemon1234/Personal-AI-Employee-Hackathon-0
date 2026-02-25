"""
MCP Servers Startup Script
Starts all 5 MCP servers: Email, Browser, Odoo, Social (Meta), and X (Twitter)
"""

import subprocess
import sys
import time
from threading import Thread
from pathlib import Path

# Server configurations
SERVERS = [
    {
        'name': 'Email MCP',
        'file': 'mcp_email_server.py',
        'port': 8080,
        'description': 'Email management and approval workflow'
    },
    {
        'name': 'Browser MCP',
        'file': 'mcp_browser_server.py',
        'port': 8081,
        'description': 'Web browsing and automation'
    },
    {
        'name': 'Odoo MCP',
        'file': 'mcp_odoo_server.py',
        'port': 8082,
        'description': 'Odoo ERP integration'
    },
    {
        'name': 'Social MCP (Meta)',
        'file': 'mcp_social_server.py',
        'port': 8083,
        'description': 'Facebook & Instagram posting'
    },
    {
        'name': 'X MCP (Twitter)',
        'file': 'mcp_x_server.py',
        'port': 8084,
        'description': 'Twitter/X posting'
    }
]


def start_server(server_config):
    """Start a single MCP server"""
    name = server_config['name']
    file = server_config['file']
    port = server_config['port']
    desc = server_config['description']
    
    print("\n" + "=" * 60)
    print(f"Starting {name} on port {port}...")
    print(f"Description: {desc}")
    print("=" * 60)
    
    try:
        subprocess.run([sys.executable, file], timeout=3600)
    except KeyboardInterrupt:
        print(f"\n{name} stopped.")
    except Exception as e:
        print(f"\n{name} error: {e}")


def main():
    """Start all MCP servers"""
    print("\n" + "=" * 70)
    print(" " * 15 + "MCP Servers - All-in-One Startup")
    print("=" * 70)
    print(f"\nProject Directory: {Path('.').absolute()}")
    print(f"\nServers to start: {len(SERVERS)}")
    
    for i, server in enumerate(SERVERS, 1):
        print(f"  {i}. {server['name']:25} -> Port {server['port']}")
    
    print("\n" + "=" * 70)
    print("\nNote: Each server runs in a separate window.")
    print("      Press Ctrl+C in each window to stop individual servers.")
    print("=" * 70 + "\n")
    
    # Start each server in a separate thread
    threads = []
    
    for server in SERVERS:
        thread = Thread(
            target=start_server,
            args=(server,),
            daemon=True,
            name=server['name']
        )
        thread.start()
        threads.append(thread)
        time.sleep(1)  # Stagger startup
    
    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n" + "=" * 70)
        print("Shutting down all MCP servers...")
        print("=" * 70)
        print("All servers stopped.")


if __name__ == "__main__":
    main()
