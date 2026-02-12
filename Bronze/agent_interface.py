"""
AI Agent Interface Script
This script demonstrates how the AI Agent can proactively read from and write to the vault
"""

import os
import json
from datetime import datetime
from pathlib import Path


class AgentInterface:
    """Interface for the AI Agent to interact with the vault"""
    
    def __init__(self):
        self.vault_path = Path.cwd()  # Current directory as vault
        self.inbox_path = self.vault_path / "Inbox"
        self.needs_action_path = self.vault_path / "Needs_Action"
        self.dashboard_path = self.vault_path / "Dashboard.md"
        
    def read_inbox_status(self):
        """Read the status of the Inbox folder"""
        if self.inbox_path.exists():
            files = list(self.inbox_path.glob("*"))
            return {
                "folder_exists": True,
                "file_count": len(files),
                "files": [f.name for f in files],
                "last_modified": self._get_last_modified(self.inbox_path)
            }
        else:
            return {"folder_exists": False, "file_count": 0, "files": []}
    
    def read_needs_action_status(self):
        """Read the status of the Needs_Action folder"""
        if self.needs_action_path.exists():
            files = list(self.needs_action_path.glob("*"))
            return {
                "folder_exists": True,
                "file_count": len(files),
                "files": [f.name for f in files],
                "last_modified": self._get_last_modified(self.needs_action_path)
            }
        else:
            return {"folder_exists": False, "file_count": 0, "files": []}
    
    def read_dashboard(self):
        """Read the current dashboard content"""
        if self.dashboard_path.exists():
            with open(self.dashboard_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return content
        else:
            return "Dashboard file not found"
    
    def update_dashboard_with_info(self, info):
        """Update the dashboard with new information"""
        current_content = self.read_dashboard()
        
        # Add the new information to the dashboard
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        update_section = f"\n\n## Last Updated: {timestamp}\n"
        update_section += f"### System Info Added:\n{info}\n"
        
        # Write the updated content back to the dashboard
        with open(self.dashboard_path, 'a', encoding='utf-8') as f:
            f.write(update_section)
        
        print(f"Dashboard updated at {timestamp}")
    
    def _get_last_modified(self, path):
        """Get the last modified time of a directory or file"""
        if path.is_file():
            return datetime.fromtimestamp(path.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')
        elif path.is_dir():
            # Return the most recent modification time of any file in the directory
            files = list(path.glob("*"))
            if files:
                latest = max(files, key=lambda x: x.stat().st_mtime)
                return datetime.fromtimestamp(latest.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')
        return "N/A"
    
    def get_system_summary(self):
        """Generate a summary of the system status"""
        inbox_status = self.read_inbox_status()
        needs_action_status = self.read_needs_action_status()
        
        summary = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "vault_location": str(self.vault_path),
            "inbox": inbox_status,
            "needs_action": needs_action_status,
            "dashboard_exists": self.dashboard_path.exists()
        }
        
        return summary
    
    def write_to_vault(self, filename, content, folder=None):
        """Write content to a file in the vault"""
        if folder:
            file_path = self.vault_path / folder / filename
            # Create folder if it doesn't exist
            (self.vault_path / folder).mkdir(exist_ok=True)
        else:
            file_path = self.vault_path / filename
            
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Wrote to {file_path}")
        return str(file_path)


def main():
    """Main function demonstrating the agent's interaction with the vault"""
    agent = AgentInterface()
    
    print("AI Agent Vault Interface")
    print("="*50)
    
    # Get system summary
    summary = agent.get_system_summary()
    print("\nSystem Summary:")
    print(json.dumps(summary, indent=2))
    
    # Update dashboard with system info
    info_to_add = f"""
- Inbox has {summary['inbox']['file_count']} files
- Needs_Action has {summary['needs_action']['file_count']} files
- Last checked: {summary['timestamp']}
"""
    
    agent.update_dashboard_with_info(info_to_add)
    
    # Example of writing a new file to the vault
    report_content = f"""System Report
Generated at: {summary['timestamp']}

Inbox Status:
- Files: {summary['inbox']['file_count']}
- Latest Activity: {summary['inbox']['last_modified']}

Needs Action Status:
- Files: {summary['needs_action']['file_count']}
- Latest Activity: {summary['needs_action']['last_modified']}
"""
    
    agent.write_to_vault("system_report.txt", report_content)
    
    print("\nDemonstration complete!")
    print("Check Dashboard.md for updates and system_report.txt for the generated report.")


if __name__ == "__main__":
    main()