"""
WhatsApp Watcher Script
Monitors WhatsApp Web for specific keywords and saves messages as .md files in /Needs_Action
"""

import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright
import re


class WhatsAppWatcher:
    """Watches WhatsApp Web for specific keywords and saves messages as .md files"""
    
    def __init__(self, data_dir="whatsapp_data", needs_action_dir="Needs_Action"):
        self.data_dir = Path(data_dir)
        self.needs_action_dir = Path(needs_action_dir)
        self.browser_context = None
        self.page = None
        
        # Create directories if they don't exist
        self.data_dir.mkdir(exist_ok=True)
        self.needs_action_dir.mkdir(exist_ok=True)
        
        # Keywords to monitor for
        self.keywords = ['urgent', 'payment', 'help', 'emergency', 'asap', 'important']
    
    async def initialize_browser(self):
        """Initialize the browser with persistent context"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch_persistent_context(
            self.data_dir / "user_data",  # Persistent storage for WhatsApp session
            headless=False,  # Set to True if you don't want to see the browser
            viewport={'width': 1280, 'height': 800},
            args=[
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
                '--no-sandbox'
            ]
        )
        
        # Navigate to WhatsApp Web
        self.page = await self.browser.new_page()
        await self.page.goto("https://web.whatsapp.com/")
        
        # Wait for WhatsApp to load and check if user is already logged in
        print("Checking WhatsApp Web login status...")
        try:
            # Wait for either the QR code or the main app to load
            await self.page.wait_for_selector(
                'div[data-testid="qr-code"]', 
                timeout=5000
            )
            print("QR code detected. Please scan the QR code to log in.")
            print("After logging in, restart this script.")
            return False
        except:
            # If QR code is not found, user is probably already logged in
            print("Already logged in to WhatsApp Web.")
            return True
    
    async def wait_for_messages(self):
        """Wait for new messages in chats"""
        print("Monitoring WhatsApp for keywords...")
        
        # Wait for WhatsApp to load by looking for any recognizable element
        try:
            # Wait for main WhatsApp containers - using broader selectors
            await self.page.wait_for_selector('#app, .app-wrapper-web, div[role="grid"]', timeout=15000)
        except:
            print("Could not find expected WhatsApp elements. The UI might have changed.")
            return
        
        # Continuously monitor for new messages
        while True:
            try:
                # Look for chat elements using broader selectors
                # Try to find the sidebar with chats
                try:
                    # Wait for the chat list sidebar to be available
                    await self.page.wait_for_selector('#pane-side, [data-testid="chat-list-sidebar"]', timeout=5000)
                    
                    # Get all chat elements
                    chat_elements = await self.page.query_selector_all('#pane-side .chat, #pane-side [tabindex="-1"]')
                    
                    for chat_element in chat_elements:
                        try:
                            # Get the chat name before clicking
                            chat_name = "Unknown Chat"
                            name_selectors = ['.chat-title span', 'span[title]', '.emoji-text-wrapper', '.selectable-text']
                            
                            for selector in name_selectors:
                                try:
                                    name_element = await chat_element.query_selector(selector)
                                    if name_element:
                                        chat_name = await name_element.inner_text()
                                        if chat_name.strip():
                                            break
                                except:
                                    continue
                            
                            # Click on the chat to view messages
                            await chat_element.click()
                            
                            # Wait for messages to load in the chat window
                            await self.page.wait_for_selector('#main .copyable-text, #main .message', timeout=3000)
                            
                            # Get all message elements
                            message_elements = await self.page.query_selector_all('#main .copyable-text, #main .message, #main [data-id]')
                            
                            for msg_element in message_elements:
                                try:
                                    # Get the message text
                                    message_text = ""
                                    
                                    # Try different ways to extract the message text
                                    try:
                                        message_text = await msg_element.inner_text()
                                    except:
                                        pass
                                    
                                    # If innerText didn't work, try getting text from child elements
                                    if not message_text.strip():
                                        try:
                                            spans = await msg_element.query_selector_all('span')
                                            texts = []
                                            for span in spans:
                                                try:
                                                    text = await span.inner_text()
                                                    if text.strip():
                                                        texts.append(text.strip())
                                                except:
                                                    continue
                                            message_text = ' '.join(texts)
                                        except:
                                            pass
                                    
                                    # Check if message contains any of our keywords
                                    if message_text and self.contains_keywords(message_text):
                                        # Save the message
                                        await self.save_message(chat_name, message_text)
                                except Exception as e:
                                    # Skip problematic messages
                                    continue
                        
                        except Exception as e:
                            # Skip problematic chats
                            continue
                
                except Exception as e:
                    print(f"Error processing chat list: {e}")
                
                # Wait before checking again
                await asyncio.sleep(10)
                
            except Exception as e:
                print(f"Error monitoring messages: {e}")
                await asyncio.sleep(5)
    
    def contains_keywords(self, text):
        """Check if text contains any of the monitored keywords"""
        text_lower = text.lower()
        for keyword in self.keywords:
            if keyword in text_lower:
                return True
        return False
    
    async def get_current_chat_name(self):
        """Get the name of the current chat"""
        try:
            # Try multiple possible selectors for chat title
            chat_title_selectors = [
                'div[data-testid="conversation-info-title"]',
                '#main header span:first-child',
                '.chat-title',
                'header span[title]'
            ]
            
            for selector in chat_title_selectors:
                try:
                    chat_title_element = await self.page.query_selector(selector)
                    if chat_title_element:
                        title = await chat_title_element.inner_text()
                        if title.strip():
                            return title.strip()
                except:
                    continue
            
            return "Unknown Chat"
        except:
            return "Unknown Chat"
    
    async def save_message(self, chat_name, message_text):
        """Save the message as a markdown file in Needs_Action folder"""
        # Create a safe filename from the chat name
        safe_chat_name = "".join(c for c in chat_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        if not safe_chat_name:
            safe_chat_name = "unknown_chat"
        
        # Add timestamp to filename to avoid conflicts
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"whatsapp_{safe_chat_name}_{timestamp}.md"
        filepath = self.needs_action_dir / filename
        
        # Create markdown content
        md_content = f"""# WhatsApp Message from {chat_name}

