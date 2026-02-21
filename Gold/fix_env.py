"""
fix_env.py
Updates .env file with correct database name and adds helpful comments
"""

import os
from pathlib import Path

env_path = Path(".env")

if not env_path.exists():
    print("Error: .env file not found!")
    exit(1)

with open(env_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix Odoo database name (try lowercase first)
content = content.replace(
    "ODOO_DB=FahadMemon",
    "ODOO_DB=fahadmemon  # Try: fahadmemon or fahadmemon131@gmail.com"
)

# Add helpful comments for Facebook/Instagram
content = content.replace(
    "META_ACCESS_TOKEN=your_meta_access_token",
    "META_ACCESS_TOKEN=your_meta_access_token  # Get from https://developers.facebook.com/"
)

content = content.replace(
    "FACEBOOK_PAGE_ID=your_facebook_page_id",
    "FACEBOOK_PAGE_ID=your_facebook_page_id  # Your Facebook Page ID"
)

content = content.replace(
    "INSTAGRAM_BUSINESS_ACCOUNT_ID=your_instagram_business_account_id",
    "INSTAGRAM_BUSINESS_ACCOUNT_ID=your_instagram_business_account_id  # Instagram Business Account ID"
)

with open(env_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("[OK] .env file updated successfully!")
print("\nNotes:")
print("1. Odoo database name changed to lowercase 'fahadmemon'")
print("2. If that doesn't work, try using your email as database name")
print("3. Facebook/Instagram credentials need to be configured for social media features")
print("\nTo get Facebook/Instagram credentials:")
print("  1. Go to https://developers.facebook.com/")
print("  2. Create an app")
print("  3. Get Access Token, Page ID, and Instagram Business Account ID")
print("  4. Update .env file with real values")
