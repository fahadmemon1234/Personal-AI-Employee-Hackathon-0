"""
Simple Twitter Poster - Fixed OAuth 1.0a
=========================================
Posts tweets using Twitter API v1.1 with proper OAuth 1.0a
"""

import os
import sys
import codecs
import requests
import base64
import hmac
import hashlib
import time
from urllib.parse import urlencode, quote, urlparse
from pathlib import Path
from dotenv import load_dotenv

# Fix Unicode encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

load_dotenv()


class TwitterPoster:
    """Simple Twitter poster using OAuth 1.0a"""

    def __init__(self):
        self.pending_dir = Path("Pending_Approval")
        self.approved_dir = Path("Twitter_Posted")
        self.rejected_dir = Path("Twitter_Rejected")

        for dir_path in [self.pending_dir, self.approved_dir, self.rejected_dir]:
            dir_path.mkdir(exist_ok=True)

        # Credentials
        self.api_key = os.getenv("TWITTER_API_KEY")
        self.api_secret = os.getenv("TWITTER_API_SECRET")
        self.access_token = os.getenv("TWITTER_ACCESS_TOKEN")
        self.access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
        self.base_url = "https://api.twitter.com"

        if not all([self.api_key, self.api_secret, self.access_token, self.access_token_secret]):
            raise ValueError("Missing Twitter credentials in .env")

        print("✅ Twitter credentials loaded")

    def _generate_signature(self, method, url, params):
        """Generate OAuth 1.0a signature"""
        # Normalize URL (remove query string)
        parsed = urlparse(url)
        base_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        
        # Sort and encode parameters
        normalized_params = "&".join(
            f"{quote(str(k), safe='')}={quote(str(v), safe='')}"
            for k, v in sorted(params.items())
        )
        
        # Create base string
        base_string = f"{method.upper()}&{quote(base_url, safe='')}&{quote(normalized_params, safe='')}"
        
        # Create signing key
        signing_key = f"{self.api_secret}&{self.access_token_secret}"
        
        # Generate HMAC-SHA1 signature
        signature = hmac.new(
            signing_key.encode('ascii'),
            base_string.encode('ascii'),
            hashlib.sha1
        ).digest()
        
        return base64.b64encode(signature).decode('ascii')

    def _get_oauth_header(self, method, url, extra_params=None):
        """Generate OAuth 1.0a Authorization header"""
        # Base OAuth parameters
        oauth_params = {
            'oauth_consumer_key': self.api_key,
            'oauth_token': self.access_token,
            'oauth_nonce': str(int(time.time() * 1000)),
            'oauth_timestamp': str(int(time.time())),
            'oauth_signature_method': 'HMAC-SHA1',
            'oauth_version': '1.0'
        }
        
        # Add extra params for signature base
        if extra_params:
            oauth_params.update(extra_params)
        
        # Generate signature
        signature = self._generate_signature(method, url, oauth_params)
        oauth_params['oauth_signature'] = signature
        
        # Build Authorization header
        auth_params = []
        for key, value in oauth_params.items():
            auth_params.append(f'{key}="{quote(str(value), safe="")}"')
        
        return {'Authorization': 'OAuth ' + ', '.join(auth_params)}

    def verify_credentials(self):
        """Verify Twitter credentials"""
        url = f"{self.base_url}/1.1/account/verify_credentials.json"
        params = {'include_entities': 'false', 'skip_status': 'true'}
        
        headers = self._get_oauth_header('GET', url, params)
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            
            if response.status_code == 200:
                user = response.json()
                return {
                    'success': True,
                    'screen_name': user.get('screen_name'),
                    'name': user.get('name'),
                    'followers': user.get('followers_count')
                }
            else:
                return {'success': False, 'error': response.text[:200]}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def post_tweet(self, text):
        """Post a tweet using Twitter API v1.1"""
        # Truncate if needed
        if len(text) > 280:
            text = text[:280]
        
        # Use Twitter API v1.1 statuses/update
        url = f"{self.base_url}/1.1/statuses/update.json"
        params = {'status': text}
        
        headers = self._get_oauth_header('POST', url, params)
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
        
        try:
            response = requests.post(url, headers=headers, data=urlencode(params), timeout=30)
            
            if response.status_code == 200:
                tweet = response.json()
                return {
                    'success': True,
                    'tweet_id': tweet.get('id_str'),
                    'text': tweet.get('text')[:50]
                }
            else:
                return {'success': False, 'error': response.text[:200]}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def approve_and_post(self, filepath, auto_approve=True):
        """Approve and post"""
        print(f"\n{'='*60}")
        print(f"Processing: {filepath.name}")
        print(f"{'='*60}")

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"❌ Error reading file: {e}")
            return False

        print(f"\n📝 Post content ({len(content)} chars):")
        print(f"{'-'*60}")
        preview = content[:200] + "..." if len(content) > 200 else content
        print(preview)
        print(f"{'-'*60}")

        if len(content) > 280:
            print(f"⚠️  WARNING: {len(content)} chars (Twitter limit: 280)")
            content = content[:280]

        if not auto_approve:
            confirm = input("\nApprove and post? (y/n): ").strip().lower()
            if confirm != 'y':
                print("⏭️  Skipped")
                return False

        approved_path = self.approved_dir / filepath.name
        try:
            filepath.rename(approved_path)
            print(f"✅ Moved to Approved: {approved_path.name}")
        except Exception as e:
            print(f"❌ Error moving to Approved: {e}")
            return False

        print("\n📤 Posting to Twitter...")
        result = self.post_tweet(content)

        if result['success']:
            print(f"\n✅ SUCCESS! Tweet published")
            print(f"   Tweet ID: {result['tweet_id']}")
            print(f"   Text: {result['text']}...")
            
            posted_path = self.approved_dir / approved_path.name
            try:
                approved_path.rename(posted_path)
                print(f"✅ Archived to Twitter_Posted: {posted_path.name}")
            except Exception as e:
                print(f"⚠️  Warning: Could not archive: {e}")
            return True
        else:
            print(f"\n❌ FAILED: {result.get('error', 'Unknown error')}")
            
            rejected_path = self.rejected_dir / approved_path.name
            try:
                approved_path.rename(rejected_path)
                print(f"⚠️  Moved to Twitter_Rejected: {rejected_path.name}")
            except Exception as e:
                print(f"⚠️  Warning: Could not move to Rejected: {e}")
            return False

    def list_pending_posts(self):
        """List pending posts"""
        if not self.pending_dir.exists():
            return []
        posts = list(self.pending_dir.glob("linkedin_post_*.txt"))
        posts.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        return posts


