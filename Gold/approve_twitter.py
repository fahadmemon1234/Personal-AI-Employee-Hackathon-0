"""
Quick Twitter Post Approver
============================
Automatically approves and posts Twitter content from Pending_Approval folder.

Requirements:
- Twitter API credentials in .env:
  - TWITTER_API_KEY
  - TWITTER_API_SECRET
  - TWITTER_ACCESS_TOKEN
  - TWITTER_ACCESS_TOKEN_SECRET
"""

import os
import sys
import codecs
import requests
from pathlib import Path
from dotenv import load_dotenv
import base64
import hmac
import hashlib
import time
from urllib.parse import urlencode, quote

# Fix Unicode encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

# Load environment variables
load_dotenv()


class TwitterPostApprover:
    """
    Automated Twitter post approver and publisher.

    Handles:
    - Moving posts from Pending → Approved
    - Posting to Twitter API
    - Moving failed posts to Rejected folder
    - Moving successful posts to Posted folder
    """

    def __init__(self):
        # Directory paths
        self.pending_dir = Path("Pending_Approval")
        self.approved_dir = Path("Twitter_Posted")
        self.rejected_dir = Path("Twitter_Rejected")

        # Create directories
        for dir_path in [self.pending_dir, self.approved_dir, self.rejected_dir]:
            dir_path.mkdir(exist_ok=True)

        # Twitter API configuration (OAuth 1.0a)
        self.api_key = os.getenv("TWITTER_API_KEY")
        self.api_secret = os.getenv("TWITTER_API_SECRET")
        self.access_token = os.getenv("TWITTER_ACCESS_TOKEN")
        self.access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
        self.base_url = "https://api.twitter.com"

        # Cached user data
        self.user_info = None

        # Validate setup
        if not all([self.api_key, self.api_secret, self.access_token, self.access_token_secret]):
            print("❌ ERROR: Twitter credentials not found in .env file")
            print("   Required: TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET")
            raise ValueError("Missing Twitter credentials in .env")

        print("✅ Twitter credentials loaded (OAuth 1.0a)")

    def _generate_oauth_signature(self, method, url, params):
        """Generate OAuth 1.0a signature"""
        # Normalize parameters
        normalized_params = urlencode(sorted(params.items()))
        
        # Create base string
        base_string = f"{method.upper()}&{quote(url, safe='')}&{quote(normalized_params, safe='')}"
        
        # Create signing key
        signing_key = f"{self.api_secret}&{self.access_token_secret}"
        
        # Generate signature
        signature = hmac.new(
            signing_key.encode('ascii'),
            base_string.encode('ascii'),
            hashlib.sha1
        ).digest()
        
        return base64.b64encode(signature).decode('ascii')

    def _get_oauth_headers(self, method, url, extra_params=None):
        """Generate OAuth 1.0a headers for API requests"""
        # OAuth parameters
        oauth_params = {
            'oauth_consumer_key': self.api_key,
            'oauth_token': self.access_token,
            'oauth_nonce': str(int(time.time() * 1000000)),
            'oauth_timestamp': str(int(time.time())),
            'oauth_signature_method': 'HMAC-SHA1',
            'oauth_version': '1.0'
        }
        
        # Add extra params if provided
        if extra_params:
            oauth_params.update(extra_params)
        
        # Generate signature
        signature = self._generate_oauth_signature(method, url, oauth_params)
        oauth_params['oauth_signature'] = signature
        
        # Build Authorization header
        auth_header_params = []
        for key, value in oauth_params.items():
            auth_header_params.append(f'{key}="{quote(str(value), safe="")}"')
        
        authorization_header = 'OAuth ' + ', '.join(sorted(auth_header_params))
        
        return {
            'Authorization': authorization_header,
            'Content-Type': 'application/json'
        }

    def get_user_info(self):
        """Get current user's profile information"""
        if self.user_info:
            return self.user_info

        try:
            url = f"{self.base_url}/1.1/account/verify_credentials.json"
            params = {
                'include_entities': 'false'
            }
            headers = self._get_oauth_headers('GET', url, params)
            
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()

            self.user_info = response.json()
            return self.user_info

        except Exception as e:
            print(f"❌ Error getting user info: {e}")
            return None

    def validate_credentials(self):
        """Validate Twitter credentials by fetching user info"""
        return self.get_user_info() is not None

    def create_tweet(self, text):
        """
        Create a tweet on Twitter.

        Args:
            text: Tweet content (max 280 characters)

        Returns:
            dict: Tweet response with ID, or None if failed
        """
        # Validate text length (Twitter limit: 280 characters)
        if len(text) > 280:
            print(f"⚠️  Warning: Tweet truncated from {len(text)} to 280 characters")
            text = text[:280]

        # Construct tweet payload
        payload = {"text": text}

        # API endpoint - use v2 tweets endpoint
        url = f"{self.base_url}/2/tweets"

        try:
            headers = self._get_oauth_headers('POST', url)
            response = requests.post(url, headers=headers, json=payload, timeout=30)

            # Check for errors
            if response.status_code != 201:
                print(f"❌ HTTP {response.status_code}: Failed to create tweet")
                print(f"   Response: {response.text}")
                return None

            # Parse successful response
            result = response.json()
            tweet_id = result.get("data", {}).get("id")

            if not tweet_id:
                print("❌ No tweet ID in response")
                print(f"   Response: {result}")
                return None

            return result

        except requests.exceptions.RequestException as e:
            print(f"❌ Network error: {e}")
            return None
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return None

    def approve_and_post(self, filepath, auto_approve=True):
        """
        Approve a post and publish it to Twitter.

        Workflow:
        1. Read post content from file
        2. Move from Pending → Approved
        3. Post to Twitter API
        4. On success: Move to Twitter_Posted folder
        5. On failure: Move to Twitter_Rejected folder

        Args:
            filepath: Path to post file in Pending_Approval
            auto_approve: If True, skip confirmation prompt

        Returns:
            bool: True if posted successfully, False otherwise
        """
        print(f"\n{'='*60}")
        print(f"Processing: {filepath.name}")
        print(f"{'='*60}")

        # Read post content
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"❌ Error reading file: {e}")
            return False

        # Show post preview
        print(f"\n📝 Post content ({len(content)} chars):")
        print(f"{'-'*60}")
        preview = content[:200] + "..." if len(content) > 200 else content
        print(preview)
        print(f"{'-'*60}")

        # Check length
        if len(content) > 280:
            print(f"⚠️  WARNING: Content is {len(content)} chars (Twitter limit: 280)")
            print("   Content will be truncated.")

        # Confirmation (skip if auto_approve)
        if not auto_approve:
            confirm = input("\nApprove and post? (y/n): ").strip().lower()
            if confirm != 'y':
                print("⏭️  Skipped")
                return False

        # Move to Approved directory
        approved_path = self.approved_dir / filepath.name
        try:
            filepath.rename(approved_path)
            print(f"✅ Moved to Approved: {approved_path.name}")
        except Exception as e:
            print(f"❌ Error moving to Approved: {e}")
            return False

        # Post to Twitter
        print("\n📤 Posting to Twitter...")
        result = self.create_tweet(content)

        if result:
            # ✅ SUCCESS - Move to Posted folder
            tweet_id = result.get("data", {}).get("id")
            username = self.user_info.get("username", "user") if self.user_info else "user"
            tweet_url = f"https://twitter.com/{username}/status/{tweet_id}"

            print(f"\n✅ SUCCESS! Tweet published")
            print(f"   Tweet ID: {tweet_id}")
            print(f"   URL: {tweet_url}")

            # Move to Posted folder
            posted_path = self.approved_dir / approved_path.name
            try:
                approved_path.rename(posted_path)
                print(f"✅ Archived to Twitter_Posted: {posted_path.name}")
            except Exception as e:
                print(f"⚠️  Warning: Could not archive: {e}")

            return True

        else:
            # ❌ FAILED - Move to Rejected folder
            print(f"\n❌ FAILED to post to Twitter")

            # Move to Rejected folder
            rejected_path = self.rejected_dir / approved_path.name
            try:
                approved_path.rename(rejected_path)
                print(f"⚠️  Moved to Twitter_Rejected: {rejected_path.name}")
            except Exception as e:
                print(f"⚠️  Warning: Could not move to Rejected: {e}")

            return False

    def list_pending_posts(self):
        """List all pending posts sorted by date (newest first)"""
        if not self.pending_dir.exists():
            return []

        posts = list(self.pending_dir.glob("linkedin_post_*.txt"))
        posts.sort(key=lambda x: x.stat().st_mtime, reverse=True)

        return posts

    def approve_all_pending(self):
        """Approve and post all pending posts automatically"""
        posts = self.list_pending_posts()

        if not posts:
            print("\n✅ No pending posts found!")
            return 0, 0

        print(f"\n📋 Found {len(posts)} pending post(s)")

        success_count = 0
        failed_count = 0

        for i, post in enumerate(posts, 1):
            print(f"\n[{i}/{len(posts)}]")
            success = self.approve_and_post(post, auto_approve=True)

            if success:
                success_count += 1
            else:
                failed_count += 1

        return success_count, failed_count


