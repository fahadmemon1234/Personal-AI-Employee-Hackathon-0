"""
Automatic LinkedIn Poster with Approval Monitoring
- Monitors Approved/ folder for approval
- Posts automatically via LinkedIn API (no browser)
- Posts all pending posts sequentially
- Auto re-authenticates when token expires
"""

import os
import json
import time
import datetime
import requests
import sys
import webbrowser
import threading
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class AutoLinkedInPoster:
    """Automatically posts to LinkedIn when approval is detected"""

    def __init__(self):
        self.approved_dir = Path("Approved")
        self.pending_dir = Path("Pending_Approval")
        self.posted_dir = Path("Posted")
        self.dashboard_file = "Dashboard.md"
        
        # Credentials from .env
        self.client_id = os.getenv("LINKEDIN_CLIENT_ID", "")
        self.client_secret = os.getenv("LINKEDIN_CLIENT_SECRET", "")
        self.redirect_uri = os.getenv("LINKEDIN_REDIRECT_URI", "http://localhost:8080/callback")
        self.access_token = os.getenv("LINKEDIN_ACCESS_TOKEN", "")
        self.person_urn = os.getenv("LINKEDIN_PERSON_URN", "")
        
        # Token file
        self.token_file = "linkedin_token.json"
        self.auth_code = None
        
        # Create directories
        self.approved_dir.mkdir(exist_ok=True)
        self.pending_dir.mkdir(exist_ok=True)
        self.posted_dir.mkdir(exist_ok=True)

    def has_approval(self):
        """Check if approval file exists"""
        if not self.approved_dir.exists():
            return False
        approval_files = list(self.approved_dir.glob("*"))
        return len(approval_files) > 0

    def clear_approval(self):
        """Remove approval files after processing"""
        for f in self.approved_dir.glob("*"):
            f.unlink()
        print("Approval cleared")

    def auto_authenticate(self):
        """Auto re-authenticate when token is expired - no user interaction"""
        print("\nToken expired, attempting auto re-authentication...")

        if not self.client_id or not self.client_secret:
            print("Client ID or Secret missing in .env")
            return False

        # Generate auth URL
        base_url = "https://www.linkedin.com/oauth/v2/authorization"
        import datetime as dt
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": "w_member_social",
            "state": "auto_" + dt.datetime.now().strftime("%Y%m%d%H%M%S")
        }
        from urllib.parse import urlencode
        auth_url = f"{base_url}?{urlencode(params)}"

        print("\nMANUAL STEP REQUIRED:")
        print(f"   Opening browser for authorization...")
        print(f"   URL: {auth_url[:80]}...")

        # Open browser
        webbrowser.open(auth_url)

        # Start callback server
        print("\nWaiting for callback on localhost:8080...")
        print("   After authorizing, the server will capture the code automatically")

        def create_handler():
            callback_done = threading.Event()
            captured_code = [None]

            class Handler(BaseHTTPRequestHandler):
                def do_GET(self):
                    if self.path.startswith('/callback'):
                        query_components = parse_qs(self.path.split('?')[1])
                        code = query_components.get('code', [''])[0]
                        if code:
                            captured_code[0] = code
                            self.send_response(200)
                            self.send_header('Content-type', 'text/html')
                            self.end_headers()
                            html = """
                            <html><body style="font-family:Arial;text-align:center;padding:50px">
                            <h1 style="color:#28a745">Authorized!</h1>
                            <p>You can close this window.</p>
                            </body></html>
                            """
                            self.wfile.write(html.encode())
                            callback_done.set()
                        else:
                            self.send_response(400)
                            self.end_headers()
                    else:
                        self.send_response(404)
                        self.end_headers()

                def log_message(self, format, *args):
                    pass

            return Handler, callback_done, captured_code

        Handler, callback_done, captured_code = create_handler()

        try:
            httpd = HTTPServer(('localhost', 8080), Handler)
            server_thread = threading.Thread(target=httpd.serve_forever)
            server_thread.daemon = True
            server_thread.start()

            # Wait for callback (2 min timeout)
            if callback_done.wait(timeout=120):
                auth_code = captured_code[0]
                print(f"Authorization code received")

                # Exchange for token
                token_url = "https://www.linkedin.com/oauth/v2/accessToken"
                data = {
                    "grant_type": "authorization_code",
                    "code": auth_code,
                    "redirect_uri": self.redirect_uri,
                    "client_id": self.client_id,
                    "client_secret": self.client_secret
                }
                response = requests.post(token_url, data=data)

                if response.status_code == 200:
                    token_data = response.json()
                    token_data["expires_at"] = datetime.datetime.now().timestamp() + token_data.get("expires_in", 3600)

                    # Get person URN first
                    person_urn = self._fetch_person_urn(token_data["access_token"])
                    if person_urn:
                        token_data["person_urn"] = person_urn
                        self.person_urn = person_urn
                        self._save_person_urn(person_urn)

                    # Save token
                    with open(self.token_file, 'w') as f:
                        json.dump(token_data, f, indent=2)

                    # Update .env
                    self._update_env_token(token_data["access_token"])
                    self.access_token = token_data["access_token"]

                    print("Re-authentication successful!")
                    httpd.shutdown()
                    return True
                else:
                    print(f"Token exchange failed: {response.text}")

            else:
                print("Authorization timeout")

        except Exception as e:
            print(f"Auth error: {e}")

        finally:
            try:
                httpd.shutdown()
            except:
                pass

        return False

    def _update_env_token(self, new_token):
        """Update access token in .env file"""
        env_path = Path(".env")
        if env_path.exists():
            with open(env_path, 'r') as f:
                lines = f.readlines()

            for i, line in enumerate(lines):
                if line.startswith("LINKEDIN_ACCESS_TOKEN="):
                    lines[i] = f"LINKEDIN_ACCESS_TOKEN={new_token}\n"
                    break

            with open(env_path, 'w') as f:
                f.writelines(lines)

    def _fetch_person_urn(self, access_token):
        """Fetch person URN from LinkedIn API - try posts endpoint"""
        # Try to get from existing posts
        url = "https://api.linkedin.com/v2/posts?q=members&projection=(elements*(author))"
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
                    author = elements[0].get("author", "")
                    if author.startswith("urn:li:person:"):
                        person_urn = author.replace("urn:li:person:", "")
                        print(f"Person URN fetched from posts: {person_urn}")
                        return person_urn
        except Exception as e:
            print(f"Could not fetch Person URN from posts: {e}")
        
        # Try email endpoint
        url = "https://api.linkedin.com/v2/emailAddress?q=members&projection=(elements*(handle~))"
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                elements = data.get("elements", [])
                if elements:
                    print(f"Email found: {elements[0].get('handle~', {}).get('emailAddress', 'N/A')}")
        except Exception as e:
            print(f"Email endpoint error: {e}")
        
        return None

    def _save_person_urn(self, person_urn):
        """Save person URN to .env file"""
        env_path = Path(".env")
        if env_path.exists():
            with open(env_path, 'r') as f:
                lines = f.readlines()

            found = False
            for i, line in enumerate(lines):
                if line.startswith("LINKEDIN_PERSON_URN="):
                    lines[i] = f"LINKEDIN_PERSON_URN={person_urn}\n"
                    found = True
                    break

            if not found:
                lines.append(f"\nLINKEDIN_PERSON_URN={person_urn}\n")

            with open(env_path, 'w') as f:
                f.writelines(lines)
            print("Person URN saved to .env")

    def get_access_token(self):
        """Get valid access token"""
        # First try .env
        if self.access_token:
            print("Using token from .env")
            return self.access_token

        # Then try token file
        if os.path.exists(self.token_file):
            with open(self.token_file, 'r') as f:
                token_data = json.load(f)
                # Check expiration
                if "expires_at" in token_data:
                    if datetime.datetime.now().timestamp() < token_data["expires_at"]:
                        print("Using valid token from file")
                        return token_data.get("access_token")
                    else:
                        print("Token expired, need re-authentication")
                        return None

        return None

    def get_person_urn(self, access_token):
        """Get person URN - tries cache first, then API"""
        # Approach 1: Check .env for person URN
        person_urn = os.getenv("LINKEDIN_PERSON_URN", "")
        if person_urn:
            print(f"Person URN (from .env): {person_urn}")
            return person_urn
        
        # Approach 2: Try to extract from existing token file
        if os.path.exists(self.token_file):
            with open(self.token_file, 'r') as f:
                token_data = json.load(f)
                if "person_urn" in token_data:
                    person_urn = token_data["person_urn"]
                    print(f"Person URN (from cache): {person_urn}")
                    return person_urn
        
        # Approach 3: Fetch from API
        return self._fetch_person_urn(access_token)

    def create_post(self, text, access_token, person_urn):
        """Create a post on LinkedIn via API - using urn:li:person:me"""
        url = "https://api.linkedin.com/v2/posts"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "X-Restli-Protocol-Version": "2.0.0",
            "Content-Type": "application/json",
            "LinkedIn-Version": "202402"
        }
        
        # Always use 'me' - LinkedIn resolves automatically with w_member_social scope
        author = "urn:li:person:me"

        # LinkedIn API v2 format for text-only posts
        payload = {
            "author": author,
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

        try:
            response = requests.post(url, json=payload, headers=headers)

            if response.status_code == 201:
                post_data = response.json()
                post_id = post_data.get("id", "Unknown")
                print(f"   Posted successfully! ID: {post_id}")
                return True, post_id
            else:
                print(f"   API Error {response.status_code}: {response.text[:300]}")
                return False, None

        except Exception as e:
            print(f"   Post failed: {e}")
            return False, None

    def log_post(self, content, post_id):
        """Log post to dashboard"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"\n### LinkedIn Post - {timestamp}\n**Post ID:** {post_id}\n{content}\n\n---\n"

        with open(self.dashboard_file, 'a', encoding='utf-8') as f:
            f.write(entry)

    def post_all_pending(self):
        """Post all pending posts to LinkedIn"""
        print("\n" + "="*50)
        print("Starting Auto-Post Process")
        print("="*50)
        
        # Get token
        access_token = self.get_access_token()
        
        # If no token, try auto re-authenticate
        if not access_token:
            print("No valid access token found!")
            if self.auto_authenticate():
                access_token = self.access_token
            else:
                print("Auto-authentication failed")
                self.clear_approval()
                return False
        
        # Get person URN
        person_urn = self.get_person_urn(access_token)
        
        # If Person URN not available, try to auto-authenticate with proper scope
        if not person_urn:
            print("\nPerson URN not found!")
            print("Will try to fetch from API or use 'me' as fallback...")
            
            # Try to fetch from existing posts
            person_urn = self._fetch_person_urn(access_token)
            
            if person_urn:
                self.person_urn = person_urn
                self._save_person_urn(person_urn)
                print(f"Person URN saved: {person_urn}")
            else:
                print("Using 'urn:li:person:me' as author (LinkedIn will resolve automatically)")
                person_urn = None  # Will use 'me' in create_post
        
        # Get pending posts
        post_files = list(self.pending_dir.glob("linkedin_post_*.txt"))
        
        if not post_files:
            print("No pending posts found")
            self.clear_approval()
            return True
        
        print(f"Found {len(post_files)} pending post(s)")
        print("="*50)
        
        # Try API first
        success_count = 0
        fail_count = 0
        api_failed = False
        
        for post_file in post_files:
            print(f"\nProcessing: {post_file.name}")
            
            try:
                with open(post_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                
                if not content:
                    print("Empty post, skipping")
                    continue
                
                # Preview
                preview = content[:80] + "..." if len(content) > 80 else content
                print(f"   Content: {preview}")
                
                # Post to LinkedIn
                success, post_id = self.create_post(content, access_token, person_urn)
                
                if success:
                    print(f"   Posted! ID: {post_id}")
                    
                    # Move to posted folder
                    archive_path = self.posted_dir / post_file.name
                    post_file.rename(archive_path)
                    
                    # Log to dashboard
                    self.log_post(content, post_id)
                    
                    success_count += 1
                    
                    # Small delay between posts
                    time.sleep(1)
                else:
                    print(f"   Failed to post")
                    fail_count += 1
                    api_failed = True
                    
            except Exception as e:
                print(f"   Error: {e}")
                fail_count += 1
                api_failed = True
        
        # If API failed for all posts, use browser fallback
        if api_failed and success_count == 0:
            print("\n" + "="*50)
            print("API posting failed. Using browser fallback...")
            print("="*50)
            self.post_using_browser_fallback()
            return True
        
        # Summary
        print("\n" + "="*50)
        print(f"Summary: {success_count} posted, {fail_count} failed")
        print("="*50)
        
        # Clear approval
        self.clear_approval()

        return success_count > 0

    def post_using_browser_fallback(self):
        """Use browser automation as fallback when API not available"""
        print("\nStarting browser-based posting...")
        print("This will open a browser and post automatically.\n")

        # Import and run browser poster directly
        from linkedin_browser_fallback import LinkedInBrowserPoster
        import asyncio

        async def run_browser_post():
            poster = LinkedInBrowserPoster()
            await poster.post_pending()

        try:
            asyncio.run(run_browser_post())
            print("\nBrowser posting completed!")
        except Exception as e:
            print(f"Browser posting failed: {e}")

    def monitor(self, check_interval=10):
        """Monitor for approval continuously"""
        print("\n" + "="*50)
        print("LinkedIn Auto-Poster Monitor Started")
        print("="*50)
        print(f"Watching: {self.approved_dir.absolute()}")
        print(f"Check interval: {check_interval}s")
        print("\nTo approve: Create any file in Approved/ folder")
        print("   Example: echo approved > Approved/approve.txt")
        print("\nPress Ctrl+C to stop monitoring\n")
        
        try:
            while True:
                if self.has_approval():
                    print("\nApproval detected!")
                    self.post_all_pending()
                    print("\nResuming monitoring...")
                
                time.sleep(check_interval)
                
        except KeyboardInterrupt:
            print("\n\nMonitor stopped by user")


def main():
    """Main entry point"""
    poster = AutoLinkedInPoster()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--once":
            # Check once and exit
            print("Checking for approval...")
            if poster.has_approval():
                print("Approval found!")
                poster.post_all_pending()
            else:
                print("No approval found")
        elif sys.argv[1] == "--post-now":
            # Post immediately without waiting for approval
            print("Posting all pending posts now...")
            poster.post_all_pending()
        elif sys.argv[1] == "--status":
            # Show current status
            print("Current Status:")
            print(f"   Token: {'OK' if poster.access_token else 'Missing'}")
            print(f"   Person URN: {poster.person_urn or 'Not set'}")
            pending = list(poster.pending_dir.glob("linkedin_post_*.txt"))
            print(f"   Pending posts: {len(pending)}")
            approval = poster.has_approval()
            print(f"   Approval: {'Waiting' if approval else 'None'}")
        else:
            print("Usage:")
            print("  python auto_linkedin_poster.py          # Start monitoring")
            print("  python auto_linkedin_poster.py --once   # Check once")
            print("  python auto_linkedin_poster.py --post-now  # Post immediately")
            print("  python auto_linkedin_poster.py --status # Show status")
    else:
        # Start continuous monitoring
        poster.monitor()


if __name__ == "__main__":
    main()
