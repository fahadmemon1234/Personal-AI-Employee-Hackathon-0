"""
Simple test to trigger logging in the watcher scripts
"""

from gmail_watcher import GmailWatcher
from whatsapp_watcher import WhatsAppWatcher
import asyncio

def test_gmail_logging():
    """Test Gmail watcher logging"""
    print("Testing Gmail Watcher logging...")
    watcher = GmailWatcher()
    # This will attempt to authenticate and log an action
    watcher.log_action("Test action from Gmail Watcher")
    print("Gmail Watcher test completed")

async def test_whatsapp_logging():
    """Test WhatsApp watcher logging"""
    print("Testing WhatsApp Watcher logging...")
    watcher = WhatsAppWatcher()
    # This will log an action
    watcher.log_action("Test action from WhatsApp Watcher")
    print("WhatsApp Watcher test completed")

if __name__ == "__main__":
    test_gmail_logging()
    
    # Run the async function for WhatsApp
    asyncio.run(test_whatsapp_logging())
    
    print("Logging test completed. Check Audit_Log.md for entries.")