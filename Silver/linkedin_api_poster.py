"""
LinkedIn API Poster
Posts content to LinkedIn using the official LinkedIn API v2
"""

import os
import json
import datetime
import requests
import webbrowser
import threading
from pathlib import Path
from urllib.parse import urlencode, parse_qs
from http.server import HTTPServer, BaseHTTPRequestHandler
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class LinkedInAPIPoster:
    """Posts content to LinkedIn using the official API"""

    def __init__(self, config_file="linkedin_config.json"):
        self.config_file = config_file
        self.token_file = "linkedin_token.json"
        self.pending_approval_dir = Path("Pending_Approval")
        self.posted_dir = Path("Posted")
        self.dashboard_file = "Dashboard.md"
        self.auth_code = None

        # Create directories if they don't exist
        self.pending_approval_dir.mkdir(exist_ok=True)
        self.posted_dir.mkdir(exist_ok=True)

        # Load configuration
        self.config = self.load_config()


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """HTTP server to handle OAuth2 callback from LinkedIn"""
    
    def __init__(self, *args, callback_func=None, **kwargs):
        self.callback_func = callback_func
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        # Parse the authorization code from the redirect URL
        if self.path.startswith('/callback'):
            query_components = parse_qs(self.path.split('?')[1])
            code = query_components.get('code', [''])[0]
            
            if code:
                # Send success response
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                
                html = """
                <!DOCTYPE html>
                <html>
                <head>
                    <title>LinkedIn Authentication Successful</title>
                    <style>
                        body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                        .success { color: #28a745; }
                        .info { color: #666; margin-top: 20px; }
                    </style>
                </head>
                <body>
                    <h1 class="success">✓ Authentication Successful!</h1>
                    <p>You can close this window and return to the terminal.</p>
                    <p class="info">Authorization code captured.</p>
                </body>
                </html>
                """
                self.wfile.write(html.encode())
                
                # Store the code
                if self.callback_func:
                    self.callback_func(code)
            else:
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b"Authorization failed. Please try again.")
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        # Suppress server log messages
        pass


def create_handler(callback_func):
    """Factory function to create handler with callback"""
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path.startswith('/callback'):
                query_components = parse_qs(self.path.split('?')[1])
                code = query_components.get('code', [''])[0]
                
                if code:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    
                    html = """
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <title>LinkedIn Authentication Successful</title>
                        <style>
                            body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                            .success { color: #28a745; }
                            .info { color: #666; margin-top: 20px; }
                        </style>
                    </head>
                    <body>
                        <h1 class="success">✓ Authentication Successful!</h1>
                        <p>You can close this window and return to the terminal.</p>
                        <p class="info">Authorization code captured.</p>
                    </body>
                    </html>
                    """
                    self.wfile.write(html.encode())
                    callback_func(code)
                else:
                    self.send_response(400)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(b"Authorization failed. Please try again.")
            else:
                self.send_response(404)
                self.end_headers()
        
        def log_message(self, format, *args):
            pass
    
    return Handler


