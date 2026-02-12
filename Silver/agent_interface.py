"""
Agent Interface for Silver Tier Automation System
Coordinates all agent skills and enforces HITL validation
"""
import os
import time
from pathlib import Path
from threading import Thread
import schedule


class AgentInterface:
    def __init__(self):
        self.pending_approval_dir = Path("Pending_Approval")
        self.approved_dir = Path("Approved")
        self.skills_dir = Path(".qwen/skills")
        
        # Create directories if they don't exist
        self.pending_approval_dir.mkdir(exist_ok=True)
        self.approved_dir.mkdir(exist_ok=True)
    
    def validate_hitl_process(self):
        """Validate that all pending items require approval before execution"""
        pending_items = list(self.pending_approval_dir.glob("*"))
        
        if pending_items:
            print(f"Validation: Found {len(pending_items)} items in Pending_Approval")
            print("These items require manual approval before execution.")
            print("To approve, move files from Pending_Approval to Approved directory.")
            return True
        else:
            print("Validation: No pending items awaiting approval")
            return False
    
    def check_and_execute_approved(self):
        """Check for approved items and execute them"""
        approved_items = list(self.approved_dir.glob("*"))
        
        if approved_items:
            print(f"Found {len(approved_items)} approved items to execute")
            for item in approved_items:
                self.execute_approved_item(item)
        else:
            print("No approved items to execute")
    
    def execute_approved_item(self, item_path):
        """Execute an approved item based on its type"""
        print(f"Executing approved item: {item_path.name}")
        
        # For LinkedIn posts
        if "linkedin_post" in item_path.name:
            self.execute_linkedin_post(item_path)
        # For email responses
        elif "draft_response" in item_path.name:
            self.execute_email_response(item_path)
        # For other types
        else:
            print(f"Unknown item type: {item_path.name}")
    
    def execute_linkedin_post(self, item_path):
        """Execute a LinkedIn post that has been approved"""
        print(f"Executing LinkedIn post: {item_path.name}")
        
        # Read the post content
        with open(item_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # In a real implementation, this would post to LinkedIn
        # For now, we'll just simulate and log
        print(f"LinkedIn post content: {content[:100]}...")
        
        # Archive the executed post
        posted_dir = Path("Posted")
        posted_dir.mkdir(exist_ok=True)
        archive_path = posted_dir / item_path.name
        item_path.rename(archive_path)
        
        print(f"LinkedIn post executed and archived: {archive_path}")
    
    def execute_email_response(self, item_path):
        """Execute an email response that has been approved"""
        print(f"Executing email response: {item_path.name}")
        
        # Read the response content
        with open(item_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # In a real implementation, this would send the email
        # For now, we'll just simulate and log
        print(f"Email response content: {content[:100]}...")
        
        # Archive the executed response
        sent_dir = Path("Sent")
        sent_dir.mkdir(exist_ok=True)
        archive_path = sent_dir / item_path.name
        item_path.rename(archive_path)
        
        print(f"Email response executed and archived: {archive_path}")
    
    def run_validation_cycle(self):
        """Run a complete validation cycle"""
        print(f"\n--- HITL Validation Cycle Started at {time.strftime('%Y-%m-%d %H:%M:%S')} ---")
        
        # Validate pending items
        self.validate_hitl_process()
        
        # Execute approved items
        self.check_and_execute_approved()
        
        print(f"--- HITL Validation Cycle Completed at {time.strftime('%Y-%m-%d %H:%M:%S')} ---\n")
    
    def start_monitoring(self):
        """Start monitoring for approved items in the background"""
        def monitor_loop():
            while True:
                self.run_validation_cycle()
                time.sleep(60)  # Check every minute
        
        monitor_thread = Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
        return monitor_thread


def run_agent_interface():
    """Run the main agent interface"""
    print("Starting Agent Interface for Silver Tier Automation...")
    
    agent = AgentInterface()
    
    # Run one validation cycle
    agent.run_validation_cycle()
    
    # Start continuous monitoring
    print("Starting continuous monitoring for approved items...")
    monitor_thread = agent.start_monitoring()
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        print("\nAgent Interface stopped by user.")


if __name__ == "__main__":
    run_agent_interface()