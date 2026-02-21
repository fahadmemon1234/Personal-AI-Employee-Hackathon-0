"""
LinkedIn Post Example - Working Code
=====================================
This is a COMPLETE, WORKING example of posting to LinkedIn using the ugcPosts API.

KEY FIXES (compared to broken implementations):
1. ✅ Author field: "urn:li:person:{id}" (NOT just the ID)
2. ✅ Header: X-Restli-Protocol-Version: 2.0.0 (REQUIRED)
3. ✅ Endpoint: /v2/userinfo (NOT deprecated /v2/me)
4. ✅ Header: Authorization: Bearer {token}
5. ✅ Correct payload structure for ugcPosts

Run this script to post a test message to your LinkedIn profile.
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def main():
    """Complete working example - post to LinkedIn"""
    
    # ============================================================
    # CONFIGURATION
    # ============================================================
    
    # Get access token from .env
    ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")
    
    if not ACCESS_TOKEN:
        print("❌ ERROR: No access token found")
        print("\nFix:")
        print("1. Run 'python linkedin_auth.py' to authorize")
        print("2. Token will be saved to .env file")
        return
    
    # API endpoints
    BASE_URL = "https://api.linkedin.com/v2"
    
    # ============================================================
    # STEP 1: GET USER INFO (to get person URN)
    # ============================================================
    # FIX: Use /v2/userinfo (OIDC compliant)
    # NOT /v2/me (deprecated, returns 403)
    # ============================================================
    
    print("📋 Getting user info...")
    
    userinfo_url = f"{BASE_URL}/userinfo"
    userinfo_headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(userinfo_url, headers=userinfo_headers)
    
    if response.status_code != 200:
        print(f"❌ Failed to get user info: HTTP {response.status_code}")
        print(f"   Response: {response.text}")
        print("\nPossible causes:")
        print("  - Token expired or invalid")
        print("  - Missing 'openid' or 'profile' scope")
        print("\nFix: Run 'python linkedin_auth.py' to re-authorize")
        return
    
    user_info = response.json()
    person_urn = user_info.get("sub")  # "urn:li:person:..."
    
    if not person_urn:
        print("❌ Could not extract person URN from response")
        print(f"   Response: {user_info}")
        return
    
    print(f"✅ Logged in as: {user_info.get('name', 'Unknown')}")
    print(f"   Person URN: {person_urn}")
    
    # ============================================================
    # STEP 2: CREATE THE POST
    # ============================================================
    # FIX: Author must be full URN format
    # WRONG:  "MqvEfm3LKp"
    # RIGHT:  "urn:li:person:MqvEfm3LKp"
    # ============================================================
    
    print("\n📝 Creating post...")
    
    # Post content
    post_text = "This is a test post from my Python automation script! 🚀\n\n#LinkedIn #API #Python #Automation"
    
    # API endpoint
    post_url = f"{BASE_URL}/ugcPosts"
    
    # ============================================================
    # PAYLOAD STRUCTURE
    # ============================================================
    
    payload = {
        "author": person_urn,  # ✅ FULL URN: "urn:li:person:..."
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": post_text
                },
                "shareMediaCategory": "NONE"  # Text-only post
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }
    
    # ============================================================
    # HEADERS - CRITICAL
    # ============================================================
    # FIX: X-Restli-Protocol-Version: 2.0.0 is REQUIRED
    # ============================================================
    
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",  # ✅ Bearer token
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0",  # ✅ REQUIRED
        "LinkedIn-Version": "202402"  # ✅ API version
    }
    
    # ============================================================
    # MAKE API REQUEST
    # ============================================================
    
    response = requests.post(post_url, json=payload, headers=headers)
    
    # ============================================================
    # HANDLE RESPONSE
    # ============================================================
    
    if response.status_code != 201:
        print(f"\n❌ FAILED: HTTP {response.status_code}")
        print(f"   Response: {response.text}")
        
        # Handle common errors
        if response.status_code == 403:
            try:
                error_data = response.json()
                error_msg = str(error_data)
                
                if "ACCESS_DENIED" in error_msg:
                    print("\n   ⚠️  ACCESS_DENIED - Check permissions:")
                    print("   - Token must have 'w_member_social' scope")
                    print("   - Run 'python linkedin_auth.py' to re-authorize")
                
                if "Data Processing Exception" in error_msg:
                    print("\n   ⚠️  Author field format error!")
                    print(f"   Current: {person_urn}")
                    print("   Expected format: urn:li:person:{id}")
                
            except:
                pass
        
        elif response.status_code == 401:
            print("\n   ⚠️  Token expired or invalid")
            print("   Run 'python linkedin_auth.py' to get new token")
        
        return
    
    # Success!
    result = response.json()
    post_id = result.get("id")
    
    if not post_id:
        print("❌ No post ID in response")
        print(f"   Response: {result}")
        return
    
    # ============================================================
    # SUCCESS
    # ============================================================
    
    post_url = f"https://www.linkedin.com/feed/update/{post_id}"
    
    print(f"\n✅ SUCCESS!")
    print(f"   Post ID: {post_id}")
    print(f"   URL: {post_url}")
    print(f"\n   View your post: {post_url}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Cancelled")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
