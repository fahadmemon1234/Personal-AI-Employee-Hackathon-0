"""
Test Twitter Credentials
Simple script to test Twitter API connectivity
"""

import os
import requests
import base64
import hmac
import hashlib
import time
from urllib.parse import urlencode, quote
from dotenv import load_dotenv

load_dotenv()

# Get credentials
api_key = os.getenv("TWITTER_API_KEY")
api_secret = os.getenv("TWITTER_API_SECRET")
access_token = os.getenv("TWITTER_ACCESS_TOKEN")
access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

print("="*60)
print("TWITTER CREDENTIALS TEST")
print("="*60)

print(f"\nCredentials loaded:")
print(f"  API Key: {api_key[:20]}...")
print(f"  API Secret: {api_secret[:20]}...")
print(f"  Access Token: {access_token[:30]}...")
print(f"  Access Token Secret: {access_token_secret[:20]}...")

def generate_oauth_signature(method, url, params, api_secret, access_token_secret):
    """Generate OAuth 1.0a signature"""
    normalized_params = urlencode(sorted(params.items()))
    base_string = f"{method.upper()}&{quote(url, safe='')}&{quote(normalized_params, safe='')}"
    signing_key = f"{api_secret}&{access_token_secret}"
    
    signature = hmac.new(
        signing_key.encode('ascii'),
        base_string.encode('ascii'),
        hashlib.sha1
    ).digest()
    
    return base64.b64encode(signature).decode('ascii')

def get_oauth_headers(method, url, api_key, api_secret, access_token, access_token_secret, extra_params=None):
    """Generate OAuth 1.0a headers"""
    oauth_params = {
        'oauth_consumer_key': api_key,
        'oauth_token': access_token,
        'oauth_nonce': str(int(time.time() * 1000000)),
        'oauth_timestamp': str(int(time.time())),
        'oauth_signature_method': 'HMAC-SHA1',
        'oauth_version': '1.0'
    }
    
    if extra_params:
        oauth_params.update(extra_params)
    
    signature = generate_oauth_signature(method, url, oauth_params, api_secret, access_token_secret)
    oauth_params['oauth_signature'] = signature
    
    auth_header_params = []
    for key, value in oauth_params.items():
        auth_header_params.append(f'{key}="{quote(str(value), safe="")}"')
    
    authorization_header = 'OAuth ' + ', '.join(sorted(auth_header_params))
    
    return {'Authorization': authorization_header}

# Test 1: OAuth 2.0 Bearer Token
print("\n" + "-"*60)
print("Test 1: OAuth 2.0 Bearer Token")
print("-"*60)

try:
    key_secret = f"{api_key}:{api_secret}".encode('ascii')
    b64_encoded_key = base64.b64encode(key_secret).decode('ascii')
    
    url = "https://api.twitter.com/oauth2/token"
    headers = {
        "Authorization": f"Basic {b64_encoded_key}",
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"
    }
    data = {"grant_type": "client_credentials"}
    
    response = requests.post(url, headers=headers, data=data, timeout=30)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        bearer_token = result.get("access_token")
        print(f"✅ Bearer token obtained: {bearer_token[:50]}...")
        
        # Test bearer token
        print("\nTesting bearer token...")
        test_url = "https://api.twitter.com/2/users/me"
        test_headers = {"Authorization": f"Bearer {bearer_token}"}
        test_response = requests.get(test_url, headers=test_headers, timeout=30)
        print(f"Status: {test_response.status_code}")
        print(f"Response: {test_response.text[:200]}")
    else:
        print(f"❌ Failed: {response.text}")
        
except Exception as e:
    print(f"❌ Error: {e}")

# Test 2: OAuth 1.0a User Context
print("\n" + "-"*60)
print("Test 2: OAuth 1.0a User Context")
print("-"*60)

try:
    url = "https://api.twitter.com/1.1/account/verify_credentials.json"
    params = {'include_entities': 'false', 'skip_status': 'true'}
    headers = get_oauth_headers('GET', url, api_key, api_secret, access_token, access_token_secret, params)
    
    response = requests.get(url, headers=headers, params=params, timeout=30)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        user = response.json()
        print(f"✅ Connected as: @{user.get('screen_name', 'Unknown')}")
        print(f"   Name: {user.get('name', 'Unknown')}")
        print(f"   Followers: {user.get('followers_count', 0)}")
    else:
        print(f"❌ Failed: {response.text[:200]}")
        
except Exception as e:
    print(f"❌ Error: {e}")

# Test 3: Post a test tweet
print("\n" + "-"*60)
print("Test 3: Post Test Tweet")
print("-"*60)

try:
    url = "https://api.twitter.com/2/tweets"
    payload = {"text": "Test tweet from API - ignore"}
    headers = get_oauth_headers('POST', url, api_key, api_secret, access_token, access_token_secret)
    
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 201:
        result = response.json()
        tweet_id = result.get("data", {}).get("id")
        print(f"✅ Tweet posted: {tweet_id}")
    else:
        print(f"❌ Failed: {response.text[:200]}")
        
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*60)
print("TEST COMPLETE")
print("="*60)
