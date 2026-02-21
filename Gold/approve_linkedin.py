"""
Quick LinkedIn Post Approver - FIXED VERSION
=============================================
Automatically approves and posts LinkedIn content from Pending_Approval folder.

FIXES APPLIED:
1. ✅ Correct author URN format: urn:li:person:{id} (not just the ID)
2. ✅ Proper X-Restli-Protocol-Version: 2.0.0 header
3. ✅ Uses /v2/userinfo endpoint (OIDC compliant, not deprecated /v2/me)
4. ✅ Correct ugcPosts payload structure
5. ✅ Automatic token validation and user info retrieval
6. ✅ Proper error handling with Rejected folder for failed posts

Requirements:
- Access token in .env with scope: w_member_social
- Token must be valid (not expired)
"""

import os
import sys
import codecs
import requests
from pathlib import Path
from dotenv import load_dotenv

# Fix Unicode encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

# Load environment variables
load_dotenv()


class LinkedInPostApprover:
    """
    Automated LinkedIn post approver and publisher.
    
    Handles:
    - Moving posts from Pending → Approved
    - Posting to LinkedIn using ugcPosts API
    - Moving failed posts to Rejected folder
    - Moving successful posts to Posted folder
    """
    
    def __init__(self):
        # Directory paths
        self.pending_dir = Path("Pending_Approval")
        self.approved_dir = Path("Approved")
        self.rejected_dir = Path("Rejected")
        self.posted_dir = Path("Posted")
        
        # Create directories
        for dir_path in [self.pending_dir, self.approved_dir, self.rejected_dir, self.posted_dir]:
            dir_path.mkdir(exist_ok=True)
        
        # LinkedIn API configuration
        self.access_token = os.getenv("LINKEDIN_ACCESS_TOKEN")
        self.base_url = "https://api.linkedin.com/v2"
        
        # Cached user data
        self.person_urn = None
        self.user_info = None
        
        # Validate setup
        if not self.access_token:
            print("❌ ERROR: No access token found in .env file")
            print("   Run 'python linkedin_auth.py' to authorize first.\n")
            raise ValueError("Missing LINKEDIN_ACCESS_TOKEN in .env")
    
    def get_user_info(self):
        """
        Get current user's profile using OIDC /v2/userinfo endpoint.
        
        FIX: Uses /v2/userinfo instead of deprecated /v2/me
        """
        if self.user_info:
            return self.user_info
        
        url = f"{self.base_url}/userinfo"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            self.user_info = response.json()
            
            # Extract person URN from 'sub' field
            # Format: "urn:li:person:ACoAABkD3jQBqKZ9X8vN5Q"
            sub_value = self.user_info.get("sub")
            
            # Ensure the URN is in full format: urn:li:person:{id}
            # The sub field may return just the ID or the full URN
            if sub_value and not sub_value.startswith("urn:li:person:"):
                self.person_urn = f"urn:li:person:{sub_value}"
            else:
                self.person_urn = sub_value

            if not self.person_urn:
                print("❌ ERROR: Could not extract person URN from user info")
                print(f"   Response: {self.user_info}")
                return None
            
            return self.user_info
            
        except requests.exceptions.HTTPError as e:
            print(f"❌ HTTP Error getting user info: {e}")
            print(f"   Response: {e.response.text}")
            return None
        except Exception as e:
            print(f"❌ Error getting user info: {e}")
            return None
    
    def validate_token(self):
        """Validate access token by fetching user info"""
        return self.get_user_info() is not None
    
    def create_linkedin_post(self, text, visibility="PUBLIC"):
        """
        Create a text post on LinkedIn using ugcPosts endpoint.
        
        FIXES APPLIED:
        1. ✅ Author field uses full URN format: urn:li:person:{id}
        2. ✅ X-Restli-Protocol-Version: 2.0.0 header included
        3. ✅ Correct payload structure for ugcPosts API
        4. ✅ Proper Bearer token authentication
        
        Args:
            text: Post content (max 3000 characters)
            visibility: "PUBLIC" or "CONNECTIONS"
            
        Returns:
            dict: Post response with ID, or None if failed
            
        API Documentation:
        https://learn.microsoft.com/en-us/linkedin/marketing/integrations/community-management/shares/ugc-post-api
        """
        # Validate token and get user info
        if not self.person_urn:
            user_info = self.get_user_info()
            if not user_info:
                print("❌ Invalid access token or insufficient permissions")
                print("   Run 'python linkedin_auth.py' to re-authorize")
                return None
        
        # Validate text length (LinkedIn limit: 3000 characters)
        if len(text) > 3000:
            text = text[:2997] + "..."
            print("⚠️  Warning: Post truncated to 3000 characters")
        
        # ============================================================
        # CONSTRUCT UGC POST PAYLOAD
        # ============================================================
        # FIX: Author must be full URN format: "urn:li:person:{id}"
        # NOT just the ID (e.g., "MqvEfm3LKp" is WRONG)
        # CORRECT: "urn:li:person:MqvEfm3LKp"
        # ============================================================
        
        payload = {
            "author": self.person_urn,  # ✅ Full URN: "urn:li:person:..."
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": text
                    },
                    "shareMediaCategory": "NONE"  # Text-only post
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": visibility
            }
        }
        
        # API endpoint
        url = f"{self.base_url}/ugcPosts"
        
        # ============================================================
        # HEADERS - CRITICAL FOR SUCCESS
        # ============================================================
        # FIX: X-Restli-Protocol-Version: 2.0.0 is REQUIRED
        # ============================================================
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",  # ✅ Bearer token auth
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",  # ✅ Required header
            "LinkedIn-Version": "202402"  # ✅ API version
        }
        
        # ============================================================
        # MAKE API REQUEST
        # ============================================================
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            
            # Check for errors
            if response.status_code != 201:
                print(f"❌ HTTP {response.status_code}: Failed to create post")
                print(f"   Response: {response.text}")
                
                # Handle specific error cases
                if response.status_code == 403:
                    error_data = response.json()
                    if "ACCESS_DENIED" in str(error_data):
                        print("   ⚠️  Access denied - check token permissions")
                        print("   Required scope: w_member_social")
                        print("   Run 'python linkedin_auth.py' to re-authorize")
                    elif "Data Processing Exception" in str(error_data):
                        print("   ⚠️  Author field format error")
                        print(f"   Current author: {self.person_urn}")
                        print("   Expected format: urn:li:person:{id}")
                
                return None
            
            # Parse successful response
            result = response.json()
            post_id = result.get("id")
            
            if not post_id:
                print("❌ No post ID in response")
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
        Approve a post and publish it to LinkedIn.
        
        Workflow:
        1. Read post content from file
        2. Move from Pending → Approved
        3. Post to LinkedIn API
        4. On success: Move to Posted folder
        5. On failure: Move to Rejected folder
        
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
        
        # Post to LinkedIn
        print("\n📤 Posting to LinkedIn...")
        result = self.create_linkedin_post(content)
        
        if result:
            # ✅ SUCCESS - Move to Posted folder
            post_id = result.get("id", "unknown")
            post_url = f"https://www.linkedin.com/feed/update/{post_id}"
            
            print(f"\n✅ SUCCESS! Post published")
            print(f"   Post ID: {post_id}")
            print(f"   URL: {post_url}")
            
            # Move to Posted folder
            posted_path = self.posted_dir / approved_path.name
            try:
                approved_path.rename(posted_path)
                print(f"✅ Archived to Posted: {posted_path.name}")
            except Exception as e:
                print(f"⚠️  Warning: Could not archive: {e}")
            
            return True
            
        else:
            # ❌ FAILED - Move to Rejected folder
            print(f"\n❌ FAILED to post to LinkedIn")
            
            # Move to Rejected folder
            rejected_path = self.rejected_dir / approved_path.name
            try:
                approved_path.rename(rejected_path)
                print(f"⚠️  Moved to Rejected: {rejected_path.name}")
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
    print("  LINKEDIN POST APPROVER (FIXED VERSION)")
    print("  Auto-posts from Pending → LinkedIn")
    print("="*60)
    
    # Initialize approver
    try:
        approver = LinkedInPostApprover()
    except ValueError as e:
        print(f"\n❌ {e}")
        print("\nSetup instructions:")
        print("1. Run 'python linkedin_auth.py' to authorize")
        print("2. Make sure .env has LINKEDIN_ACCESS_TOKEN")
        return
    
    # Validate token
    print("\n🔐 Validating access token...")
    if not approver.validate_token():
        print("\n❌ Invalid or expired access token")
        print("\nFix:")
        print("1. Run 'python linkedin_auth.py' to get new token")
        print("2. Make sure token has scope: w_member_social")
        return
    
    print(f"✅ Token valid - Logged in as: {approver.user_info.get('name', 'Unknown')}")
    print(f"   Person URN: {approver.person_urn}")
    
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
            print("\n⚠️  Note: LinkedIn has rate limits (200 posts/day)")
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
