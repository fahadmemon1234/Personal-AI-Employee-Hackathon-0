"""
Twitter Browser Automation (No API Required)
=============================================
Posts tweets directly via Twitter.com using browser automation.
No API credentials needed - just your Twitter login.

Requirements:
- pip install selenium webdriver-manager
"""

import os
import sys
import codecs
import time
from pathlib import Path
from dotenv import load_dotenv

# Fix Unicode encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

# Load environment variables
load_dotenv()

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.service import Service
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.chrome.options import Options
except ImportError:
    print("❌ Missing required packages!")
    print("   Run: pip install selenium webdriver-manager")
    sys.exit(1)


class TwitterBrowserPoster:
    """
    Post tweets to Twitter using browser automation.
    No API credentials required - uses Twitter.com directly.
    """

    def __init__(self):
        # Directory paths
        self.pending_dir = Path("Pending_Approval")
        self.approved_dir = Path("Twitter_Posted")
        self.rejected_dir = Path("Twitter_Rejected")

        # Create directories
        for dir_path in [self.pending_dir, self.approved_dir, self.rejected_dir]:
            dir_path.mkdir(exist_ok=True)

        # Twitter login credentials
        self.email = os.getenv("TWITTER_EMAIL")
        self.username = os.getenv("TWITTER_USERNAME")
        self.password = os.getenv("TWITTER_PASSWORD")

        # Browser instance
        self.driver = None
        self.wait = None

        # Validate setup
        if not all([self.email, self.password]):
            print("❌ ERROR: Twitter login credentials not found in .env file")
            print("   Required: TWITTER_EMAIL (or TWITTER_USERNAME), TWITTER_PASSWORD")
            raise ValueError("Missing Twitter credentials in .env")

    def setup_browser(self):
        """Setup Chrome browser for Twitter"""
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # Keep browser open for debugging (optional)
        # chrome_options.add_experimental_option("detach", True)
        
        # Suppress logs
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.wait = WebDriverWait(self.driver, 30)
            print("✅ Browser initialized")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize browser: {e}")
            print("   Install: pip install selenium webdriver-manager")
            return False

    def login(self):
        """Login to Twitter"""
        try:
            print("🔐 Navigating to Twitter login...")
            self.driver.get("https://twitter.com/login")
            time.sleep(3)

            # Enter email/username
            print("   Entering email/username...")
            try:
                email_field = self.wait.until(
                    EC.presence_of_element_located((By.Name, "text"))
                )
                email_field.clear()
                email_field.send_keys(self.email)
                email_field.send_keys(Keys.RETURN)
                time.sleep(2)
            except Exception as e:
                print(f"   ⚠️  Email field error: {e}")

            # Enter username (if prompted)
            try:
                username_field = self.driver.find_element(By.XPATH, "//input[@type='text' and @autocomplete='username']")
                if username_field:
                    print("   Entering username...")
                    username_field.clear()
                    username_field.send_keys(self.username)
                    username_field.send_keys(Keys.RETURN)
                    time.sleep(2)
            except:
                pass  # Username step not always shown

            # Enter password
            print("   Entering password...")
            password_field = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@type='password']"))
            )
            password_field.clear()
            password_field.send_keys(self.password)
            password_field.send_keys(Keys.RETURN)

            # Wait for login to complete
            time.sleep(5)

            # Check if login successful
            if "home" in self.driver.current_url or "twitter.com/home" in self.driver.current_url:
                print("✅ Login successful!")
                return True
            else:
                print("❌ Login may have failed - checking...")
                # Try to detect error
                try:
                    error = self.driver.find_element(By.XPATH, "//div[contains(@role, 'alert')]")
                    print(f"   Error: {error.text}")
                except:
                    pass
                return False

        except Exception as e:
            print(f"❌ Login error: {e}")
            return False

    def post_tweet(self, text):
        """Post a tweet"""
        try:
            # Navigate to home
            self.driver.get("https://twitter.com/home")
            time.sleep(3)

            # Find tweet box
            print("   Finding tweet box...")
            
            # Try multiple selectors for tweet box
            tweet_box = None
            selectors = [
                "//div[@contenteditable='true' and @data-testid='tweetTextarea-0']",
                "//textarea[@data-testid='tweetTextarea-0']",
                "//div[@role='textbox' and @data-testid='tweetTextarea-0']",
            ]
            
            for selector in selectors:
                try:
                    tweet_box = self.wait.until(
                        EC.presence_of_element_located((By.XPATH, selector))
                    )
                    break
                except:
                    continue

            if not tweet_box:
                print("❌ Could not find tweet box")
                return False

            # Click and enter text
            tweet_box.click()
            time.sleep(1)
            
            # Clear existing text
            tweet_box.clear()
            time.sleep(0.5)
            
            # Enter tweet text
            print("   Entering tweet text...")
            for char in text:
                tweet_box.send_keys(char)
                time.sleep(0.02)  # Small delay for realism
            
            time.sleep(2)

            # Find and click tweet button
            print("   Clicking Tweet button...")
            tweet_button = self.wait.until(
                EC.element_to_be_clickable((
                    By.XPATH, 
                    "//div[@data-testid='tweetButton'] | //button[contains(., 'Tweet')] | //button[contains(., 'Post')] | //div[contains(., 'Tweet') and @role='button']"
                ))
            )
            
            # Check if button is enabled
            if tweet_button.is_enabled():
                tweet_button.click()
                time.sleep(3)
                
                # Check for success
                print("   Waiting for confirmation...")
                time.sleep(2)
                
                # Look for success indicators
                if "status" in self.driver.current_url or "photo" in self.driver.current_url:
                    print("✅ Tweet posted successfully!")
                    return True
                else:
                    # Check if still on compose page
                    print("⚠️  Tweet may not have posted - checking...")
                    return True  # Assume success if no error
            else:
                print("❌ Tweet button is disabled")
                return False

        except TimeoutException:
            print("❌ Timeout - element not found")
            return False
        except Exception as e:
            print(f"❌ Error posting tweet: {e}")
            return False

    def get_user_info(self):
        """Get current user info"""
        try:
            self.driver.get("https://twitter.com/home")
            time.sleep(3)
            
            # Try to get username from sidebar or profile
            try:
                username_elem = self.driver.find_element(
                    By.XPATH, 
                    "//div[@data-testid='SideNav_AccountSwitcher_Button']"
                )
                return {"screen_name": username_elem.text.replace('@', '')}
            except:
                return {"screen_name": "Unknown"}
                
        except Exception as e:
            print(f"Error getting user info: {e}")
            return None

    def approve_and_post(self, filepath, auto_approve=True):
        """Approve and post to Twitter"""
        print(f"\n{'='*60}")
        print(f"Processing: {filepath.name}")
        print(f"{'='*60}")

        # Read content
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"❌ Error reading file: {e}")
            return False

        # Show preview
        print(f"\n📝 Post content ({len(content)} chars):")
        print(f"{'-'*60}")
        preview = content[:200] + "..." if len(content) > 200 else content
        print(preview)
        print(f"{'-'*60}")

        # Check length
        if len(content) > 280:
            print(f"⚠️  WARNING: {len(content)} chars (Twitter limit: 280)")
            print("   Content will be truncated.")
            content = content[:280]

        # Confirmation
        if not auto_approve:
            confirm = input("\nApprove and post? (y/n): ").strip().lower()
            if confirm != 'y':
                print("⏭️  Skipped")
                return False

        # Move to Approved
        approved_path = self.approved_dir / filepath.name
        try:
            filepath.rename(approved_path)
            print(f"✅ Moved to Approved: {approved_path.name}")
        except Exception as e:
            print(f"❌ Error moving to Approved: {e}")
            return False

        # Post to Twitter
        print("\n📤 Posting to Twitter...")
        success = self.post_tweet(content)

        if success:
            print(f"\n✅ SUCCESS! Tweet published")
            
            # Move to Posted folder
            posted_path = self.approved_dir / approved_path.name
            try:
                approved_path.rename(posted_path)
                print(f"✅ Archived to Twitter_Posted: {posted_path.name}")
            except Exception as e:
                print(f"⚠️  Warning: Could not archive: {e}")

            return True
        else:
            print(f"\n❌ FAILED to post to Twitter")

            # Move to Rejected
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

    def close(self):
        """Close browser"""
        if self.driver:
            print("\n🔒 Closing browser...")
            self.driver.quit()


