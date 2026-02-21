"""
Test LinkedIn API Connection (OIDC Compliant)
Verify your LinkedIn credentials and posting capability
"""

import sys
import codecs

# Fix Unicode encoding for Windows
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

def main():
    print("="*60)
    print("LINKEDIN API CONNECTION TEST (OIDC Compliant)")
    print("="*60)
    
    # Import modern API
    from linkedin_api_modern import LinkedInAPI
    
    try:
        api = LinkedInAPI()
    except ValueError as e:
        print(f"\n[FAIL] {e}")
        return
    
    # Check credentials
    print("\n1. Checking credentials...")
    if not api.client_id:
        print("   [FAIL] LINKEDIN_CLIENT_ID not found in .env")
        return
    else:
        print(f"   [OK] Client ID: {api.client_id[:10]}...")
    
    if not api.client_secret:
        print("   [FAIL] LINKEDIN_CLIENT_SECRET not found in .env")
        return
    else:
        print(f"   [OK] Client Secret: {'*' * 10}")
    
    if not api.redirect_uri:
        print("   [FAIL] LINKEDIN_REDIRECT_URI not found in .env")
        return
    else:
        print(f"   [OK] Redirect URI: {api.redirect_uri}")
    
    if not api.access_token:
        print("   [WARNING] No access token found. You need to authorize first.")
        print("\n   Run: python linkedin_auth.py")
        return
    else:
        print(f"   [OK] Access Token: {api.access_token[:20]}...")
    
    # Test token validation
    print("\n2. Testing token validity...")
    if not api.validate_token():
        print(f"   [FAIL] Token is invalid or expired")
        print("\n   Run: python linkedin_auth.py to get a new token")
        return
    else:
        print(f"   [OK] Token is valid!")
    
    # Test getting user info (OIDC endpoint)
    print("\n3. Testing /v2/userinfo endpoint...")
    user_info = api.get_user_info()
    
    if user_info:
        print(f"   [OK] Connected to LinkedIn!")
        print(f"   Name: {user_info.get('name', 'N/A')}")
        print(f"   Email: {user_info.get('email', 'N/A')}")
        print(f"   URN: {user_info.get('sub', 'N/A')}")
        print(f"   Profile: {user_info.get('profile', 'N/A')}")
    else:
        print(f"   [FAIL] Could not retrieve user info")
        print("\n   Possible issues:")
        print("   - Missing 'openid' or 'profile' scope")
        print("   - Token doesn't have OIDC permissions")
        return
    
    # Test posting
    print("\n4. Test posting (optional)...")
    test_post = input("   Post a test message to LinkedIn? (y/n): ").strip().lower()
    
    if test_post == 'y':
        test_content = "Testing my LinkedIn API integration! This post was created using the OIDC-compliant API with Python. #LinkedIn #API #Python #Automation"
        print(f"\n   Posting: {test_content}")
        
        result = api.create_text_post(test_content)
        
        if result:
            post_id = result.get('id')
            print(f"   [OK] Test post successful!")
            print(f"   Post ID: {post_id}")
            print(f"   Post URL: https://www.linkedin.com/feed/update/{post_id}")
            print("\n   Check your LinkedIn profile to verify the post.")
        else:
            print("   [FAIL] Test post failed.")
            print("\n   Possible issues:")
            print("   - Access token expired")
            print("   - Missing 'w_member_social' scope")
            print("   - API rate limit reached")
            print("   - Insufficient permissions")
            print("\n   Try re-authorizing: python linkedin_auth.py")


if __name__ == "__main__":
    main()
