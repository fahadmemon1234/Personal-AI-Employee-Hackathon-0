"""
Direct Twitter Post Script - Post tweet directly using OAuth 1.0a
"""

import os
import sys
from dotenv import load_dotenv

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables
load_dotenv(override=True)

# Get credentials from .env
API_KEY = os.getenv('X_API_KEY', '')
API_SECRET = os.getenv('X_API_SECRET', '')
ACCESS_TOKEN = os.getenv('X_ACCESS_TOKEN', '')
ACCESS_TOKEN_SECRET = os.getenv('X_ACCESS_TOKEN_SECRET', '')

# Check if all credentials are available
if not API_SECRET or API_SECRET == 'your_x_api_secret_here':
    print("[ERROR] X_API_SECRET is not configured!")
    print("")
    print("Please get your API Secret from:")
    print("https://developer.twitter.com/en/portal/dashboard")
    print("")
    print("Steps:")
    print("1. Go to Twitter Developer Portal")
    print("2. Select your project/app")
    print("3. Go to 'Keys and Tokens' section")
    print("4. Copy 'API Key Secret'")
    print("5. Update .env file: X_API_SECRET=your_actual_secret_here")
    exit(1)

try:
    from requests_oauthlib import OAuth1Session
except ImportError:
    print("[ERROR] requests-oauthlib not installed!")
    print("Run: pip install requests-oauthlib")
    exit(1)

# Tweet content
tweet_text = "🚀 Excited to share our AI-driven automation project! Building intelligent agents that streamline business workflows and boost productivity. The future of work is here! #AI #Automation #Innovation #TechStartup"

# Twitter API v2 endpoint
url = "https://api.twitter.com/2/tweets"

# Create OAuth1 session
oauth = OAuth1Session(
    API_KEY,
    client_secret=API_SECRET,
    resource_owner_key=ACCESS_TOKEN,
    resource_owner_secret=ACCESS_TOKEN_SECRET
)

print(f"Posting tweet: {tweet_text[:100]}...")
print()

try:
    # Post the tweet
    response = oauth.post(url, json={'text': tweet_text})
    
    print(f"Response Status: {response.status_code}")
    
    if response.status_code in [200, 201]:
        result = response.json()
        tweet_id = result.get('data', {}).get('id', 'Unknown')
        print("[SUCCESS] Tweet posted!")
        print(f"Tweet ID: {tweet_id}")
        print(f"View at: https://twitter.com/software13702/status/{tweet_id}")
    else:
        print("[FAILED]")
        try:
            error_data = response.json()
            print(f"Error: {error_data}")
        except:
            print(f"Error: {response.text}")
            
except Exception as e:
    print(f"[ERROR] {str(e)}")