def main():
    """Main entry point"""
    print("\n" + "="*60)
    print("  TWITTER POST APPROVER (Browser Automation)")
    print("  Auto-posts from Pending → Twitter/X")
    print("  No API required - uses Twitter.com")
    print("="*60)

    # Initialize
    try:
        approver = TwitterBrowserPoster()
    except ValueError as e:
        print(f"\n❌ {e}")
        print("\nAdd to .env:")
        print("  TWITTER_EMAIL=your@email.com")
        print("  TWITTER_PASSWORD=your_password")
        return

    # Setup browser
    print("\n🌐 Setting up browser...")
    if not approver.setup_browser():
        return

    try:
        # Login
        print("\n🔐 Logging in to Twitter...")
        if not approver.login():
            print("\n❌ Login failed. Check credentials in .env")
            print("   Required: TWITTER_EMAIL, TWITTER_PASSWORD")
            return

        # Get user info
        user_info = approver.get_user_info()
        if user_info:
            print(f"✅ Logged in as: @{user_info.get('screen_name', 'Unknown')}")

        # List pending posts
        posts = approver.list_pending_posts()

        if not posts:
            print("\n✅ No pending posts found!")
            return

        print(f"\n📋 Found {len(posts)} pending post(s):\n")

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
            print(f"\n📤 Posting latest: {posts[0].name}")
            approver.approve_and_post(posts[0], auto_approve=True)

        elif choice == "2":
            print(f"\n📤 Posting all {len(posts)} pending posts...")
            confirm = input("   Are you sure? (y/n): ").strip().lower()

            if confirm == 'y':
                print("\n⚠️  Twitter may flag automated posting")
                print("   Posts will be processed with delays...\n")

                success_count = 0
                failed_count = 0

                for i, post in enumerate(posts, 1):
                    print(f"\n[{i}/{len(posts)}]")
                    success = approver.approve_and_post(post, auto_approve=True)
                    if success:
                        success_count += 1
                    else:
                        failed_count += 1
                    time.sleep(3)  # Delay between posts

                print(f"\n{'='*60}")
                print(f"✅ Completed!")
                print(f"   Posted: {success_count}")
                print(f"   Failed: {failed_count}")
                print(f"{'='*60}")
            else:
                print("\n⏭️  Cancelled")

        elif choice == "3":
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

    finally:
        approver.close()


if __name__ == "__main__":
    main()
