"""
Gmail Watcher Script
Monitors Gmail for important unread emails and saves them as .md files in /Needs_Action
"""

import os
import json
import pickle
import base64
from datetime import datetime
from pathlib import Path
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class GmailWatcher:
    """Watches Gmail for important unread emails and saves them as .md files"""
    
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    
    def __init__(self, credentials_file=None, token_file=None):
        # Load from environment variables if not provided
        self.credentials_file = credentials_file or os.getenv("GMAIL_CREDENTIALS_FILE", "credentials.json")
        self.token_file = token_file or os.getenv("GMAIL_TOKEN_FILE", "token.pickle")
        self.service = None
        self.needs_action_path = Path(os.getenv("NEEDS_ACTION_DIR", "Needs_Action"))
        self.watch_interval = int(os.getenv("GMAIL_WATCH_INTERVAL", "300"))

        # Create Needs_Action directory if it doesn't exist
        self.needs_action_path.mkdir(exist_ok=True)
        
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
    
    def get_unread_emails(self, query="is:unread"):
        """Get unread emails from Gmail"""
        try:
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=10  # Limit to 10 newest emails
            ).execute()
            
            messages = results.get('messages', [])
            return messages
        except Exception as e:
            print(f"Error retrieving emails: {e}")
            return []
    
    def get_email_details(self, msg_id):
        """Get detailed information about a specific email"""
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=msg_id,
                format='full'
            ).execute()
            
            # Extract headers and payload
            headers = message['payload'].get('headers', [])
            subject = ''
            sender = ''
            
            for header in headers:
                if header['name'].lower() == 'subject':
                    subject = header['value']
                elif header['name'].lower() == 'from':
                    sender = header['value']
            
            # Extract body
            body = self.extract_body(message)
            
            return {
                'id': msg_id,
                'subject': subject,
                'sender': sender,
                'body': body,
                'timestamp': datetime.now().isoformat(),
                'raw_message': message
            }
        except Exception as e:
            print(f"Error getting email details: {e}")
            return None
    
    def extract_body(self, message):
        """Extract the body of the email"""
        body = ""
        payload = message.get('payload', {})
        parts = payload.get('parts', [])
        
        if parts:
            for part in parts:
                if part.get('mimeType') == 'text/plain':
                    body_data = part.get('body', {}).get('data', '')
                    if body_data:
                        body = base64.urlsafe_b64decode(body_data).decode('utf-8')
                        break
        else:
            # For simple messages without parts
            body_data = payload.get('body', {}).get('data', '')
            if body_data:
                body = base64.urlsafe_b64decode(body_data).decode('utf-8')
        
        return body
    
    def save_email_as_md(self, email_data):
        """Save email data as a markdown file in Needs_Action folder"""
        if not email_data:
            return

        # Create a safe filename from the subject
        safe_subject = "".join(c for c in email_data['subject'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
        if not safe_subject:
            safe_subject = "email_no_subject"

        # Add timestamp to filename to avoid conflicts
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"email_{safe_subject}_{timestamp}.md"
        filepath = self.needs_action_path / filename

        # Create markdown content
        md_content = f"""# Email from {email_data['sender']}

**Subject:** {email_data['subject']}

**Received:** {email_data['timestamp']}

**Email ID:** {email_data['id']}

---

## Message Body:

{email_data['body']}

---

*This email was automatically saved by the Gmail Watcher*
"""

        # Write the markdown file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(md_content)

        # Use safe print for Windows console
        try:
            print(f"Saved email '{email_data['subject']}' to {filepath}")
        except UnicodeEncodeError:
            safe_subject = email_data['subject'].encode('ascii', 'replace').decode('ascii')
            print(f"Saved email '{safe_subject}' to {filepath}")

        # Log the action to Audit_Log.md
        self.log_action(f"Gmail Watcher processed email: {email_data['subject']}")

    def log_action(self, action_description):
        """Log an action to Audit_Log.md"""
        audit_log_path = Path("Audit_Log.md")
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        log_entry = f"- [{timestamp}] {action_description}\n"
        
        # Append the log entry to the audit log file
        with open(audit_log_path, 'a', encoding='utf-8') as f:
            f.write(log_entry)

    def mark_as_read(self, msg_id):
        """Mark an email as read"""
        try:
            # Modify the message to remove the UNREAD label
            self.service.users().messages().modify(
                userId='me',
                id=msg_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            print(f"Marked email {msg_id} as read")
        except Exception as e:
            print(f"Error marking email as read: {e}")
    
    def process_new_emails(self):
        """Process all new unread emails"""
        if not self.service:
            print("Not authenticated. Please authenticate first.")
            self.log_action("Gmail Watcher failed to authenticate")
            return

        messages = self.get_unread_emails()
        print(f"Found {len(messages)} unread emails")
        
        if messages:
            self.log_action(f"Gmail Watcher found {len(messages)} unread emails")
        else:
            self.log_action("Gmail Watcher found no new emails")

        for msg in messages:
            email_data = self.get_email_details(msg['id'])
            if email_data:
                self.save_email_as_md(email_data)
                # Optionally mark as read after processing
                # self.mark_as_read(msg['id'])
    
    def start_monitoring(self, interval=None):  # Default to checking every 5 minutes
        """Start monitoring for new emails at regular intervals"""
        check_interval = interval or self.watch_interval
        print(f"Starting Gmail monitoring (checking every {check_interval} seconds)")

        if not self.authenticate():
            print("Authentication failed. Cannot start monitoring.")
            return

        try:
            while True:
                self.process_new_emails()
                print(f"Waiting {check_interval} seconds before next check...")
                time.sleep(check_interval)
        except KeyboardInterrupt:
            print("\nStopping Gmail monitoring...")


def main():
    """Main function to run the Gmail watcher"""
    import sys
    import codecs
    
    # Fix Unicode encoding for Windows console
    if sys.platform == 'win32':
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    
    print("Initializing Gmail Watcher...")

    # Initialize the watcher
    watcher = GmailWatcher()

    # For demonstration, we'll process emails once
    # In a real scenario, you'd call watcher.start_monitoring() to run continuously
    if watcher.authenticate():
        print("Authentication successful!")
        watcher.process_new_emails()
        print("Email processing complete.")
    else:
        print("Authentication failed. Please set up your credentials.")


if __name__ == "__main__":
    main()