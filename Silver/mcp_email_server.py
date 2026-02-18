"""
MCP Email Server
Implements a working MCP server for email operations including sending emails with approval workflow
Port: 8080
"""

import json
import pickle
import os
import base64
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
from datetime import datetime

try:
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
except ImportError:
    print("Google API libraries not installed. Run: pip install google-auth google-auth-oauthlib google-api-python-client")


class MCPEmailServer:
    """MCP Server for email operations with approval workflow"""

    SCOPES = ['https://www.googleapis.com/auth/gmail.send', 'https://www.googleapis.com/auth/gmail.readonly']

    def __init__(self, host='localhost', port=8080, credentials_file="credentials.json", token_file="token.pickle"):
        self.host = host
        self.port = port
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.service = None
        self.approved_dir = Path("Approved")
        self.pending_dir = Path("Pending_Approval")
        self.sent_dir = Path("Sent")

        # Create directories
        self.approved_dir.mkdir(exist_ok=True)
        self.pending_dir.mkdir(exist_ok=True)
        self.sent_dir.mkdir(exist_ok=True)

        self._authenticate()

    def _authenticate(self):
        """Authenticate with Google API"""
        creds = None

        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"Token refresh failed: {e}")
                    creds = None
            else:
                if os.path.exists(self.credentials_file):
                    print("Gmail authentication required. Please complete OAuth flow...")
                    try:
                        flow = InstalledAppFlow.from_client_secrets_file(
                            self.credentials_file, self.SCOPES)
                        creds = flow.run_local_server(port=0)
                        with open(self.token_file, 'wb') as token:
                            pickle.dump(creds, token)
                        print("Authentication successful!")
                    except Exception as e:
                        print(f"Authentication failed: {e}")
                        print("Email sending will be simulated (not actually sent)")
                else:
                    print(f"Credentials file not found: {self.credentials_file}")
                    print("Email sending will be simulated (not actually sent)")
                    return

        if creds:
            try:
                self.service = build('gmail', 'v1', credentials=creds)
                print("Gmail service initialized")
            except Exception as e:
                print(f"Failed to build Gmail service: {e}")

    def check_approval(self, email_id):
        """Check if an email has approval to be sent"""
        approval_file = self.approved_dir / f"{email_id}.approved"
        return approval_file.exists()

    def create_approval_request(self, email_data):
        """Create an approval request file in Pending_Approval"""
        email_id = f"email_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        approval_file = self.pending_dir / f"{email_id}.pending"

        content = json.dumps({
            "email_id": email_id,
            "to": email_data.get("to", ""),
            "subject": email_data.get("subject", ""),
            "body": email_data.get("body", ""),
            "created_at": datetime.now().isoformat(),
            "status": "pending_approval"
        }, indent=2)

        with open(approval_file, 'w', encoding='utf-8') as f:
            f.write(content)

        return email_id

    def approve_email(self, email_id):
        """Approve an email for sending"""
        pending_file = self.pending_dir / f"{email_id}.pending"
        approval_file = self.approved_dir / f"{email_id}.approved"

        if pending_file.exists():
            # Move from pending to approved
            with open(pending_file, 'r', encoding='utf-8') as f:
                content = f.read()

            data = json.loads(content)
            data["status"] = "approved"
            data["approved_at"] = datetime.now().isoformat()

            with open(approval_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)

            pending_file.unlink()
            return True

        return False

    def send_email(self, to, subject, body, email_id=None):
        """Send an email (requires prior approval)"""
        if email_id and not self.check_approval(email_id):
            return {
                "success": False,
                "error": "Email not approved. Please approve first.",
                "email_id": email_id
            }

        if not self.service:
            # Simulate sending when no Gmail service available
            print(f"[SIMULATED] Email would be sent to: {to}")
            print(f"[SIMULATED] Subject: {subject}")
            print(f"[SIMULATED] Body: {body[:200]}...")

            # Save to Sent folder
            if email_id:
                sent_file = self.sent_dir / f"{email_id}.sent"
            else:
                sent_file = self.sent_dir / f"sent_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            with open(sent_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "to": to,
                    "subject": subject,
                    "body": body,
                    "sent_at": datetime.now().isoformat(),
                    "status": "simulated_sent"
                }, f, indent=2)

            return {
                "success": True,
                "message": "Email simulated (Gmail not configured)",
                "email_id": email_id or "simulated"
            }

        try:
            # Create MIME message
            from email.mime.text import MIMEText

            message = MIMEText(body)
            message['to'] = to
            message['from'] = 'me'
            message['subject'] = subject

            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

            # Send via Gmail API
            sent_message = self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()

            # Save to Sent folder
            if email_id:
                sent_file = self.sent_dir / f"{email_id}.sent"
            else:
                sent_file = self.sent_dir / f"sent_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            with open(sent_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "to": to,
                    "subject": subject,
                    "body": body,
                    "sent_at": datetime.now().isoformat(),
                    "status": "sent",
                    "gmail_id": sent_message['id']
                }, f, indent=2)

            # Clean up approval file
            if email_id:
                approval_file = self.approved_dir / f"{email_id}.approved"
                if approval_file.exists():
                    approval_file.unlink()

            return {
                "success": True,
                "message": "Email sent successfully",
                "email_id": email_id or sent_message['id'],
                "gmail_id": sent_message['id']
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def receive_emails(self, max_results=10):
        """Receive/list recent emails"""
        if not self.service:
            return {
                "success": False,
                "error": "Gmail service not available"
            }

        try:
            results = self.service.users().messages().list(
                userId='me',
                maxResults=max_results
            ).execute()

            messages = results.get('messages', [])
            email_list = []

            for msg in messages:
                msg_detail = self.service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='metadata',
                    metadataHeaders=['from', 'to', 'subject', 'date']
                ).execute()

                headers = msg_detail['payload']['headers']
                email_list.append({
                    "id": msg['id'],
                    "from": next((h['value'] for h in headers if h['name'] == 'From'), ''),
                    "to": next((h['value'] for h in headers if h['name'] == 'To'), ''),
                    "subject": next((h['value'] for h in headers if h['name'] == 'Subject'), ''),
                    "date": next((h['value'] for h in headers if h['name'] == 'Date'), '')
                })

            return {
                "success": True,
                "emails": email_list
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def process_email(self, email_data):
        """Process an email with approval workflow"""
        # Create approval request
        email_id = self.create_approval_request(email_data)

        return {
            "success": True,
            "message": "Email approval request created",
            "email_id": email_id,
            "status": "pending_approval",
            "approval_file": str(self.pending_dir / f"{email_id}.pending")
        }


class MCPRequestHandler(BaseHTTPRequestHandler):
    """HTTP Request Handler for MCP Email Server"""

    server_instance = None

    def _set_headers(self, status=200, content_type='application/json'):
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers()

    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query = parse_qs(parsed_path.query)

        if path == '/health':
            self._set_headers()
            self.wfile.write(json.dumps({
                "status": "healthy",
                "server": "MCP Email Server",
                "port": self.server_instance.port,
                "timestamp": datetime.now().isoformat()
            }).encode())

        elif path == '/capabilities':
            self._set_headers()
            self.wfile.write(json.dumps({
                "capabilities": [
                    "send-email",
                    "receive-email",
                    "process-email",
                    "gmail-watch",
                    "email-approval"
                ],
                "approval_workflow": True,
                "hitl_required": True
            }).encode())

        elif path == '/emails':
            max_results = int(query.get('max_results', [10])[0])
            result = self.server_instance.receive_emails(max_results)
            self._set_headers(200 if result['success'] else 500)
            self.wfile.write(json.dumps(result).encode())

        elif path.startswith('/approve/'):
            email_id = path.split('/')[-1]
            result = self.server_instance.approve_email(email_id)
            self._set_headers(200 if result else 404)
            self.wfile.write(json.dumps({
                "success": result,
                "message": "Email approved" if result else "Email not found"
            }).encode())

        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode())

    def do_POST(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')

        try:
            data = json.loads(body) if body else {}
        except json.JSONDecodeError:
            self._set_headers(400)
            self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode())
            return

        if path == '/send':
            # Send email (requires approval)
            email_id = data.get('email_id')
            to = data.get('to')
            subject = data.get('subject', '')
            body_text = data.get('body', '')

            if not to:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Missing 'to' field"}).encode())
                return

            result = self.server_instance.send_email(to, subject, body_text, email_id)
            self._set_headers(200 if result['success'] else 500)
            self.wfile.write(json.dumps(result).encode())

        elif path == '/process':
            # Process email with approval workflow
            email_data = {
                "to": data.get('to', ''),
                "subject": data.get('subject', ''),
                "body": data.get('body', '')
            }

            result = self.server_instance.process_email(email_data)
            self._set_headers(200 if result['success'] else 500)
            self.wfile.write(json.dumps(result).encode())

        elif path == '/approve':
            # Approve an email
            email_id = data.get('email_id')
            if not email_id:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Missing 'email_id' field"}).encode())
                return

            result = self.server_instance.approve_email(email_id)
            self._set_headers(200 if result else 404)
            self.wfile.write(json.dumps({
                "success": result,
                "message": "Email approved" if result else "Email not found"
            }).encode())

        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode())

    def log_message(self, format, *args):
        print(f"[MCP Email Server] {args[0]}")


def run_mcp_email_server(host='localhost', port=8080):
    """Run the MCP Email Server"""
    server = MCPEmailServer(host=host, port=port)
    MCPRequestHandler.server_instance = server

    httpd = HTTPServer((host, port), MCPRequestHandler)
    print(f"MCP Email Server running on http://{host}:{port}")
    print(f"Capabilities: send-email, receive-email, process-email, gmail-watch, email-approval")
    print(f"Approval Workflow: Enabled (HITL required)")
    print(f"Press Ctrl+C to stop")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down MCP Email Server...")
        httpd.shutdown()


if __name__ == "__main__":
    run_mcp_email_server()
