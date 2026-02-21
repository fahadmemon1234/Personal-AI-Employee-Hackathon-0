"""
LinkedIn Authorization Script (OIDC Compliant - 2024+)
=======================================================
Uses modern OAuth 2.0 / OIDC flow with correct scopes:
- openid: OIDC basic profile access
- profile: User profile information  
- email: User email address
- w_member_social: Post to LinkedIn as member

This replaces the deprecated /v2/me endpoint with /v2/userinfo
"""

import os
import sys
import webbrowser
from dotenv import load_dotenv

load_dotenv()

def main():
    # Import the modern API
    from linkedin_api_modern import LinkedInAPI
    
    print("="*60)
    print("LINKEDIN AUTHORIZATION (OIDC Compliant)")
    print("="*60)
    
    try:
        api = LinkedInAPI()
    except ValueError as e:
        print(f"ERROR: {e}")
        print("\nPlease configure in .env:")
        print("  - LINKEDIN_CLIENT_ID")
        print("  - LINKEDIN_CLIENT_SECRET")
        print("  - LINKEDIN_REDIRECT_URI")
        sys.exit(1)
    
    print("\nStep 1: Authorize the application")
    print("-" * 60)
    
    # Generate authorization URL with correct scopes
    auth_url = api.get_authorization_url()
    
    print(f"\nOpening authorization URL in your browser...")
    print(f"\nRequired Scopes:")
    print(f"  - openid (OIDC profile access)")
    print(f"  - profile (user information)")
    print(f"  - email (email address)")
    print(f"  - w_member_social (posting permission)")
    
    print(f"\nIf the browser doesn't open, visit:")
    print(f"{auth_url}")
    
    # Try to open browser
    try:
        webbrowser.open(auth_url)
    except Exception as e:
        print(f"Could not open browser: {e}")
    
    print("\n" + "-" * 60)
    print("\nStep 2: Get the authorization code")
    print("-" * 60)
    print("After authorizing, LinkedIn will redirect you to a URL.")
    print("Copy the 'code' parameter from that URL.")
    print("\nExample: http://localhost:8080/callback?code=ABC123...")
    
    auth_code = input("\nPaste the authorization code here: ").strip()
    
    if not auth_code:
        print("No code provided. Exiting.")
        sys.exit(1)
    
    print("\n" + "-" * 60)
    print("\nStep 3: Exchange code for access token")
    print("-" * 60)
    
    try:
        # Exchange code for token
        token_data = api.exchange_code_for_token(auth_code)
        access_token = token_data.get('access_token')
        expires_in = token_data.get('expires_in', 0)
        
        if access_token:
            print("\n[SUCCESS] Access token obtained!")
            print(f"\nAccess Token: {access_token}")
            print(f"Expires in: {expires_in} seconds ({expires_in // 3600} hours)")
            
            # Save token to .env
            print("\n" + "-" * 60)
            save = input("Save this token to .env file? (y/n): ").strip().lower()
            
            if save == 'y':
                api.save_token_to_env(access_token)
            
            # Test the token using OIDC userinfo endpoint
            print("\n" + "-" * 60)
            print("Testing access token with /v2/userinfo...")
            
            user_info = api.get_user_info()
            
            if user_info:
                print(f"[SUCCESS] Token is valid!")
                print(f"\nUser Information:")
                print(f"  Name: {user_info.get('name', 'N/A')}")
                print(f"  Email: {user_info.get('email', 'N/A')}")
                print(f"  Profile: {user_info.get('profile', 'N/A')}")
                print(f"  URN: {user_info.get('sub', 'N/A')}")
                print(f"\n  Note: Using OIDC /v2/userinfo (not deprecated /v2/me)")
            else:
                print(f"[WARNING] Could not retrieve user info")
                print("\n  This may indicate:")
                print("  - Missing 'openid' or 'profile' scope")
                print("  - Token doesn't have sufficient permissions")
        else:
            print(f"[ERROR] No access token in response: {token_data}")
    
    except Exception as e:
        print(f"[ERROR] {e}")
        print("\nTroubleshooting:")
        print("1. Make sure your LinkedIn app has these redirect URLs:")
        print(f"   {api.redirect_uri}")
        print("2. Verify your app has 'Sign In with LinkedIn using OpenID Connect' enabled")
        print("3. Check that scopes include: openid, profile, email, w_member_social")


if __name__ == "__main__":
    main()
