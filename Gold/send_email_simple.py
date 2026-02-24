"""
Simple Email Sender - SMTP based
Quick email sending without OAuth complexity
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from getpass import getpass

# Email Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Sender credentials
SENDER_EMAIL = input("Enter your Gmail address: ")
SENDER_PASSWORD = getpass("Enter your Gmail password (or App Password): ")

# Email details
RECEIVER_EMAIL = input("Enter receiver email: ")
SUBJECT = input("Enter subject: ")
BODY = input("Enter email body: ")

try:
    # Create message
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL
    msg['Subject'] = SUBJECT
    
    # Add body
    msg.attach(MIMEText(BODY, 'plain'))
    
    # Connect and send
    print(f"\nConnecting to {SMTP_SERVER}:{SMTP_PORT}...")
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(SENDER_EMAIL, SENDER_PASSWORD)
    
    text = msg.as_string()
    server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, text)
    server.quit()
    
    print("\n✅ Email sent successfully!")
    print(f"To: {RECEIVER_EMAIL}")
    print(f"Subject: {SUBJECT}")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nNote: If using Gmail, you may need to:")
    print("1. Enable 2-Factor Authentication")
    print("2. Generate an App Password at: https://myaccount.google.com/apppasswords")
    print("3. Use the App Password instead of your regular password")
