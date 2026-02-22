"""
Manual LinkedIn Auth - Enter code manually
"""

import os
import json
import datetime
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

print("="*60)
print("LinkedIn Manual Authentication")
print("="*60)
print()

# Step 1: Open authorization URL
auth_url = "https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id=77yksu2wc0ldwv&redirect_uri=http://localhost:8080/callback&scope=w_member_social"

print("Step 1: Open this URL in your browser:")
print()
print(auth_url)
print()
print("Step 2: Authorize the application")
print("Step 3: Copy the 'code' parameter from the redirect URL")
print()

# Step 2: Get authorization code
code = input("Enter the authorization code: ").strip()

if not code:
    print("No code entered. Exiting.")
    exit(1)

print("\nExchanging code for token...")

# Step 3: Exchange code for token
client_id = os.getenv("LINKEDIN_CLIENT_ID", "77yksu2wc0ldwv")
client_secret = os.getenv("LINKEDIN_CLIENT_SECRET")
redirect_uri = "http://localhost:8080/callback"

token_url = "https://www.linkedin.com/oauth/v2/accessToken"
data = {
    "grant_type": "authorization_code",
    "code": code,
    "redirect_uri": redirect_uri,
    "client_id": client_id,
    "client_secret": client_secret
}

response = requests.post(token_url, data=data)

if response.status_code == 200:
    token_data = response.json()
    print("\nToken received!")
    
    # Add expiration
    token_data["expires_at"] = datetime.datetime.now().timestamp() + token_data.get("expires_in", 3600)
    
    # Save token
    token_file = "linkedin_token.json"
    with open(token_file, 'w') as f:
        json.dump(token_data, f, indent=2)
    print(f"Token saved to {token_file}")
    
    # Update .env
    access_token = token_data["access_token"]
    env_path = Path(".env")
    if env_path.exists():
        with open(env_path, 'r') as f:
            lines = f.readlines()
        
        for i, line in enumerate(lines):
            if line.startswith("LINKEDIN_ACCESS_TOKEN="):
                lines[i] = f"LINKEDIN_ACCESS_TOKEN={access_token}\n"
                break
        
        with open(env_path, 'w') as f:
            f.writelines(lines)
        print(".env updated")
    
    # Try to get person URN from existing posts
    print("\nFetching Person URN...")
    headers = {
        "Authorization": f"Bearer {access_token}",
        "X-Restli-Protocol-Version": "2.0.0",
        "LinkedIn-Version": "202402"
    }
    
    # Try to get from posts
    url = "https://api.linkedin.com/v2/posts?q=members&projection=(elements*(author))"
    try:
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            data = resp.json()
            elements = data.get("elements", [])
            if elements:
                author = elements[0].get("author", "")
                if author.startswith("urn:li:person:"):
                    person_urn = author.replace("urn:li:person:", "")
                    print(f"Person URN: {person_urn}")
                    
                    # Save to .env
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
                    print("Person URN saved to .env")
    except Exception as e:
        print(f"Could not get Person URN: {e}")
    
    print("\n" + "="*60)
    print("SUCCESS! Authentication complete!")
    print("="*60)
    print("\nNow run:")
    print("  python auto_linkedin_poster.py --post-now")
    print("="*60)

else:
    print(f"\nFailed: {response.status_code}")
    print(f"Response: {response.text}")
