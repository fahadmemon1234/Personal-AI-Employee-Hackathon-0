"""
Manual Gmail OAuth Setup
For when browser doesn't open automatically
"""

import os
import pickle
import webbrowser
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.readonly'
]

print("\n" + "="*70)
print("Gmail OAuth - Manual Authentication")
print("="*70)

if not os.path.exists('credentials.json'):
    print("\n[ERROR] credentials.json not found!")
    print("Download from Google Cloud Console first.")
    input("\nPress Enter to exit...")
    exit(1)

print("\n[OK] credentials.json found")
print("\nOpening browser for authentication...")
print("If browser doesn't open, copy the URL and paste in your browser.\n")

try:
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    
    # Try to open browser
    auth_url, _ = flow.authorization_url(prompt='consent')
    
    print("="*70)
    print("COPY THIS URL AND PASTE IN YOUR BROWSER:")
    print("="*70)
    print(auth_url)
    print("="*70)
    
    # Try to open browser
    webbrowser.open(auth_url)
    
    print("\nWaiting for authentication...")
    print("After you allow access, the browser will redirect to localhost")
    print("and this script will complete automatically.\n")
    
    # Get authorization code from user
    print("If redirect doesn't work, paste the redirect URL here:")
    redirect_url = input("Redirect URL: ").strip()
    
    if redirect_url:
        flow.fetch_token(code=redirect_url.split('code=')[1].split('&')[0] if 'code=' in redirect_url else redirect_url)
    
    # Complete OAuth
    creds = flow.run_local_server(port=0, timeout_seconds=300)
    
    # Save token
    with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)
    
    print("\n" + "="*70)
    print("[SUCCESS] Authentication completed!")
    print("="*70)
    print("\nToken saved to: token.pickle")
    print("\nNow run: python mcp_email_server.py")
    
except Exception as e:
    print(f"\n[ERROR] {e}")
    print("\nMake sure:")
    print("1. OAuth consent screen is configured")
    print("2. Your email is added as test user")
    print("3. Gmail API is enabled")

input("\nPress Enter to exit...")
