"""
WhatsApp Watcher Skill
Monitors WhatsApp for new messages and processes them according to business rules.
"""
import os
from pathlib import Path
import time
import json


class WhatsAppWatcherSkill:
    def __init__(self):
        # In a real implementation, this would connect to WhatsApp Business API
        # For now, we'll simulate monitoring a directory for incoming messages
        self.inbox_dir = Path("Inbox")
        self.needs_action_dir = Path("Needs_Action")
        
        # Create directories if they don't exist
        self.inbox_dir.mkdir(exist_ok=True)
        self.needs_action_dir.mkdir(exist_ok=True)
    
    def scan_inbox(self):
        """Scan the inbox for new WhatsApp messages"""
        message_files = list(self.inbox_dir.glob("*.txt"))
        return message_files
    
    def process_message(self, message_file):
        """Process a single WhatsApp message"""
        with open(message_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Determine if message needs action based on simple heuristics
        important_keywords = [
            'urgent', 'important', 'meeting', 'proposal', 'contract', 
            'opportunity', 'client', 'sales', 'business', 'offer',
            'whatsapp', 'message', 'contact'
        ]
        
        is_important = any(keyword in content.lower() for keyword in important_keywords)
        
        if is_important:
            # Move to Needs_Action directory
            new_filename = f"whatsapp_{message_file.name}"
            new_filepath = self.needs_action_dir / new_filename
            
            # Copy the file to Needs_Action
            with open(new_filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"Important WhatsApp message saved to Needs_Action: {new_filename}")
            return True
        
        return False
    
    def process_messages(self):
        """Process all new WhatsApp messages"""
        message_files = self.scan_inbox()
        
        for message_file in message_files:
            self.process_message(message_file)
            
            # Optionally, move processed messages to archive
            # message_file.unlink()  # Uncomment to delete after processing


def run_skill():
    """Run the WhatsApp Watcher Skill"""
    print("Running WhatsApp Watcher Skill...")
    watcher = WhatsAppWatcherSkill()
    watcher.process_messages()
    print("WhatsApp Watcher Skill completed.")


if __name__ == "__main__":
    run_skill()