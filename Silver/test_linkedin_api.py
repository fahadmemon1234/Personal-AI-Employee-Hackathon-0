"""Test LinkedIn UGC Posts API"""
import requests
import json

with open('linkedin_token.json') as f:
    token = json.load(f)['access_token']

print("Testing LinkedIn UGC Posts API...")
print("Endpoint: https://api.linkedin.com/v2/ugcPosts")

url = 'https://api.linkedin.com/v2/ugcPosts'
headers = {
    'Authorization': f'Bearer {token}',
    'X-Restli-Protocol-Version': '2.0.0',
    'Content-Type': 'application/json',
    'LinkedIn-Version': '202402'
}

# UGC Posts API format
payload = {
    "author": "urn:li:person:me",
    "lifecycleState": "PUBLISHED",
    "specificContent": {
        "com.linkedin.ugc.ShareContent": {
            "shareCommentary": {
                "text": "Test post from UGC Posts API - please ignore"
            },
            "shareMediaCategory": "NONE"
        }
    },
    "visibility": {
        "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
    }
}

print(f"\nPayload: {json.dumps(payload, indent=2)}")
print("\nSending request...")

try:
    response = requests.post(url, json=payload, headers=headers, timeout=30)
    print(f"\nStatus: {response.status_code}")
    print(f"Response: {response.text[:500] if response.text else 'Empty'}")
    
    if response.status_code == 201:
        print("\nSUCCESS! Post created!")
        post_id = response.json().get('id', 'Unknown')
        print(f"Post ID: {post_id}")
    else:
        print(f"\nFailed with status {response.status_code}")
        
except Exception as e:
    print(f"\nError: {e}")
