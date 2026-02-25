"""
Gmail OAuth Setup Script
Run this once to authenticate with Gmail
"""

import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

# Gmail API scopes
SCOPES = [
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.readonly'
]

def main():
    print("="*60)
    print("Gmail OAuth Setup")
    print("="*60)
    
    creds = None
    token_file = "token.pickle"
    credentials_file = "credentials.json"
    
    # Check if token exists
    if os.path.exists(token_file):
        print(f"\nFound existing token: {token_file}")
        with open(token_file, 'rb') as token:
            creds = pickle.load(token)
    
    # If no valid credentials, authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("\nRefreshing token...")
            try:
                creds.refresh(Request())
                print("Token refreshed!")
            except Exception as e:
                print(f"Token refresh failed: {e}")
                creds = None
        
        if not creds:
            # Check for credentials file
            if not os.path.exists(credentials_file):
                print(f"\n❌ Error: {credentials_file} not found!")
                print("\nSteps to get credentials:")
                print("1. Go to https://console.cloud.google.com/")
                print("2. Create a new project")
                print("3. Enable Gmail API")
                print("4. Create OAuth 2.0 Client ID credentials")
                print("5. Download credentials.json")
                print("6. Save it as 'credentials.json' in this folder")
                return
            
            print("\nStarting OAuth flow...")
            print("A browser window will open for Gmail login")
            print("Please complete the authentication...")
            
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_file, SCOPES)
                creds = flow.run_local_server(port=0)
                
                # Save token
                with open(token_file, 'wb') as token:
                    pickle.dump(creds, token)
                
                print("\n✅ Authentication successful!")
                print(f"Token saved to: {token_file}")
                print("\nYou can now use MCP Email Server!")
                
            except Exception as e:
                print(f"\n❌ Authentication failed: {e}")
                print("\nPlease check:")
                print("1. credentials.json is valid")
                print("2. Gmail API is enabled in Google Cloud Console")
                print("3. OAuth consent screen is configured")
    else:
        print("\n✅ Existing token is valid!")
        print("You can now use MCP Email Server!")

if __name__ == "__main__":
    main()
