"""
Quick LinkedIn Authenticator
Authenticates and gets Person URN with proper scopes
"""

import os
import json
import datetime
import requests
import webbrowser
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlencode
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class QuickAuth:
    def __init__(self):
        self.client_id = os.getenv("LINKEDIN_CLIENT_ID", "")
        self.client_secret = os.getenv("LINKEDIN_CLIENT_SECRET", "")
        self.redirect_uri = "http://localhost:8080/callback"
        self.auth_code = None
        self.token_file = "linkedin_token.json"
    
    def get_auth_url(self):
        base_url = "https://www.linkedin.com/oauth/v2/authorization"
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": "w_member_social",
            "state": "auth_" + datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        }
        return f"{base_url}?{urlencode(params)}"
    
    def authenticate(self):
        print("="*60)
        print("LinkedIn Authentication")
        print("="*60)
        print()
        
        if not self.client_id:
            print("ERROR: LINKEDIN_CLIENT_ID not found in .env")
            return False
        
        # Generate auth URL
        auth_url = self.get_auth_url()
        print("Opening LinkedIn authorization page...")
        print(f"URL: {auth_url[:80]}...")
        
        # Start callback server
        auth_event = threading.Event()
        captured_code = [None]
        
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path.startswith('/callback'):
                    query = parse_qs(self.path.split('?')[1])
                    code = query.get('code', [''])[0]
                    if code:
                        captured_code[0] = code
                        self.send_response(200)
                        self.send_header('Content-type', 'text/html')
                        self.end_headers()
                        html = """
                        <html><body style="font-family:Arial;text-align:center;padding:50px">
                        <h1 style="color:#28a745">Authorized!</h1>
                        <p>Capturing code... You can close this window in 3 seconds.</p>
                        <script>setTimeout(function(){window.close();},3000);</script>
                        </body></html>
                        """
                        self.wfile.write(html.encode())
                        auth_event.set()
                    else:
                        self.send_response(400)
                        self.end_headers()
                else:
                    self.send_response(404)
                    self.end_headers()
            
            def log_message(self, format, *args):
                pass
        
        # Try multiple ports
        for port in [8080, 8081, 8082, 8888]:
            try:
                httpd = HTTPServer(('localhost', port), Handler)
                print(f"Server started on port {port}")
                break
            except OSError:
                print(f"Port {port} busy, trying next...")
                continue
        else:
            print("Could not start server on any port!")
            return False
        
        try:
            server_thread = threading.Thread(target=httpd.serve_forever)
            server_thread.daemon = True
            server_thread.start()
            
            # Open browser
            webbrowser.open(auth_url)
            
            print("\nWaiting for authorization (2 min timeout)...")
            if auth_event.wait(timeout=120):
                print("Authorization code received!")
                
                # Exchange for token
                token_url = "https://www.linkedin.com/oauth/v2/accessToken"
                data = {
                    "grant_type": "authorization_code",
                    "code": captured_code[0],
                    "redirect_uri": self.redirect_uri,
                    "client_id": self.client_id,
                    "client_secret": self.client_secret
                }
                
                response = requests.post(token_url, data=data)
                
                if response.status_code == 200:
                    token_data = response.json()
                    token_data["expires_at"] = datetime.datetime.now().timestamp() + token_data.get("expires_in", 3600)
                    
                    # Get person URN
                    access_token = token_data["access_token"]
                    person_urn = self.get_person_urn(access_token)
                    
                    if person_urn:
                        token_data["person_urn"] = person_urn
                        self.person_urn = person_urn
                        self.update_env(access_token, person_urn)
                    else:
                        # Save token without URN, will fetch later
                        self.update_env_token_only(access_token)
                    
                    # Save token
                    with open(self.token_file, 'w') as f:
                        json.dump(token_data, f, indent=2)
                    
                    print("\n" + "="*60)
                    print("SUCCESS!")
                    print("="*60)
                    print(f"Token saved to: {self.token_file}")
                    if person_urn:
                        print(f"Person URN: {person_urn}")
                    else:
                        print("Note: Person URN will be fetched when posting")
                    print("\nYou can now run:")
                    print("  python auto_linkedin_poster.py --post-now")
                    print("="*60)
                    return True
                else:
                    print(f"Token exchange failed: {response.text}")
                    return False
            else:
                print("Authorization timeout")
                return False
        
        finally:
            try:
                httpd.shutdown()
            except:
                pass
    
    def get_person_urn(self, access_token):
        """Get person URN - try multiple methods"""
        # Method 1: Try email endpoint (works with w_member_social)
        url = "https://api.linkedin.com/v2/emailAddress?q=members&projection=(elements*(handle~))"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "X-Restli-Protocol-Version": "2.0.0",
            "LinkedIn-Version": "202402"
        }
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                elements = data.get("elements", [])
                if elements:
                    handle = elements[0].get("handle~", {})
                    # Email se person URN nikal sakte hain
                    print(f"Email found: {handle.get('emailAddress', 'N/A')}")
        except Exception as e:
            print(f"Email endpoint error: {e}")
        
        # Method 2: Try posts endpoint to get author URN
        url = "https://api.linkedin.com/v2/posts?q=members&projection=(elements*(author))"
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                elements = data.get("elements", [])
                if elements:
                    author = elements[0].get("author", "")
                    if author.startswith("urn:li:person:"):
                        person_urn = author.replace("urn:li:person:", "")
                        print(f"Person URN from posts: {person_urn}")
                        return person_urn
        except Exception as e:
            print(f"Posts endpoint error: {e}")
        
        # Method 3: Use a default/fallback approach
        # For w_member_social, we can use 'me' as placeholder
        print("Using default person URN approach...")
        return None
    
    def update_env(self, token, person_urn):
        env_path = Path(".env")
        if env_path.exists():
            with open(env_path, 'r') as f:
                lines = f.readlines()
            
            for i, line in enumerate(lines):
                if line.startswith("LINKEDIN_ACCESS_TOKEN="):
                    lines[i] = f"LINKEDIN_ACCESS_TOKEN={token}\n"
                elif line.startswith("LINKEDIN_PERSON_URN="):
                    lines[i] = f"LINKEDIN_PERSON_URN={person_urn}\n"
            
            with open(env_path, 'w') as f:
                f.writelines(lines)
    
    def update_env_token_only(self, token):
        """Update only access token in .env"""
        env_path = Path(".env")
        if env_path.exists():
            with open(env_path, 'r') as f:
                lines = f.readlines()
            
            for i, line in enumerate(lines):
                if line.startswith("LINKEDIN_ACCESS_TOKEN="):
                    lines[i] = f"LINKEDIN_ACCESS_TOKEN={token}\n"
                    break
            
            with open(env_path, 'w') as f:
                f.writelines(lines)


if __name__ == "__main__":
    auth = QuickAuth()
    auth.authenticate()
