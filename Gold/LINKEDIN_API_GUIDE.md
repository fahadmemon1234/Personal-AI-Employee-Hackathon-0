# LinkedIn API Integration - Complete Guide (2024+ OIDC Compliant)

## 🔴 Problem: Why `/v2/me` Returns 403 ACCESS_DENIED

### Deprecated vs Modern Endpoints

| Endpoint | Status | Reason |
|----------|--------|--------|
| `https://api.linkedin.com/v2/me` | ❌ **DEPRECATED** | Legacy API (pre-2020), returns 403 |
| `https://api.linkedin.com/v2/userinfo` | ✅ **CURRENT** | OIDC compliant (OpenID Connect) |

### Why `/v2/me` Fails

```json
{
  "status": 403,
  "message": "ACCESS_DENIED",
  "details": "Not enough permissions to access: me.GET.NO_VERSION"
}
```

**Reason:** LinkedIn migrated to OIDC (OpenID Connect) standard. The old `/v2/me` endpoint:
- Used LinkedIn's proprietary authentication
- Returned non-standard user data format
- Is no longer maintained

**Solution:** Use `/v2/userinfo` which:
- Follows OIDC standard (RFC 6749, OpenID Connect Core 1.0)
- Returns standardized claims (name, email, sub, profile)
- Works with `openid`, `profile`, `email` scopes
- Is actively maintained

---

## ✅ Complete Working Implementation

### 1. OAuth Authorization URL

**Required Scopes:**
- `openid` - OIDC basic profile access
- `profile` - User profile information
- `email` - User email address
- `w_member_social` - Permission to post on behalf of user

```python
def get_authorization_url():
    scopes = ["openid", "profile", "email", "w_member_social"]
    
    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": " ".join(scopes),
        "state": STATE_TOKEN  # CSRF protection
    }
    
    query = "&".join(f"{k}={v}" for k, v in params.items())
    return f"https://www.linkedin.com/oauth/v2/authorization?{query}"
```

**Example URL:**
```
https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id=77o2e734lvyjp0&redirect_uri=http://localhost:8080/callback&scope=openid%20profile%20email%20w_member_social&state=20240221120000
```

---

### 2. Access Token Exchange (Python requests)

```python
import requests

def exchange_code_for_token(authorization_code):
    token_url = "https://www.linkedin.com/oauth/v2/accessToken"
    
    payload = {
        "grant_type": "authorization_code",
        "code": authorization_code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    response = requests.post(token_url, data=payload, headers=headers)
    response.raise_for_status()
    
    token_data = response.json()
    # {
    #     "access_token": "AQV8Zm9vYmFy...",
    #     "expires_in": 3600,
    #     "scope": "openid profile email w_member_social"
    # }
    
    return token_data
```

---

### 3. Get User Identity (OIDC Compliant)

```python
def get_user_info(access_token):
    """
    Get user info using OIDC /v2/userinfo endpoint.
    NOT the deprecated /v2/me endpoint!
    """
    url = "https://api.linkedin.com/v2/userinfo"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    user_info = response.json()
    # {
    #     "sub": "urn:li:person:ACoAABkD3jQBqKZ9X8vN5Q",
    #     "name": "Fahad Memon",
    #     "given_name": "Fahad",
    #     "family_name": "Memon",
    #     "email": "fahad@example.com",
    #     "profile": "https://www.linkedin.com/in/fahadmemon",
    #     "locale": "en_US",
    #     "picture": "https://media.licdn.com/dms/image/..."
    # }
    
    return user_info
```

---

### 4. Person URN Format

The `sub` field from `/v2/userinfo` **already contains the full URN**:

```python
user_info = get_user_info(access_token)
person_urn = user_info["sub"]  # "urn:li:person:ACoAABkD3jQBqKZ9X8vN5Q"
```

**Format:** `urn:li:person:{id}`

