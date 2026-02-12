"""
Gmail Watcher Skill
Monitors Gmail for new emails and processes them according to business rules.
"""
import os
import json
from pathlib import Path
import base64
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class GmailWatcherSkill:
    def __init__(self):
        self.creds = None
        self.SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
        self.service = None
        
    def authenticate(self):
        """Authenticate with Gmail API"""
        creds = None
        
        # Load existing credentials
        if os.path.exists("token.pickle"):
            with open("token.pickle", "rb") as token:
                creds = pickle.load(token)
        
        # Refresh or get new credentials if needed
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = Flow.from_client_secrets_file(
                    "credentials.json",
                    scopes=self.SCOPES,
                    redirect_uri="urn:ietf:wg:oauth:2.0:oob"
                )
                flow.run_console()
                creds = flow.credentials
            
            # Save credentials for next run
            with open("token.pickle", "wb") as token:
                pickle.dump(creds, token)
        
        self.creds = creds
        self.service = build("gmail", "v1", credentials=creds)
    
    def get_recent_emails(self, max_results=10):
        """Get recent emails from Gmail"""
        if not self.service:
            self.authenticate()
        
        try:
            # Call the Gmail API
            results = self.service.users().messages().list(
                userId="me", maxResults=max_results
            ).execute()
            messages = results.get("messages", [])
            
            emails = []
            for msg in messages:
                msg_detail = self.service.users().messages().get(
                    userId="me", id=msg['id']
                ).execute()
                
                # Extract email headers
                headers = msg_detail['payload']['headers']
                subject = next((header['value'] for header in headers if header['name'] == 'Subject'), 'No Subject')
                sender = next((header['value'] for header in headers if header['name'] == 'From'), 'Unknown Sender')
                
                # Extract email body
                body = ""
                if 'parts' in msg_detail['payload']:
                    for part in msg_detail['payload']['parts']:
                        if part['mimeType'] == 'text/plain':
                            body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                            break
                else:
                    if 'body' in msg_detail['payload'] and 'data' in msg_detail['payload']['body']:
                        body = base64.urlsafe_b64decode(msg_detail['payload']['body']['data']).decode('utf-8')
                
                email_data = {
                    'id': msg['id'],
                    'subject': subject,
                    'sender': sender,
                    'body': body[:500] + "..." if len(body) > 500 else body  # Truncate long bodies
                }
                emails.append(email_data)
            
            return emails
        except HttpError as error:
            print(f"An error occurred: {error}")
            return []
    
    def process_emails(self):
        """Process recent emails and move important ones to Needs_Action"""
        emails = self.get_recent_emails()
        
        needs_action_dir = Path("Needs_Action")
        needs_action_dir.mkdir(exist_ok=True)
        
        for email in emails:
            # Determine if email needs action based on simple heuristics
            content = f"From: {email['sender']}\nSubject: {email['subject']}\n\n{email['body']}"
            
            # Keywords that indicate importance
            important_keywords = [
                'urgent', 'important', 'meeting', 'proposal', 'contract', 
                'opportunity', 'client', 'sales', 'business', 'offer'
            ]
            
            is_important = any(keyword in content.lower() for keyword in important_keywords)
            
            if is_important:
                # Create a file in Needs_Action directory
                filename = f"email_{email['subject'].replace(' ', '_').replace('/', '_')}_{email['id'][:8]}.txt"
                filepath = needs_action_dir / filename
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"Important email saved to Needs_Action: {filename}")


def run_skill():
    """Run the Gmail Watcher Skill"""
    print("Running Gmail Watcher Skill...")
    watcher = GmailWatcherSkill()
    watcher.process_emails()
    print("Gmail Watcher Skill completed.")


if __name__ == "__main__":
    run_skill()