class LinkedInAPIPoster:
    """Posts content to LinkedIn using the official API"""

    def __init__(self, token_file="linkedin_token.json"):
        self.token_file = token_file
        self.pending_approval_dir = Path("Pending_Approval")
        self.posted_dir = Path("Posted")
        self.dashboard_file = "Dashboard.md"
        self.auth_code = None

        # Load credentials from .env file
        self.client_id = os.getenv("LINKEDIN_CLIENT_ID", "")
        self.client_secret = os.getenv("LINKEDIN_CLIENT_SECRET", "")
        self.redirect_uri = os.getenv("LINKEDIN_REDIRECT_URI", "http://localhost:8080/callback")
        self.access_token = os.getenv("LINKEDIN_ACCESS_TOKEN", "")
        self.person_urn = os.getenv("LINKEDIN_PERSON_URN", "")

        # Create directories if they don't exist
        self.pending_approval_dir.mkdir(exist_ok=True)
        self.posted_dir.mkdir(exist_ok=True)

    def get_authorization_url(self):
        """Generate LinkedIn OAuth2 authorization URL"""
        base_url = "https://www.linkedin.com/oauth/v2/authorization"
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": "w_member_social",
            "state": "unique_state_" + datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        }
        return f"{base_url}?{urlencode(params)}"

    def authenticate(self, authorization_code):
        """Exchange authorization code for access token"""
        token_url = "https://www.linkedin.com/oauth/v2/accessToken"
        data = {
            "grant_type": "authorization_code",
            "code": authorization_code,
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }

        response = requests.post(token_url, data=data)
        
        if response.status_code == 200:
            token_data = response.json()
            # Add expiration timestamp
            token_data["expires_at"] = datetime.datetime.now().timestamp() + token_data.get("expires_in", 3600)
            self.save_token(token_data)
            print("Authentication successful!")
            
            # Get person URN for posting
            self.get_person_urn(token_data["access_token"])
            
            return True
        else:
            print(f"Authentication failed: {response.text}")
            return False

    def save_token(self, token_data):
        """Save access token to file"""
        with open(self.token_file, 'w', encoding='utf-8') as f:
            json.dump(token_data, f, indent=2)
        print(f"Token saved to {self.token_file}")

    def load_token(self):
        """Load access token from file"""
        if os.path.exists(self.token_file):
            with open(self.token_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None

    def is_token_valid(self, token_data):
        """Check if token is still valid"""
        if not token_data:
            # Check if we have a token in .env
            if self.access_token:
                print("Using access token from .env file")
                # Try to get person URN if not available
                if not self.person_urn:
                    self.get_person_urn(self.access_token)
                return bool(self.person_urn)
            return False
        
        # Check if token has expiration
        if "expires_at" in token_data:
            expires_at = token_data.get("expires_at", 0)
            current_time = datetime.datetime.now().timestamp()
            if current_time >= expires_at:
                print("Token expired. Please re-authenticate.")
                return False
        
        return True

    def get_access_token(self):
        """Get the current access token"""
        # First check .env
        if self.access_token:
            return self.access_token
        
        # Then check token file
        token_data = self.load_token()
        if token_data and "access_token" in token_data:
            return token_data["access_token"]
        
        return None

    def get_person_urn(self, access_token):
        """Get the user's person URN (required for posting)"""
        # Try multiple approaches to get person URN
        
        # Approach 1: Try /me endpoint (requires r_basicprofile)
        url = "https://api.linkedin.com/v2/me"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "X-Restli-Protocol-Version": "2.0.0"
        }

        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            person_urn = data.get("id", "")
            self.person_urn = person_urn
            self.save_person_urn_to_env(person_urn)
            print(f"Person URN: {person_urn}")
            return person_urn
        
        # Approach 2: Try to get from token introspection
        print("Trying alternative method to get person URN...")
        
        # Approach 3: Use vanity name lookup
        url = "https://api.linkedin.com/v2/me?vanityName=me"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            person_urn = data.get("id", "")
            self.person_urn = person_urn
            self.save_person_urn_to_env(person_urn)
            print(f"Person URN: {person_urn}")
            return person_urn
        
        # If all fails, ask user to manually provide URN
        print("\nCould not automatically get Person URN.")
        print("You can find it manually:")
        print("1. Go to your LinkedIn profile")
        print("2. Look at the URL: https://www.linkedin.com/in/your-name/")
        print("3. Or run this curl command:")
        print('   curl -H "Authorization: Bearer YOUR_TOKEN" https://api.linkedin.com/v2/me')
        print("\nThen add LINKEDIN_PERSON_URN=your_urn to .env file")
        
        return None

    def save_person_urn_to_env(self, person_urn):
        """Save person URN to .env file"""
        env_path = Path(".env")
        if env_path.exists():
            # Read existing .env content
            with open(env_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Update or add LINKEDIN_PERSON_URN
            found = False
            for i, line in enumerate(lines):
                if line.startswith("LINKEDIN_PERSON_URN="):
                    lines[i] = f"LINKEDIN_PERSON_URN={person_urn}\n"
                    found = True
                    break
            
            if not found:
                lines.append(f"\nLINKEDIN_PERSON_URN={person_urn}\n")
            
            # Write back to .env
            with open(env_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            print("Person URN saved to .env file")

    def create_linkedin_post(self, text, access_token):
        """Create a post on LinkedIn"""
        if not self.person_urn:
            print("Person URN not found. Please authenticate first.")
            return False, None

        url = "https://api.linkedin.com/v2/posts"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "X-Restli-Protocol-Version": "2.0.0",
            "Content-Type": "application/json"
        }

        # LinkedIn API v2 post structure
        payload = {
            "author": f"urn:li:person:{self.person_urn}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": text
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }

        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 201:
            post_data = response.json()
            post_id = post_data.get("id", "Unknown")
            print(f"Post created successfully! Post ID: {post_id}")
            return True, post_id
        else:
            print(f"Failed to create post: {response.status_code}")
            print(f"Response: {response.text}")
            return False, None

    def post_to_linkedin(self, content):
        """Post content to LinkedIn"""
        token_data = self.load_token()
        
        if not self.is_token_valid(token_data):
            print("No valid token found. Please authenticate first.")
            print(f"Run: python linkedin_api_poster.py --authenticate")
            return False

        access_token = token_data["access_token"]
        success, post_id = self.create_linkedin_post(content, access_token)
        
        if success:
            self.log_post_in_dashboard(content, post_id)
            return True
        
        return False

    def log_post_in_dashboard(self, content, post_id):
        """Log the LinkedIn post in Dashboard.md"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"\n### LinkedIn Post - {timestamp}\n**Post ID:** {post_id}\n{content}\n\n---\n"

        with open(self.dashboard_file, 'a', encoding='utf-8') as f:
            f.write(entry)

    def check_for_approved_posts(self):
        """Check for posts in Pending_Approval and post them"""
        post_files = list(self.pending_approval_dir.glob("linkedin_post_*.txt"))

        if not post_files:
            print("No pending posts found.")
            return

        # Get access token
        access_token = self.get_access_token()
        
        if not access_token:
            print("No valid LinkedIn token found. Please authenticate first.")
            print(f"Run: python linkedin_api_poster.py --authenticate")
            return

        # Get person URN if not available
        if not self.person_urn:
            print("Getting person URN...")
            self.get_person_urn(access_token)
            
        # If Person URN still not available, use browser fallback
        if not self.person_urn:
            print("\n[WARNING] API posting not available (missing r_basicprofile permission)")
            print("Using browser-based posting as fallback...")
            print()
            self.post_using_browser_fallback()
            return

        # Use API to post
        for post_file in post_files:
            print(f"\nProcessing: {post_file.name}")
            
            with open(post_file, 'r', encoding='utf-8') as f:
                content = f.read()

            print(f"Content: {content[:100]}...")
            
            # Confirm before posting
            confirm = input("Post this to LinkedIn? (y/n): ").lower()
            if confirm != 'y':
                print(f"Skipped: {post_file.name}")
                continue

            success, post_id = self.create_linkedin_post(content, access_token)

            if success:
                # Move to posted folder
                archive_path = self.posted_dir / post_file.name
                post_file.rename(archive_path)
                self.log_post_in_dashboard(content, post_id)
                print(f"Posted successfully! Post ID: {post_id}")
            else:
                print(f"Failed to post: {post_file.name}")

    def post_using_browser_fallback(self):
        """Use browser automation as fallback when API not available"""
        print("Starting browser-based posting...")
        print()
        
        # Import and run browser poster directly
        from linkedin_browser_fallback import LinkedInBrowserPoster
        import asyncio
        
        async def run_browser_post():
            poster = LinkedInBrowserPoster()
            # Post all pending without individual prompts (already prompted in API poster)
            await poster.post_pending()
        
        asyncio.run(run_browser_post())

    def run_authentication_flow(self):
        """Run the complete authentication flow"""
        print("\n=== LinkedIn API Authentication ===\n")
        
        if not self.client_id or self.client_id == "":
            print("Error: LINKEDIN_CLIENT_ID not found in .env file!")
            print("\nSetup Instructions:")
            print("1. Go to https://www.linkedin.com/developers/apps")
            print("2. Create a new app or select existing app")
            print("3. Go to 'Auth' tab and copy Client ID and Client Secret")
            print("4. Update .env file with your credentials")
            return

        # Step 1: Generate authorization URL
        auth_url = self.get_authorization_url()
        
        # Start local HTTP server to capture the callback
        print("\nStarting local server to capture authorization code...")
        
        server_port = 8080
        httpd = None
        
        try:
            # Create server with callback handler
            handler = create_handler(self.set_auth_code)
            httpd = HTTPServer(('localhost', server_port), handler)
            
            # Start server in a separate thread
            server_thread = threading.Thread(target=httpd.serve_forever)
            server_thread.daemon = True
            server_thread.start()
            
            print(f"Server started on http://localhost:{server_port}")
            
            # Open browser automatically
            print("\nOpening LinkedIn authorization page in your browser...")
            webbrowser.open(auth_url)
            
            print("\nPlease authorize the application on LinkedIn.")
            print("Waiting for authorization code...")
            
            # Wait for authorization code (with timeout)
            timeout = 120  # 2 minutes timeout
            start_time = datetime.datetime.now().timestamp()
            
            while self.auth_code is None:
                if datetime.datetime.now().timestamp() - start_time > timeout:
                    print("\nAuthorization timeout. Please try again.")
                    return
                
                import time
                time.sleep(0.5)
            
            print(f"\nAuthorization code received!")

            # Step 2: Exchange code for token
            if self.authenticate(self.auth_code):
                print("\nAuthentication complete! You can now post to LinkedIn.")
        
        except Exception as e:
            print(f"Error during authentication: {e}")
        
        finally:
            if httpd:
                httpd.shutdown()

    def set_auth_code(self, code):
        """Callback to set the authorization code"""
        self.auth_code = code


def main():
    """Main function"""
    import sys
    
    poster = LinkedInAPIPoster()

    if len(sys.argv) > 1:
        if sys.argv[1] == "--authenticate":
            poster.run_authentication_flow()
        elif sys.argv[1] == "--post":
            # Post specific content
            if len(sys.argv) > 2:
                content = " ".join(sys.argv[2:])
                poster.post_to_linkedin(content)
            else:
                print("Usage: python linkedin_api_poster.py --post <content>")
        else:
            print("Usage:")
            print("  python linkedin_api_poster.py --authenticate  # Authenticate with LinkedIn")
            print("  python linkedin_api_poster.py --post <text>   # Post text directly")
            print("  python linkedin_api_poster.py                 # Check and post pending posts")
    else:
        # Default: check for pending posts
        poster.check_for_approved_posts()


if __name__ == "__main__":
    main()