**Example:**
- Full URN: `urn:li:person:ACoAABkD3jQBqKZ9X8vN5Q`
- Person ID: `ACoAABkD3jQBqKZ9X8vN5Q`

---

### 5. Create Text Post (ugcPosts API)

```python
def create_text_post(access_token, person_urn, text, visibility="PUBLIC"):
    """
    Create a text post using ugCPosts endpoint.
    Documentation: https://learn.microsoft.com/en-us/linkedin/marketing/integrations/community-management/shares/ugc-post-api
    """
    url = "https://api.linkedin.com/v2/ugcPosts"
    
    payload = {
        "author": person_urn,  # "urn:li:person:ACoAABkD3jQBqKZ9X8vN5Q"
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": text  # Max 3000 characters
                },
                "shareMediaCategory": "NONE"  # Text-only post
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": visibility  # "PUBLIC" or "CONNECTIONS"
        }
    }
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0"
    }
    
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    
    result = response.json()
    # {
    #     "id": "urn:li:ugcPost:7165432109876543210"
    # }
    
    return result
```

**Post URL:** `https://www.linkedin.com/feed/update/urn:li:ugcPost:7165432109876543210`

---

## 📝 Complete End-to-End Example

```python
"""
Complete LinkedIn API Integration - End-to-End Example
"""

import requests
import webbrowser
from dotenv import load_dotenv
import os

load_dotenv()

# Configuration
CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID")
CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET")
REDIRECT_URI = os.getenv("LINKEDIN_REDIRECT_URI")

# Step 1: Generate authorization URL
scopes = ["openid", "profile", "email", "w_member_social"]
auth_url = (
    "https://www.linkedin.com/oauth/v2/authorization"
    f"?response_type=code"
    f"&client_id={CLIENT_ID}"
    f"&redirect_uri={REDIRECT_URI}"
    f"&scope={' '.join(scopes)}"
)

print("Open this URL in your browser:")
print(auth_url)
webbrowser.open(auth_url)

# Step 2: Get authorization code from user
auth_code = input("Enter authorization code: ").strip()

# Step 3: Exchange code for access token
token_url = "https://www.linkedin.com/oauth/v2/accessToken"
token_payload = {
    "grant_type": "authorization_code",
    "code": auth_code,
    "redirect_uri": REDIRECT_URI,
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET
}

token_response = requests.post(token_url, data=token_payload)
token_response.raise_for_status()
token_data = token_response.json()
access_token = token_data["access_token"]

print(f"Access Token: {access_token[:30]}...")

# Step 4: Get user info (OIDC endpoint)
userinfo_url = "https://api.linkedin.com/v2/userinfo"
userinfo_headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

userinfo_response = requests.get(userinfo_url, headers=userinfo_headers)
userinfo_response.raise_for_status()
user_info = userinfo_response.json()

person_urn = user_info["sub"]  # "urn:li:person:..."
print(f"Logged in as: {user_info['name']}")
print(f"Person URN: {person_urn}")

# Step 5: Create a post
post_url = "https://api.linkedin.com/v2/ugcPosts"
post_payload = {
    "author": person_urn,
    "lifecycleState": "PUBLISHED",
    "specificContent": {
        "com.linkedin.ugc.ShareContent": {
            "shareCommentary": {
                "text": "Hello LinkedIn! This post was created using the OIDC-compliant API. 🚀 #LinkedIn #API #Python"
            },
            "shareMediaCategory": "NONE"
        }
    },
    "visibility": {
        "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
    }
}

post_headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json",
    "X-Restli-Protocol-Version": "2.0.0"
}

post_response = requests.post(post_url, json=post_payload, headers=post_headers)
post_response.raise_for_status()
post_result = post_response.json()

post_id = post_result["id"]
print(f"Post created successfully!")
print(f"Post ID: {post_id}")
print(f"Post URL: https://www.linkedin.com/feed/update/{post_id}")
```

---

## 🔧 LinkedIn App Configuration

### Required Settings

