"""
Send Test Email from MCP System
Uses credentials from .env file
"""

import os
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Set UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables
load_dotenv()

# Configuration from .env
SENDER_EMAIL = os.getenv('GMAIL_SENDER_EMAIL', '')
APP_PASSWORD = os.getenv('GMAIL_APP_PASSWORD', '')
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))

# Email details
RECEIVER_EMAIL = SENDER_EMAIL  # Send to self for testing
SUBJECT = "🤖 Test Email from MCP System"
BODY = """
Hello!

This is a test email from your MCP (Model Context Protocol) Email System.

✅ Email MCP Server is working correctly!
✅ Gmail SMTP integration is active!
✅ You can now send automated emails!

---
Sent by: AI Digital FTE Employee
System: MCP Email Server
"""

print("\n" + "="*70)
print("Sending Test Email via Gmail SMTP")
print("="*70)
print(f"\nFrom: {SENDER_EMAIL}")
print(f"To: {RECEIVER_EMAIL}")
print(f"Subject: {SUBJECT}")
print("\nSending...")

try:
    # Create message
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL
    msg['Subject'] = SUBJECT
    msg.attach(MIMEText(BODY, 'plain'))
    
    # Connect and send
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(SENDER_EMAIL, APP_PASSWORD)
    
    text = msg.as_string()
    server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, text)
    server.quit()
    
    print("\n" + "="*70)
    print("✅ EMAIL SENT SUCCESSFULLY!")
    print("="*70)
    print(f"\nCheck inbox: {RECEIVER_EMAIL}")
    print("\nNext steps:")
    print("1. Check your email inbox")
    print("2. Start Email MCP Server: python mcp_email_server.py")
    print("3. Send emails via API endpoint")
    
except smtplib.SMTPAuthenticationError:
    print("\n" + "="*70)
    print("❌ AUTHENTICATION FAILED!")
    print("="*70)
    print("\nPossible issues:")
    print("1. App Password is incorrect")
    print("2. 2-Factor Authentication not enabled")
    print("\nFix:")
    print("1. Go to: https://myaccount.google.com/apppasswords")
    print("2. Generate NEW App Password")
    print("3. Update .env file: GMAIL_APP_PASSWORD=newpassword")
    
except Exception as e:
    print(f"\n❌ Error: {e}")

input("\nPress Enter to exit...")