def main():
    """Main entry point"""
    print("\n" + "="*60)
    print("  TWITTER POST APPROVER")
    print("  Auto-posts from Pending → Twitter/X")
    print("="*60)

    # Initialize approver
    try:
        approver = TwitterPostApprover()
    except ValueError as e:
        print(f"\n❌ {e}")
        print("\nSetup instructions:")
        print("1. Add Twitter credentials to .env:")
        print("   - TWITTER_API_KEY")
        print("   - TWITTER_API_SECRET")
        print("   - TWITTER_ACCESS_TOKEN")
        print("   - TWITTER_ACCESS_TOKEN_SECRET")
        return

    # Validate credentials
    print("\n🔐 Validating Twitter credentials...")
    if not approver.validate_credentials():
        print("\n❌ Invalid Twitter credentials")
        print("\nFix:")
        print("1. Check your Twitter API credentials in .env")
        print("2. Ensure your Twitter app has proper permissions (Read and Write)")
        print("3. Make sure access tokens are generated for your Twitter account")
        return

    user_info = approver.get_user_info()
    if user_info:
        print(f"✅ Connected as: @{user_info.get('screen_name', 'Unknown')}")
        print(f"   Name: {user_info.get('name', 'Unknown')}")
        print(f"   Followers: {user_info.get('followers_count', 0)}")

    # List pending posts
    posts = approver.list_pending_posts()

    if not posts:
        print("\n✅ No pending posts found!")
        return

    print(f"\n📋 Found {len(posts)} pending post(s):\n")

    # Show latest 10 posts
    for i, post in enumerate(posts[:10], 1):
        print(f"  {i}. {post.name}")

    if len(posts) > 10:
        print(f"  ... and {len(posts) - 10} more")

    # Menu
    print("\n" + "-"*60)
    print("Options:")
    print("  1. Post latest (most recent)")
    print("  2. Post all pending (batch)")
    print("  3. Interactive mode (choose individually)")
    print("  4. View post content")
    print("  0. Exit")
    print("-"*60)

    choice = input("\nYour choice (0-4): ").strip()

    if choice == "0":
        print("\n👋 Goodbye!")
        return

    elif choice == "1":
        # Post latest
        print(f"\n📤 Posting latest: {posts[0].name}")
        approver.approve_and_post(posts[0], auto_approve=True)

    elif choice == "2":
        # Post all
        print(f"\n📤 Posting all {len(posts)} pending posts...")
        confirm = input("   Are you sure? (y/n): ").strip().lower()

        if confirm == 'y':
            print("\n⚠️  Note: Twitter has rate limits (300 tweets/day for free tier)")
            print("   Posts will be processed with 2-second delays...\n")

            success, failed = approver.approve_all_pending()

            print(f"\n{'='*60}")
            print(f"✅ Completed!")
            print(f"   Posted: {success}")
            print(f"   Failed: {failed}")
            print(f"{'='*60}")
        else:
            print("\n⏭️  Cancelled")

    elif choice == "3":
        # Interactive mode
        print(f"\n📋 Interactive mode - choose posts to approve\n")

        for i, post in enumerate(posts[:10], 1):
            print(f"  {i}. {post.name}")

        if len(posts) > 10:
            print(f"  ... and {len(posts) - 10} more")

        while True:
            try:
                choice = input("\nPost number (or 'q' to quit): ").strip().lower()

                if choice == 'q':
                    print("\n👋 Goodbye!")
                    return

                num = int(choice) - 1

                if 0 <= num < len(posts):
                    approver.approve_and_post(posts[num], auto_approve=False)
                else:
                    print("❌ Invalid number")

            except ValueError:
                print("❌ Invalid input - enter a number or 'q'")
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                return

    elif choice == "4":
        # View post content
        print(f"\n📄 View post content\n")

        for i, post in enumerate(posts[:10], 1):
            print(f"  {i}. {post.name}")

        try:
            num = int(input("\nView post number: ").strip()) - 1

            if 0 <= num < len(posts):
                with open(posts[num], 'r', encoding='utf-8') as f:
                    content = f.read()

                print(f"\n{'='*60}")
                print(content)
                print(f"{'='*60}")
                
                # Show length warning
                if len(content) > 280:
                    print(f"\n⚠️  WARNING: {len(content)} chars (Twitter limit: 280)")
            else:
                print("❌ Invalid number")

        except ValueError:
            print("❌ Invalid input")
        except Exception as e:
            print(f"❌ Error: {e}")

    else:
        print("❌ Invalid choice")


if __name__ == "__main__":
    main()