def main():
    print("\n" + "="*60)
    print("  TWITTER POST APPROVER (API v1.1)")
    print("  Auto-posts from Pending → Twitter/X")
    print("="*60)

    try:
        poster = TwitterPoster()
    except ValueError as e:
        print(f"\n❌ {e}")
        return

    # Verify credentials
    print("\n🔐 Verifying credentials...")
    result = poster.verify_credentials()
    
    if result['success']:
        print(f"✅ Connected as: @{result['screen_name']}")
        print(f"   Name: {result['name']}")
        print(f"   Followers: {result['followers']}")
    else:
        print(f"❌ Verification failed: {result['error']}")
        print("\nPossible issues:")
        print("1. Invalid credentials in .env")
        print("2. Twitter app needs Read & Write permissions")
        print("3. Access tokens need to be regenerated")
        return

    # List pending
    posts = poster.list_pending_posts()
    
    if not posts:
        print("\n✅ No pending posts!")
        return

    print(f"\n📋 Found {len(posts)} pending post(s):\n")
    
    for i, post in enumerate(posts[:10], 1):
        print(f"  {i}. {post.name}")
    
    if len(posts) > 10:
        print(f"  ... and {len(posts) - 10} more")

    # Menu
    print("\n" + "-"*60)
    print("Options:")
    print("  1. Post latest")
    print("  2. Post all (batch)")
    print("  3. Interactive mode")
    print("  4. View content")
    print("  0. Exit")
    print("-"*60)

    choice = input("\nYour choice (0-4): ").strip()

    if choice == "0":
        print("\n👋 Goodbye!")
        return
    elif choice == "1":
        print(f"\n📤 Posting: {posts[0].name}")
        poster.approve_and_post(posts[0], auto_approve=True)
    elif choice == "2":
        confirm = input(f"\nPost all {len(posts)} tweets? (y/n): ").strip().lower()
        if confirm == 'y':
            success, failed = 0, 0
            for i, post in enumerate(posts, 1):
                print(f"\n[{i}/{len(posts)}]")
                if poster.approve_and_post(post, auto_approve=True):
                    success += 1
                else:
                    failed += 1
                time.sleep(2)
            print(f"\n✅ Done! Posted: {success}, Failed: {failed}")
    elif choice == "3":
        for i, post in enumerate(posts[:10], 1):
            print(f"  {i}. {post.name}")
        while True:
            try:
                c = input("\nPost number (or 'q' to quit): ").strip()
                if c == 'q':
                    return
                num = int(c) - 1
                if 0 <= num < len(posts):
                    poster.approve_and_post(posts[num], auto_approve=False)
                else:
                    print("❌ Invalid")
            except ValueError:
                print("❌ Invalid input")
    elif choice == "4":
        for i, post in enumerate(posts[:10], 1):
            print(f"  {i}. {post.name}")
        try:
            num = int(input("\nView number: ").strip()) - 1
            if 0 <= num < len(posts):
                with open(posts[num], 'r', encoding='utf-8') as f:
                    print(f"\n{'='*60}")
                    print(f.read())
                    print(f"{'='*60}")
        except:
            pass
    else:
        print("❌ Invalid choice")


if __name__ == "__main__":
    main()
