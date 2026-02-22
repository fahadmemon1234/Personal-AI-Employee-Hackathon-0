"""
LinkedIn Browser Poster - Fallback
Posts to LinkedIn using browser automation when API permissions are limited
"""

import asyncio
import datetime
from pathlib import Path
from playwright.async_api import async_playwright
import os
from dotenv import load_dotenv

load_dotenv()


class LinkedInBrowserPoster:
    """Posts to LinkedIn using browser automation"""

    def __init__(self):
        self.pending_approval_dir = Path("Pending_Approval")
        self.posted_dir = Path("Posted")
        self.dashboard_file = "Dashboard.md"
        self.pending_approval_dir.mkdir(exist_ok=True)
        self.posted_dir.mkdir(exist_ok=True)

    async def post_content(self, content):
        """Post content to LinkedIn via browser"""
        playwright = await async_playwright().start()
        
        # Use persistent context to keep LinkedIn session
        browser = await playwright.chromium.launch_persistent_context(
            Path("linkedin_data") / "user_data",
            headless=False,  # Must be visible for user to login
            viewport={'width': 1280, 'height': 800}
        )
        
        page = await browser.new_page()
        
        try:
            print("Navigating to LinkedIn...")
            await page.goto("https://www.linkedin.com/", timeout=60000)
            await page.wait_for_load_state('networkidle')
            
            # Check if logged in
            try:
                await page.wait_for_selector(
                    'button[aria-label="Start a post"], div[aria-label="Start a post"]',
                    timeout=30000
                )
                print("[OK] Logged in to LinkedIn")
            except Exception as e:
                print("Please log in to LinkedIn in the browser window...")
                print("(You have 2 minutes)")
                try:
                    await page.wait_for_selector(
                        'button[aria-label="Start a post"]',
                        timeout=120000
                    )
                    print("[OK] Login detected!")
                except:
                    print("Login timeout")
                    return False
            
            # Click Start a post
            post_buttons = await page.query_selector_all(
                'button[aria-label="Start a post"], div[aria-label="Start a post"]'
            )
            if not post_buttons:
                print("Could not find 'Start a post' button")
                return False
                
            await post_buttons[0].click()
            await page.wait_for_load_state('networkidle')
            await asyncio.sleep(2)
            
            # Find editor and type content
            editors = await page.query_selector_all(
                'div[contenteditable="true"][aria-label="What do you want to talk about?"],'
                'div[contenteditable="true"]'
            )
            
            if not editors:
                print("Could not find text editor")
                return False
                
            await editors[0].focus()
            await page.keyboard.press('Control+A')
            await page.keyboard.press('Delete')
            await editors[0].type(content, delay=50)
            print("[OK] Content entered")
            
            await asyncio.sleep(2)
            
            # Click Post button
            post_btns = await page.query_selector_all(
                'button[aria-label="Post"], button:has-text("Post")'
            )
            
            if not post_btns:
                print("Could not find Post button")
                return False
                
            await post_btns[0].click()
            print("[OK] Post submitted!")
            await asyncio.sleep(3)
            return True
                
        except Exception as e:
            print(f"Error: {e}")
            return False
        finally:
            await browser.close()
            await playwright.stop()

    def log_post(self, content):
        """Log post to dashboard"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"\n### LinkedIn Post - {timestamp}\n{content}\n\n---\n"
        with open(self.dashboard_file, 'a', encoding='utf-8') as f:
            f.write(entry)

    async def post_pending(self, content=None):
        """Post content to LinkedIn"""
        if content is None:
            post_files = list(self.pending_approval_dir.glob("linkedin_post_*.txt"))
            
            if not post_files:
                print("No pending posts found.")
                return
            
            print(f"Found {len(post_files)} pending post(s)\n")
            
            for post_file in post_files:
                with open(post_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                print(f"Posting: {post_file.name}")
                print(f"Content: {content[:100]}...\n")
                
                success = await self.post_content(content)
                
                if success:
                    archive_path = self.posted_dir / post_file.name
                    post_file.rename(archive_path)
                    self.log_post(content)
                    print(f"[OK] Posted and archived!\n")
                else:
                    print(f"[FAIL] Failed to post\n")
                
                if len(post_files) > 1:
                    await asyncio.sleep(5)
        else:
            # Post direct content
            success = await self.post_content(content)
            if success:
                self.log_post(content)


async def main():
    import sys
    
    poster = LinkedInBrowserPoster()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--post":
        content = " ".join(sys.argv[2:])
        await poster.post_content(content)
    else:
        await poster.post_pending()


if __name__ == "__main__":
    asyncio.run(main())
