# LinkedIn API - Quick Reference Card

## 🔑 Key Changes (Legacy → Modern)

| Old (❌ Deprecated) | New (✅ Current) |
|---------------------|------------------|
| `/v2/me` | `/v2/userinfo` |
| `w_member_social` only | `openid profile email w_member_social` |
| Legacy auth | OIDC (OpenID Connect) |
| `shares` endpoint | `ugcPosts` endpoint |
| Custom user format | Standard OIDC claims |

---

## 📝 OAuth URL (Copy-Paste)

```
https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id=YOUR_CLIENT_ID&redirect_uri=YOUR_REDIRECT_URI&scope=openid%20profile%20email%20w_member_social
```

**Required Scopes:** `openid profile email w_member_social`

---

## 🔁 Token Exchange

```python
import requests

token_url = "https://www.linkedin.com/oauth/v2/accessToken"
payload = {
    "grant_type": "authorization_code",
    "code": AUTH_CODE,
    "redirect_uri": "http://localhost:8080/callback",
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET
}

response = requests.post(token_url, data=payload)
access_token = response.json()["access_token"]
```

---

## 👤 Get User Info (OIDC)

```python
# ✅ CORRECT - Use /v2/userinfo
url = "https://api.linkedin.com/v2/userinfo"
headers = {"Authorization": f"Bearer {access_token}"}
response = requests.get(url, headers=headers)
user_info = response.json()
person_urn = user_info["sub"]  # "urn:li:person:..."
```

```python
# ❌ WRONG - Don't use /v2/me (returns 403)
url = "https://api.linkedin.com/v2/me"  # DON'T USE THIS!
```

---

## 📝 Create Post

```python
url = "https://api.linkedin.com/v2/ugcPosts"
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json",
    "X-Restli-Protocol-Version": "2.0.0"
}

payload = {
    "author": person_urn,  # "urn:li:person:..."
    "lifecycleState": "PUBLISHED",
    "specificContent": {
        "com.linkedin.ugc.ShareContent": {
            "shareCommentary": {"text": "Your post content here"},
            "shareMediaCategory": "NONE"
        }
    },
    "visibility": {
        "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
    }
}

response = requests.post(url, json=payload, headers=headers)
post_id = response.json()["id"]
```

---

## 🏃 Run Commands

```bash
# Authorize (get token)
python linkedin_auth.py

# Test connection
python test_linkedin_api.py

# Post latest pending content
python post_latest_linkedin.py

# Interactive approval
python approve_linkedin.py
```

---

## ⚠️ Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `403 ACCESS_DENIED` on `/v2/me` | Deprecated endpoint | Use `/v2/userinfo` |
| `Not enough permissions` | Missing scopes | Re-authorize with `openid profile email` |
| `Invalid redirect_uri` | URL not configured | Add to LinkedIn app settings |
| `401 Unauthorized` | Expired token | Re-authorize (tokens expire in 60 days) |

---

## 🔗 Person URN Format

```
urn:li:person:ACoAABkD3jQBqKZ9X8vN5Q
│       │     │
│       │     └── Person ID (unique)
│       └── Person type
└── URN namespace
```

**Get from:** `user_info["sub"]` field

---

## 📋 Checklist

Before posting to LinkedIn:

- [ ] LinkedIn app created at [developers.linkedin.com](https://www.linkedin.com/developers/apps)
- [ ] "Sign In with LinkedIn using OpenID Connect" enabled
- [ ] Redirect URI configured: `http://localhost:8080/callback`
- [ ] Scopes authorized: `openid`, `profile`, `email`, `w_member_social`
- [ ] Access token saved in `.env` file
- [ ] Using `/v2/userinfo` (not `/v2/me`)
- [ ] Using `ugcPosts` endpoint for posting

---

## 📚 Documentation

- [LinkedIn API v2](https://learn.microsoft.com/en-us/linkedin/shared/api-guide/reference)
- [UGC Posts API](https://learn.microsoft.com/en-us/linkedin/marketing/integrations/community-management/shares/ugc-post-api)
- [OpenID Connect](https://openid.net/specs/openid-connect-core-1_0.html)

---

**Last Updated:** 2024+ (OIDC Compliant)  
**Status:** ✅ Production Ready