1. **Go to:** [LinkedIn Developer Portal](https://www.linkedin.com/developers/apps)
2. **Select your app** (or create new one)
3. **Auth tab** → Configure:

### Authorized Redirect URLs
```
http://localhost:8080/callback
```

### Sign In with LinkedIn using OpenID Connect
- ✅ **Enable** "Sign In with LinkedIn using OpenID Connect"
- ✅ **Scopes:**
  - ✅ `openid`
  - ✅ `profile`
  - ✅ `email`
  - ✅ `w_member_social`

### App Permissions
Make sure your app has these permissions approved:
- **Share on LinkedIn** (`w_member_social`)
- **Sign In with LinkedIn** (`openid`, `profile`, `email`)

---

## 📚 API Reference

### Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/oauth/v2/authorization` | GET | OAuth authorization URL |
| `/oauth/v2/accessToken` | POST | Exchange code for token |
| `/v2/userinfo` | GET | Get user profile (OIDC) |
| `/v2/ugcPosts` | POST | Create posts |

### Scopes

| Scope | Purpose |
|-------|---------|
| `openid` | OIDC authentication |
| `profile` | Access user profile |
| `email` | Access user email |
| `w_member_social` | Post to LinkedIn |

### Response Formats

**User Info (`/v2/userinfo`):**
```json
{
  "sub": "urn:li:person:ACoAABkD3jQBqKZ9X8vN5Q",
  "name": "Fahad Memon",
  "given_name": "Fahad",
  "family_name": "Memon",
  "email": "fahad@example.com",
  "profile": "https://www.linkedin.com/in/fahadmemon",
  "locale": "en_US",
  "picture": "https://media.licdn.com/dms/image/..."
}
```

**Create Post (`/v2/ugcPosts`):**
```json
{
  "id": "urn:li:ugcPost:7165432109876543210"
}
```

---

## 🐛 Troubleshooting

### 403 ACCESS_DENIED on /v2/userinfo

**Cause:** Missing OIDC scopes or deprecated endpoint

**Solution:**
1. Re-authorize with correct scopes: `openid profile email w_member_social`
2. Use `/v2/userinfo` instead of `/v2/me`
3. Enable "Sign In with LinkedIn using OpenID Connect" in app settings

### Invalid redirect_uri

**Solution:**
1. Go to LinkedIn Developer Portal
2. Auth tab → Authorized Redirect URLs
3. Add: `http://localhost:8080/callback`

### Token expires quickly

**Note:** Access tokens expire after **60 days** (2 months)

**Solution:** Implement token refresh or re-authorize periodically

### 401 Unauthorized

**Cause:** Invalid or expired token

**Solution:**
```python
if response.status_code == 401:
    print("Token expired. Re-authorize.")
    # Run authorization flow again
```

---

## 📁 Files in This Project

| File | Purpose |
|------|---------|
| `linkedin_api_modern.py` | Modern OIDC-compliant API client |
| `linkedin_auth.py` | Authorization script |
| `test_linkedin_api.py` | Test connection and posting |
| `linkedin_poster.py` | Updated to use modern API |
| `post_latest_linkedin.py` | Quick post script |
| `approve_linkedin.py` | Interactive approver |

---

## 🚀 Quick Start

```bash
# 1. Authorize (get token with correct scopes)
python linkedin_auth.py

# 2. Test connection
python test_linkedin_api.py

# 3. Post pending content
python post_latest_linkedin.py
```

---

## 📖 Official Documentation

- [LinkedIn API v2](https://learn.microsoft.com/en-us/linkedin/shared/api-guide/reference)
- [OpenID Connect Core](https://openid.net/specs/openid-connect-core-1_0.html)
- [UGC Posts API](https://learn.microsoft.com/en-us/linkedin/marketing/integrations/community-management/shares/ugc-post-api)
- [OAuth 2.0 RFC 6749](https://tools.ietf.org/html/rfc6749)