**Detected Keyword(s):** {self.find_keywords(message_text)}

**Received:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

**Chat:** {chat_name}

---

## Message Content:

{message_text}

---

*This message was automatically saved by the WhatsApp Watcher*
"""
        
        # Write the markdown file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(md_content)

        print(f"Saved WhatsApp message from '{chat_name}' to {filepath}")

        # Notify the agent about the new message
        await self.notify_agent(chat_name, message_text)
        
        # Log the action to Audit_Log.md
        self.log_action(f"WhatsApp Watcher saved message from {chat_name}: {message_text[:50]}{'...' if len(message_text) > 50 else ''}")
    
    def find_keywords(self, text):
        """Find which keywords are present in the text"""
        text_lower = text.lower()
        found_keywords = []
        for keyword in self.keywords:
            if keyword in text_lower:
                found_keywords.append(keyword)
        return ", ".join(found_keywords) if found_keywords else "None"
    
    async def notify_agent(self, chat_name, message_text):
        """Notify the agent about a new WhatsApp lead"""
        # Create a notification file to alert the agent
        notification_file = self.needs_action_dir / f"notification_whatsapp_alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        notification_content = f"""NEW WHATSAPP LEAD DETECTED

From: {chat_name}
Keywords: {self.find_keywords(message_text)}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Message Preview:
{message_text[:200]}...

Action Required: Review the full message in {self.needs_action_dir}
"""
        
        with open(notification_file, 'w', encoding='utf-8') as f:
            f.write(notification_content)
        
        print(f"Agent notified about new WhatsApp lead from {chat_name}")

    def log_action(self, action_description):
        """Log an action to Audit_Log.md"""
        audit_log_path = Path("Audit_Log.md")
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        log_entry = f"- [{timestamp}] {action_description}\n"
        
        # Append the log entry to the audit log file
        with open(audit_log_path, 'a', encoding='utf-8') as f:
            f.write(log_entry)

    async def run(self):
        """Run the WhatsApp watcher"""
        print("Initializing WhatsApp Watcher...")
        
        # Initialize the browser
        if not await self.initialize_browser():
            print("Failed to initialize browser. Please log in to WhatsApp Web first.")
            return
        
        try:
            # Start monitoring for messages
            await self.wait_for_messages()
        except KeyboardInterrupt:
            print("\nStopping WhatsApp Watcher...")
        finally:
            await self.close()
    
    async def close(self):
        """Close the browser and clean up"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()


class WhatsAppAgentSkill:
    """Agent skill to integrate WhatsApp monitoring with the AI agent"""
    
    def __init__(self):
        self.watcher = WhatsAppWatcher()
    
    async def start_monitoring(self):
        """Start the WhatsApp monitoring"""
        await self.watcher.run()


def main():
    """Main function to run the WhatsApp watcher"""
    print("Initializing WhatsApp Watcher...")
    print("Note: You need to be logged in to WhatsApp Web for this to work.")
    print("If you're not logged in, scan the QR code when prompted.")
    
    async def run_watcher():
        skill = WhatsAppAgentSkill()
        await skill.start_monitoring()
    
    # Run the async function
    try:
        asyncio.run(run_watcher())
    except KeyboardInterrupt:
        print("\nWhatsApp Watcher stopped by user.")


if __name__ == "__main__":
    main()