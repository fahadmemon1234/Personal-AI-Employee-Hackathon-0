"""
check_system_health.py
Skill to report the PID and status of processes managed by PM2 on the Obsidian Dashboard
"""

import subprocess
import sys
import json
import re
from pathlib import Path
from datetime import datetime


def get_pm2_process_info():
    """
    Get information about PM2-managed processes
    """
    try:
        # Run pm2 jlist to get JSON output of all processes
        result = subprocess.run(['pm2', 'jlist'], capture_output=True, text=True, check=True)
        processes = json.loads(result.stdout)
        
        process_info = []
        
        for proc in processes:
            info = {
                'name': proc['name'],
                'pid': proc['pid'],
                'pm2_pid': proc['pm_id'],
                'status': proc['pm2_env']['status'],
                'instances': proc['pm2_env'].get('instances', 1),
                'created_at': proc['pm2_env'].get('created_at', 'N/A'),
                'memory': proc['monit'].get('memory', 0) if 'monit' in proc else 0,
                'cpu': proc['monit'].get('cpu', 0) if 'monit' in proc else 0
            }
            process_info.append(info)
        
        return process_info
    
    except subprocess.CalledProcessError as e:
        print(f"Error running PM2 command: {e}")
        return []
    except FileNotFoundError:
        print("PM2 is not installed or not in PATH")
        return []
    except json.JSONDecodeError as e:
        print(f"Error parsing PM2 output: {e}")
        return []


def format_process_status(processes):
    """
    Format the process information for display
    """
    if not processes:
        return "No PM2 processes found or PM2 not accessible"
    
    status_text = "## System Health Report\n"
    status_text += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    
    status_text += "### Active Processes\n"
    
    for proc in processes:
        status_text += f"- **{proc['name']}**\n"
        status_text += f"  - Status: `{proc['status']}`\n"
        status_text += f"  - PID: {proc['pid']}\n"
        status_text += f"  - PM2 ID: {proc['pm2_pid']}\n"
        status_text += f"  - Instances: {proc['instances']}\n"
        status_text += f"  - Memory: {proc['memory']:,} bytes\n"
        status_text += f"  - CPU: {proc['cpu']}%\n"
        status_text += f"  - Created: {proc['created_at']}\n\n"
    
    # Count running processes
    running_count = len([p for p in processes if p['status'] == 'online'])
    total_count = len(processes)
    
    status_text += f"### Summary\n"
    status_text += f"- **Total Processes:** {total_count}\n"
    status_text += f"- **Running Processes:** {running_count}\n"
    status_text += f"- **Stopped Processes:** {total_count - running_count}\n\n"
    
    # Add health assessment
    if running_count == total_count and total_count > 0:
        status_text += "### Health Assessment\n"
        status_text += "- **Status:** :white_check_mark: All systems operational\n"
        status_text += "- **Assessment:** All monitored processes are running normally\n"
    elif running_count == 0:
        status_text += "### Health Assessment\n"
        status_text += "- **Status:** :x: All processes offline\n"
        status_text += "- **Assessment:** No processes are currently running. Check system status.\n"
    else:
        status_text += "### Health Assessment\n"
        status_text += f"- **Status:** :warning: {total_count - running_count} processes offline\n"
        status_text += "- **Assessment:** Some processes are not running as expected\n"
    
    return status_text


def update_dashboard_with_health_status():
    """
    Update the Dashboard.md file with the system health status
    """
    try:
        # Get process information
        processes = get_pm2_process_info()
        
        # Format the status information
        health_status = format_process_status(processes)
        
        # Read the current dashboard file
        dashboard_path = Path("Dashboard.md")
        if not dashboard_path.exists():
            print(f"Dashboard.md not found at {dashboard_path}")
            return False
            
        with open(dashboard_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if System Health section already exists
        if "## System Health Report" in content:
            # Replace existing health report
            start_marker = content.find("## System Health Report")
            end_marker = content.find("### Last System Health Check", start_marker)
            if end_marker == -1:
                end_marker = content.find("---", start_marker)  # Alternative end marker
                if end_marker == -1:
                    end_marker = len(content)  # If no end marker, replace to end of file
                else:
                    end_marker = content.rfind("\n", 0, end_marker)  # End at line before marker
                    
            # Replace the health report section
            new_content = content[:start_marker] + health_status + "\n### Last System Health Check\n" + content[end_marker:]
        else:
            # Append health report to the end of the file
            new_content = content + "\n\n" + health_status + "\n### Last System Health Check\n" + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Write the updated content back to the file
        with open(dashboard_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"Dashboard.md updated with system health status:")
        print(f"- Found {len(processes)} PM2 processes")
        running_count = len([p for p in processes if p['status'] == 'online'])
        print(f"- {running_count} processes running")
        
        return True
        
    except Exception as e:
        print(f"Error updating dashboard with health status: {str(e)}")
        return False


def run_system_health_check():
    """
    Main function to run the system health check
    """
    print("Running system health check...")
    
    # Get process information
    processes = get_pm2_process_info()
    
    if not processes:
        print("No processes found or PM2 is not accessible.")
        print("Make sure PM2 is installed and processes are started with 'pm2 start ecosystem.config.js'")
        return
    
    # Print formatted status
    status_text = format_process_status(processes)
    print(status_text)
    
    # Update the dashboard
    success = update_dashboard_with_health_status()
    
    if success:
        print("\nSystem health report generated and dashboard updated successfully!")
    else:
        print("\nSystem health report generated but dashboard update failed.")


def system_health_cli():
    """
    Command-line interface for the system health check
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Check system health of PM2-managed processes")
    parser.add_argument("--dashboard-path", default="Dashboard.md", 
                       help="Path to the Dashboard.md file")
    parser.add_argument("--output-format", choices=["console", "markdown", "json"], 
                       default="console", help="Output format")
    
    args = parser.parse_args()
    
    # Update the global dashboard path if specified
    global dashboard_path
    dashboard_path = args.dashboard_path
    
    if args.output_format == "json":
        processes = get_pm2_process_info()
        print(json.dumps(processes, indent=2))
    elif args.output_format == "markdown":
        processes = get_pm2_process_info()
        print(format_process_status(processes))
    else:  # console
        run_system_health_check()


if __name__ == "__main__":
    system_health_cli()