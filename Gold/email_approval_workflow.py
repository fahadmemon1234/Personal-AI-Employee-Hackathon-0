"""
Email Sender with Approval Workflow
Only sends emails after approval file is placed in /Approved directory
"""

import os
import json
import pickle
import time
from pathlib import Path
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import base64


class EmailSenderWithApproval:
    """Email sender that requires approval before sending emails"""
    
    SCOPES = ['https://www.googleapis.com/auth/gmail.send', 'https://www.googleapis.com/auth/gmail.readonly']
    
    def __init__(self, credentials_file="credentials.json", token_file="token.pickle", approved_dir="Approved"):
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.approved_dir = Path(approved_dir)
        self.service = None
        
        # Create approved directory if it doesn't exist
        self.approved_dir.mkdir(exist_ok=True)
    
    def authenticate(self):
        """Authenticate with Google API using OAuth2"""
        creds = None
        
        # Load existing token if available
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)
        
        # If no valid credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_file):
                    print(f"Credentials file {self.credentials_file} not found.")
                    print("Please download it from https://console.cloud.google.com/apis/credentials")
                    return False
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save credentials for next run
            with open(self.token_file, 'wb') as token:
                pickle.dump(creds, token)
        
        self.service = build('gmail', 'v1', credentials=creds)
        return True
    
    def has_approval(self):
        """Check if there's an approval file in the Approved directory"""
        approval_files = list(self.approved_dir.glob("*"))
        return len(approval_files) > 0
    
    def clear_approvals(self):
        """Remove all approval files after processing"""
        for approval_file in self.approved_dir.glob("*"):
            approval_file.unlink()
    
    def create_message(self, sender, to, subject, message_text):
        """Create a message for an email"""
        message = MIMEText(message_text)
        message['to'] = to
        message['from'] = sender
        message['subject'] = subject
        
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        return {'raw': raw_message}
    
    def send_email(self, to, subject, message_text):
        """Send an email if approval is present"""
        if not self.service:
            print("Not authenticated. Please authenticate first.")
            return False
        
        if not self.has_approval():
            print("No approval found. Cannot send email.")
            print("To approve, create any file in the Approved directory.")
            return False
        
        try:
            # Create the message
            message = self.create_message('me', to, subject, message_text)
            
            # Send the message
            sent_message = self.service.users().messages().send(
                userId='me',
                body=message
            ).execute()
            
            print(f"Message sent successfully! Message Id: {sent_message['id']}")
            
            # Clear approvals after sending
            self.clear_approvals()
            
            return True
        except Exception as e:
            print(f"An error occurred while sending email: {e}")
            return False
    
    def send_email_from_file(self, email_request_file):
        """Send an email based on a request file in Needs_Action"""
        if not self.has_approval():
            print("No approval found. Cannot process email request.")
            return False
        
        try:
            # Read the email request file
            with open(email_request_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # For now, we'll just send the content as the email body
            # In a real implementation, you'd parse the file for recipient, subject, etc.
            lines = content.split('\n')
            subject = f"Automated Response: {lines[0]}" if lines[0].strip() else "Automated Response"
            message_text = content
            
            # Send to a default address or parse from the file
            # For demo purposes, we'll use a placeholder
            recipient = "recipient@example.com"  # This would be parsed from the file in a real implementation
            
            success = self.send_email(recipient, subject, message_text)
            if success:
                # Move the request file to completed after sending
                completed_dir = Path("Completed")
                completed_dir.mkdir(exist_ok=True)
                completed_path = completed_dir / email_request_file.name
                Path(email_request_file).rename(completed_path)
                print(f"Email request processed and moved to {completed_path}")
            
            return success
        except Exception as e:
            print(f"Error processing email request file: {e}")
            return False


class ApprovalBasedEmailProcessor:
    """Processes email requests from Needs_Action only after approval"""
    
    def __init__(self):
        self.email_sender = EmailSenderWithApproval()
        self.needs_action_dir = Path("Needs_Action")
        self.approved_dir = Path("Approved")
        
    def authenticate(self):
        """Authenticate the email sender"""
        return self.email_sender.authenticate()
    
    def scan_for_email_requests(self):
        """Scan Needs_Action for email request files"""
        if not self.needs_action_dir.exists():
            return []
        
        # Look for files that appear to be email requests (could be .md, .txt, etc.)
        email_request_files = []
        for file_path in self.needs_action_dir.glob("*"):
            if file_path.suffix.lower() in ['.md', '.txt']:
                # Simple heuristic: if the file contains email-like content
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read().lower()
                        # If it looks like it might be an email request
                        if any(keyword in content for keyword in ['email', 'send', 'to:', 'from:', 'subject']):
                            email_request_files.append(file_path)
                except:
                    # If we can't read the file, skip it
                    continue
        
        return email_request_files
    
    def process_email_requests(self):
        """Process all email requests that have approval"""
        if not self.email_sender.has_approval():
            print("No approval found. Cannot process email requests.")
            return False
        
        email_requests = self.scan_for_email_requests()
        if not email_requests:
            print("No email requests found.")
            return True
        
        print(f"Processing {len(email_requests)} email requests...")
        
        success_count = 0
        for request_file in email_requests:
            print(f"Processing email request: {request_file.name}")
            if self.email_sender.send_email_from_file(request_file):
                success_count += 1
        
        print(f"Processed {success_count}/{len(email_requests)} email requests successfully.")
        return True
    
    def run_monitoring_loop(self, interval=10):
        """Run a continuous monitoring loop for email requests and approvals"""
        print("Starting email approval monitoring loop...")
        
        if not self.authenticate():
            print("Authentication failed. Cannot start monitoring.")
            return
        
        try:
            while True:
                if self.email_sender.has_approval():
                    print("Approval detected. Processing email requests...")
                    self.process_email_requests()
                
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\nEmail monitoring loop stopped by user.")


def main():
    """Main function to demonstrate the approval-based email processor"""
    print("Initializing Approval-Based Email Processor...")
    
    processor = ApprovalBasedEmailProcessor()
    
    # Authenticate first
    if processor.authenticate():
        print("Authentication successful!")
        
        # For demonstration, we'll process once
        if processor.email_sender.has_approval():
            print("Approval found. Processing email requests...")
            processor.process_email_requests()
        else:
            print("No approval found. Place a file in the Approved directory to allow sending emails.")
    else:
        print("Authentication failed. Please set up your credentials.")


if __name__ == "__main__":
    main()