"""
Send Email via Gmail SMTP (App Password)
Simple setup - no OAuth required!
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

print("\n" + "="*70)
print("Gmail Email Sender (App Password)")
print("="*70)

# Get credentials
print("\nEnter your Gmail credentials:")
sender_email = input("Sender Gmail: ").strip()
app_password = input("App Password (16 chars): ").strip().replace(" ", "")
receiver_email = input("Receiver Email: ").strip()
subject = input("Subject: ").strip()
body = input("Message: ").strip()

print("\n" + "-"*70)
print("Sending email...")
print("-"*70)

try:
    # Create message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    
    # Add body
    msg.attach(MIMEText(body, 'plain'))
    
    # Connect and send
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(sender_email, app_password)
    
    text = msg.as_string()
    server.sendmail(sender_email, receiver_email, text)
    server.quit()
    
    print("\n" + "="*70)
    print("✅ EMAIL SENT SUCCESSFULLY!")
    print("="*70)
    print(f"\nTo: {receiver_email}")
    print(f"Subject: {subject}")
    print(f"\nCheck your inbox!")
    
except smtplib.SMTPAuthenticationError:
    print("\n" + "="*70)
    print("❌ AUTHENTICATION FAILED!")
    print("="*70)
    print("\nPossible reasons:")
    print("1. App Password is incorrect")
    print("2. 2-Factor Authentication is not enabled")
    print("3. Less secure apps access is blocked")
    print("\nSolution:")
    print("1. Go to: https://myaccount.google.com/apppasswords")
    print("2. Generate a NEW App Password")
    print("3. Try again with the new password")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nMake sure:")
    print("- Gmail account is valid")
    print("- App Password is correct (16 characters)")
    print("- Internet connection is working")

input("\nPress Enter to exit...")
