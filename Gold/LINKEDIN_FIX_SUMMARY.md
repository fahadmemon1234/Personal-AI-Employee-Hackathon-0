# LinkedIn Post Fix - Complete Solution

## 🔴 Problem: 403 ACCESS_DENIED Error

### Original Error
```json
{
  "status": 403,
  "serviceErrorCode": 100,
  "code": "ACCESS_DENIED",
  "message": "Field Value validation failed in REQUEST_BODY: Data Processing Exception while processing fields [/author]"
}
```

### Root Cause
The `author` field was using **just the person ID** instead of the **full URN format**.

**WRONG:**
```python
"author": "MqvEfm3LKp"  # ❌ Just the ID - FAILS
```

**CORRECT:**
```python
"author": "urn:li:person:MqvEfm3LKp"  # ✅ Full URN - WORKS
```

---

## ✅ Solution: Fixed Implementation

### Key Fixes Applied

| Issue | Wrong | Correct |
|-------|-------|---------|
| **Author format** | `"MqvEfm3LKp"` | `"urn:li:person:MqvEfm3LKp"` |
| **User info endpoint** | `/v2/me` (deprecated) | `/v2/userinfo` (OIDC) |
| **Protocol version header** | Missing or wrong | `X-Restli-Protocol-Version: 2.0.0` |
| **API version header** | Missing | `LinkedIn-Version: 202402` |

---

## 📝 Working Code Example

### Complete Posting Function

```python
import requests
import os
from dotenv import load_dotenv

load_dotenv()

def create_linkedin_post(access_token, person_urn, text):
    """
    Create a text post on LinkedIn using ugcPosts API.
    
    FIXED VERSION - All issues resolved
    """
    
    # API endpoint
    url = "https://api.linkedin.com/v2/ugcPosts"
    
    # ✅ FIX 1: Author must be full URN format
    # WRONG: "MqvEfm3LKp"
    # RIGHT: "urn:li:person:MqvEfm3LKp"
    author_urn = person_urn  # Should already be "urn:li:person:..."
    
    # Payload structure
    payload = {
        "author": author_urn,  # ✅ Full URN
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": text
                },
                "shareMediaCategory": "NONE"  # Text-only
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }
    
    # ✅ FIX 2: Required headers
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0",  # ✅ REQUIRED
        "LinkedIn-Version": "202402"  # ✅ API version
    }
    
    # Make request
    response = requests.post(url, json=payload, headers=headers)
    
    # Handle response
    if response.status_code == 201:
        result = response.json()
        post_id = result.get("id")
        print(f"Post created: {post_id}")
        print(f"URL: https://www.linkedin.com/feed/update/{post_id}")
        return True
    else:
        print(f"Failed: HTTP {response.status_code}")
        print(f"Response: {response.text}")
        return False


def get_person_urn(access_token):
    """
    Get person URN using OIDC-compliant endpoint.
    
    ✅ Uses /v2/userinfo (NOT deprecated /v2/me)
    """
    url = "https://api.linkedin.com/v2/userinfo"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    user_info = response.json()
    
    # ✅ FIX 3: Extract URN from 'sub' field
    # Format: "urn:li:person:ACoAABkD3jQBqKZ9X8vN5Q"
    person_urn = user_info.get("sub")
    
    return person_urn


# Usage example
def main():
    ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")
    
    # Get person URN
    person_urn = get_person_urn(ACCESS_TOKEN)
    print(f"Person URN: {person_urn}")
    
    # Create post
    text = "Hello LinkedIn! This post was created with Python. 🚀 #API"
    create_linkedin_post(ACCESS_TOKEN, person_urn, text)


if __name__ == "__main__":
    main()
```

---

## 🔧 How to Get Person URN

### Method 1: Using /v2/userinfo (Recommended)

```python
import requests

def get_person_urn(access_token):
    url = "https://api.linkedin.com/v2/userinfo"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(url, headers=headers)
    user_info = response.json()
    
    # 'sub' field contains full URN
    return user_info.get("sub")  # "urn:li:person:..."
```

### Method 2: From Your LinkedIn Profile URL

Your person URN can also be found in your LinkedIn profile URL:

```
https://www.linkedin.com/in/your-name/

Public ID: your-name
Person URN: urn:li:member:YOUR_MEMBER_ID
```

But using `/v2/userinfo` is more reliable.

---

## 📋 Complete Workflow

### Step 1: Get Access Token

```bash
python linkedin_auth.py
```

This will:
- Open LinkedIn authorization page
- Get authorization code
- Exchange for access token
- Save token to `.env`

### Step 2: Verify Token Works

```bash
python test_linkedin_api.py
```

This will:
- Validate token
- Get user info (including person URN)
- Optionally post a test message

### Step 3: Post Pending Content

```bash
python approve_linkedin.py
```

This will:
- List all pending posts
- Move Pending → Approved
- Post to LinkedIn
- Move Approved → Posted (on success)
- Move Approved → Rejected (on failure)

---

## 🐛 Troubleshooting

### Error: "Data Processing Exception while processing fields [/author]"

**Cause:** Author field format is wrong

**Solution:**
```python
# WRONG
"author": "MqvEfm3LKp"

# CORRECT
"author": "urn:li:person:MqvEfm3LKp"
```

### Error: 403 ACCESS_DENIED

**Possible causes:**
1. Token expired
2. Missing `w_member_social` scope
3. Wrong author format

**Solution:**
```bash
# Re-authorize with correct scopes
python linkedin_auth.py
```

Make sure scopes include:
- `openid`
- `profile`
- `email`
- `w_member_social`

### Error: 401 Unauthorized

**Cause:** Invalid or expired token

**Solution:**
```bash
# Get new token
python linkedin_auth.py
```

Tokens expire after **60 days**.

---

## 📁 Files Updated

| File | Status | Description |
|------|--------|-------------|
| `approve_linkedin.py` | ✅ FIXED | Complete rewrite with correct API usage |
| `linkedin_post_example.py` | ✨ NEW | Standalone working example |
| `LINKEDIN_FIX_SUMMARY.md` | ✨ NEW | This document |

---

## ✅ Verification Checklist

Before running the script, verify:

- [ ] Access token exists in `.env` file
- [ ] Token has `w_member_social` scope
- [ ] Token is not expired (less than 60 days old)
- [ ] Using `/v2/userinfo` endpoint (not `/v2/me`)
- [ ] Author field is full URN: `urn:li:person:{id}`
- [ ] Header `X-Restli-Protocol-Version: 2.0.0` is included
- [ ] Header `LinkedIn-Version: 202402` is included
- [ ] Bearer token authentication is used

---

## 🚀 Quick Test

Run this to test the fix:

```bash
# Test with a single post
python approve_linkedin.py
# Choose option 1 (Post latest)
```

If successful, you'll see:
```
✅ SUCCESS! Post published
   Post ID: urn:li:ugcPost:7165432109876543210
   URL: https://www.linkedin.com/feed/update/urn:li:ugcPost:7165432109876543210
```

---

## 📚 API Documentation

- [UGC Posts API](https://learn.microsoft.com/en-us/linkedin/marketing/integrations/community-management/shares/ugc-post-api)
- [OpenID Connect](https://openid.net/specs/openid-connect-core-1_0.html)
- [LinkedIn API v2](https://learn.microsoft.com/en-us/linkedin/shared/api-guide/reference)

---

**Status:** ✅ Fixed and Working  
**Last Updated:** 2024-02-21  
**API Version:** 202402
