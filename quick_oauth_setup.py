"""
Quick Gmail OAuth Setup
Run this and follow browser prompts
"""

import os
import pickle
import sys
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.readonly'
]

print("\n" + "="*70)
print("Gmail OAuth Authentication")
print("="*70)

# Check for credentials
if not os.path.exists('credentials.json'):
    print("\n[ERROR] credentials.json not found!")
    print("Please download from Google Cloud Console first.")
    sys.exit(1)

print("\n[OK] credentials.json found")

# Check for existing token
if os.path.exists('token.pickle'):
    print("[OK] Existing token found")
    try:
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
        if creds and creds.valid:
            print("\n[SUCCESS] Token is valid! Email MCP ready to use.")
            sys.exit(0)
        else:
            print("[INFO] Token expired, will refresh...")
    except Exception as e:
        print(f"[WARN] Could not read token: {e}")

print("\n" + "-"*70)
print("Opening browser for Gmail authentication...")
print("-"*70)
print("\nINSTRUCTIONS:")
print("1. Browser will open automatically")
print("2. Login with your Gmail account")
print("3. Click 'Allow' to grant permissions")
print("4. Come back here when done\n")

try:
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    creds = flow.run_local_server(port=0, timeout_seconds=300)
    
    # Save token
    with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)
    
    print("\n" + "="*70)
    print("[SUCCESS] Authentication completed!")
    print("="*70)
    print("\nNext steps:")
    print("1. Start Email MCP Server: python mcp_email_server.py")
    print("2. Send test email via API")
    print("\nDone! You can now send emails via MCP Email Server.")
    
except Exception as e:
    print(f"\n[ERROR] Authentication failed: {e}")
    print("\nTroubleshooting:")
    print("1. Make sure Gmail API is enabled in Google Cloud Console")
    print("2. Check OAuth consent screen is configured")
    print("3. Add your email as test user")
    print("4. Try again: python setup_gmail_oauth.py")
