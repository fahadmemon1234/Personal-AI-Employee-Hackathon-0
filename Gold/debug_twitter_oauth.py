"""Debug Twitter OAuth"""
import os
import requests
import base64
import hmac
import hashlib
import time
from urllib.parse import urlencode, quote, urlparse
from dotenv import load_dotenv

load_dotenv()

# Get credentials
api_key = os.getenv("TWITTER_API_KEY")
api_secret = os.getenv("TWITTER_API_SECRET")
access_token = os.getenv("TWITTER_ACCESS_TOKEN")
access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

print("="*60)
print("TWITTER OAUTH DEBUG")
print("="*60)
print(f"\nCredentials:")
print(f"  API Key: {api_key}")
print(f"  API Secret: {api_secret[:20]}...")
print(f"  Access Token: {access_token}")
print(f"  Access Token Secret: {access_token_secret[:20]}...")

# Method 1: OAuth 1.0a with manual signature
def generate_oauth_signature(method, url, params, api_secret, access_token_secret):
    parsed = urlparse(url)
    base_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    
    normalized_params = "&".join(
        f"{quote(str(k), safe='')}={quote(str(v), safe='')}"
        for k, v in sorted(params.items())
    )
    
    base_string = f"{method.upper()}&{quote(base_url, safe='')}&{quote(normalized_params, safe='')}"
    signing_key = f"{api_secret}&{access_token_secret}"
    
    print(f"\nBase String:\n{base_string}")
    print(f"\nSigning Key:\n{signing_key}")
    
    signature = hmac.new(
        signing_key.encode('ascii'),
        base_string.encode('ascii'),
        hashlib.sha1
    ).digest()
    
    return base64.b64encode(signature).decode('ascii')

def get_oauth_header(method, url, extra_params=None):
    oauth_params = {
        'oauth_consumer_key': api_key,
        'oauth_token': access_token,
        'oauth_nonce': str(int(time.time() * 1000)),
        'oauth_timestamp': str(int(time.time())),
        'oauth_signature_method': 'HMAC-SHA1',
        'oauth_version': '1.0'
    }
    
    if extra_params:
        oauth_params.update(extra_params)
    
    signature = generate_oauth_signature(method, url, oauth_params, api_secret, access_token_secret)
    oauth_params['oauth_signature'] = signature
    
    print(f"\nSignature: {signature}")
    
    auth_params = []
    for key, value in oauth_params.items():
        auth_params.append(f'{key}="{quote(str(value), safe="")}"')
        print(f"  {key}: {value}")
    
    return {'Authorization': 'OAuth ' + ', '.join(auth_params)}

# Test verify_credentials
print("\n" + "="*60)
print("TEST 1: verify_credentials (OAuth 1.0a)")
print("="*60)

url = "https://api.twitter.com/1.1/account/verify_credentials.json"
params = {'include_entities': 'false', 'skip_status': 'true'}
headers = get_oauth_header('GET', url, params)

print(f"\nRequest URL: {url}")
print(f"\nHeaders:")
for k, v in headers.items():
    print(f"  {k}: {v[:100]}...")

response = requests.get(url, headers=headers, params=params, timeout=30)
print(f"\nResponse Status: {response.status_code}")
print(f"Response Body: {response.text}")

# Method 2: Try with requests-oauthlib style
print("\n" + "="*60)
print("TEST 2: Using requests with auth parameter")
print("="*60)

try:
    from requests_oauthlib import OAuth1
    
    auth = OAuth1(
        api_key,
        client_secret=api_secret,
        resource_owner_key=access_token,
        resource_owner_secret=access_token_secret
    )
    
    response = requests.get(
        "https://api.twitter.com/1.1/account/verify_credentials.json",
        auth=auth,
        params={'include_entities': 'false'},
        timeout=30
    )
    
    print(f"Response Status: {response.status_code}")
    print(f"Response Body: {response.text[:300]}")
    
except ImportError:
    print("requests-oauthlib not installed")
    print("Run: pip install requests-oauthlib")

print("\n" + "="*60)
