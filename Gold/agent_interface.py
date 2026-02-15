"""
Agent Interface for Human-in-the-Loop Approval
Monitors Pending_Approval and Approved directories to execute MCP actions
when files are moved from Pending_Approval to Approved
"""

import os
import time
from pathlib import Path
import json
from email_approval_workflow import ApprovalBasedEmailProcessor
from linkedin_poster import LinkedInPoster


class AgentInterface:
    """Interface for handling human approvals and executing corresponding MCP actions"""

    def __init__(self, pending_approval_dir="Pending_Approval", approved_dir="Approved", completed_dir="Completed"):
        self.pending_approval_dir = Path(pending_approval_dir)
        self.approved_dir = Path(approved_dir)
        self.completed_dir = Path(completed_dir)
        
        # Create directories if they don't exist
        self.pending_approval_dir.mkdir(exist_ok=True)
        self.approved_dir.mkdir(exist_ok=True)
        self.completed_dir.mkdir(exist_ok=True)
        
        # Initialize processors
        self.email_processor = ApprovalBasedEmailProcessor()
        self.linkedin_poster = LinkedInPoster()

    def scan_approved_files(self):
        """Scan the Approved directory for newly approved files"""
        if not self.approved_dir.exists():
            return []

        files = list(self.approved_dir.glob("*"))
        return files

    def determine_action_type(self, file_path):
        """Determine the type of action based on the file content and name"""
        content = ""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().lower()
        except:
            pass

        file_name = file_path.name.lower()

        # Check for email-related indicators
        if 'email' in file_name or 'email' in content or '@' in content:
            return 'email'

        # Check for LinkedIn-related indicators
        elif 'linkedin' in file_name or 'post' in file_name or 'linkedin' in content:
            return 'linkedin'

        # Default to email if uncertain
        else:
            return 'email'

    def execute_mcp_action(self, approved_file):
        """Execute the appropriate MCP action based on the approved file"""
        action_type = self.determine_action_type(approved_file)

        if action_type == 'email':
            return self.execute_email_action(approved_file)
        elif action_type == 'linkedin':
            return self.execute_linkedin_action(approved_file)
        else:
            print(f"Unknown action type for file: {approved_file.name}")
            return False

    def execute_email_action(self, approved_file):
        """Execute email sending action"""
        print(f"Executing email action for: {approved_file.name}")
        
        # For email actions, we need to move the original request from Pending_Approval
        # to trigger the email sending process
        try:
            # If the file in Approved directory corresponds to a pending email,
            # we need to process it
            pending_file_path = self.find_corresponding_pending_file(approved_file)
            
            if pending_file_path:
                # Process the email using the email processor
                if self.email_processor.authenticate():
                    # Temporarily move the approval file to trigger processing
                    # This is a simplified approach - in a real system, you'd have
                    # a more sophisticated way to link pending requests to approvals
                    result = self.email_processor.email_sender.send_email_from_file(pending_file_path)
                    
                    # Move the pending file to completed
                    completed_path = self.completed_dir / pending_file_path.name
                    pending_file_path.rename(completed_path)
                    
                    return result
                else:
                    print("Failed to authenticate email sender")
                    return False
            else:
                print(f"No corresponding pending file found for: {approved_file.name}")
                return False
        except Exception as e:
            print(f"Error executing email action: {e}")
            return False

    def execute_linkedin_action(self, approved_file):
        """Execute LinkedIn posting action"""
        print(f"Executing LinkedIn action for: {approved_file.name}")
        
        try:
            # Read the content to get the post text
            with open(approved_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract the post content (assuming the first few lines are the post)
            lines = content.split('\n')
            post_content = ""
            for line in lines:
                if line.strip() and not line.startswith('Original Request:') and not line.startswith('Draft:'):
                    post_content += line + " "
            
            post_content = post_content.strip()
            
            if post_content:
                # Post to LinkedIn
                success = self.linkedin_poster.post_to_linkedin(post_content)
                
                # Move the approved file to completed
                completed_path = self.completed_dir / approved_file.name
                approved_file.rename(completed_path)
                
                return success
            else:
                print("No post content found in approved file")
                return False
                
        except Exception as e:
            print(f"Error executing LinkedIn action: {e}")
            return False

    def find_corresponding_pending_file(self, approved_file):
        """Find the corresponding pending file based on naming convention or content"""
        # Look for a file in Pending_Approval that matches the approval
        for pending_file in self.pending_approval_dir.glob("*"):
            # Simple matching based on similar naming
            if approved_file.stem in pending_file.name or pending_file.stem in approved_file.name:
                return pending_file
        
        # If no exact match, return the first pending file as a fallback
        pending_files = list(self.pending_approval_dir.glob("*"))
        return pending_files[0] if pending_files else None

    def process_approvals(self):
        """Process all files in the Approved directory"""
        approved_files = self.scan_approved_files()
        
        if not approved_files:
            return 0

        print(f"Processing {len(approved_files)} approved files...")

        processed_count = 0
        for approved_file in approved_files:
            print(f"Processing approval: {approved_file.name}")
            
            if self.execute_mcp_action(approved_file):
                processed_count += 1
                print(f"Successfully processed: {approved_file.name}")
            else:
                print(f"Failed to process: {approved_file.name}")

        return processed_count

    def run_approval_monitoring(self, interval=5):
        """Run a continuous monitoring loop for approvals"""
        print("Starting Agent Interface - Approval Monitoring...")
        print(f"Monitoring: {self.approved_dir} for new approvals")
        
        # Track previously seen files to detect new ones
        previous_approved_files = set()
        
        try:
            while True:
                current_approved_files = {f.name for f in self.scan_approved_files()}
                new_approved_files = current_approved_files - previous_approved_files
                
                if new_approved_files:
                    print(f"New approvals detected: {new_approved_files}")
                    processed_count = self.process_approvals()
                    print(f"Processed {processed_count} new approvals")
                    
                    # Update the list of seen files
                    previous_approved_files = {f.name for f in self.scan_approved_files()}
                else:
                    # Update the list of seen files if no new ones
                    previous_approved_files = current_approved_files
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\nApproval monitoring stopped by user.")


def main():
    """Main function to run the agent interface"""
    print("Initializing Agent Interface for Human-in-the-Loop Approval...")
    
    agent = AgentInterface()
    
    # For demonstration, run once
    processed_count = agent.process_approvals()
    print(f"Processed {processed_count} approvals")
    
    # Uncomment the line below to run continuously
    # agent.run_approval_monitoring()


if __name__ == "__main__":
    main()