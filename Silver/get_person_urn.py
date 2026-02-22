"""
Get LinkedIn Person URN
Helps you find your Person URN for API posting
"""

import os
import json
import requests

# Manual .env parser (more reliable)
def load_env_token():
    try:
        with open('.env', 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('LINKEDIN_ACCESS_TOKEN=') and not line.startswith('#'):
                    return line.split('=', 1)[1].strip()
    except Exception as e:
        print(f"Error reading .env: {e}")
    return None

print("="*60)
print("LinkedIn Person URN Finder")
print("="*60)
print()

# Get token
token = load_env_token()
if not token:
    print("No access token found in .env")
    print("Please authenticate first: python quick_auth.py")
    exit(1)

print(f"Token loaded: {token[:30]}...")
print()

# Method 1: Try email endpoint
print("Method 1: Email endpoint...")
url = "https://api.linkedin.com/v2/emailAddress?q=members&projection=(elements*(handle~))"
headers = {
    "Authorization": f"Bearer {token}",
    "X-Restli-Protocol-Version": "2.0.0",
    "LinkedIn-Version": "202402"
}

try:
    response = requests.get(url, headers=headers, timeout=10)
    if response.status_code == 200:
        data = response.json()
        elements = data.get("elements", [])
        if elements:
            email = elements[0].get("handle~", {}).get("emailAddress", "")
            print(f"Email found: {email}")
            print("Note: Email endpoint worked but doesn't return URN directly")
        else:
            print("No email found")
    else:
        print(f"Email endpoint returned {response.status_code}")
except Exception as e:
    print(f"Email endpoint error: {e}")

print()

# Method 2: Try to get from existing posts
print("Method 2: Checking existing posts...")
url = "https://api.linkedin.com/v2/ugcPosts?q=members&projection=(elements*(author))"

try:
    response = requests.get(url, headers=headers, timeout=10)
    if response.status_code == 200:
        data = response.json()
        elements = data.get("elements", [])
        if elements:
            author = elements[0].get("author", "")
            if author.startswith("urn:li:member:"):
                person_urn = author.replace("urn:li:member:", "")
                print(f"SUCCESS! Found Person URN: {person_urn}")
                
                # Save to .env
                env_path = ".env"
                with open(env_path, 'r') as f:
                    lines = f.readlines()
                
                found = False
                for i, line in enumerate(lines):
                    if line.startswith("LINKEDIN_PERSON_URN="):
                        lines[i] = f"LINKEDIN_PERSON_URN={person_urn}\n"
                        found = True
                        break
                
                if not found:
                    lines.append(f"\nLINKEDIN_PERSON_URN={person_urn}\n")
                
                with open(env_path, 'w') as f:
                    f.writelines(lines)
                
                print(f"Person URN saved to .env!")
                print("\nNow you can run: python auto_linkedin_poster.py --post-now")
                exit(0)
            else:
                print(f"Author found but unexpected format: {author}")
        else:
            print("No existing posts found")
    else:
        print(f"Posts endpoint returned {response.status_code}: {response.text[:100]}")
except Exception as e:
    print(f"Posts endpoint error: {e}")

print()

# Method 3: Manual instructions
print("Method 3: Manual extraction (required if above failed)")
print()
print("Steps to get your Person URN manually:")
print()
print("1. Go to https://www.linkedin.com/feed/")
print("2. Press F12 to open Developer Tools")
print("3. Go to 'Network' tab")
print("4. Create a post on LinkedIn (can be anything)")
print("5. In Network tab, look for request to 'api.linkedin.com/v2/ugcPosts'")
print("6. Click on that request")
print("7. Go to 'Payload' or 'Request' tab")
print("8. Find the 'author' field, it will look like:")
print('   "author": "urn:li:member:123456789"')
print("9. Copy the number (123456789)")
print()
print("10. Add to .env file:")
print("    LINKEDIN_PERSON_URN=123456789")
print()
print("="*60)
