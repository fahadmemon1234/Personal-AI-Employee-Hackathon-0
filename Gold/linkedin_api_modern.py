"""
Modern LinkedIn API Integration (2024+ OIDC Compliant)
=======================================================
Uses LinkedIn's latest REST API with proper OAuth 2.0 / OIDC flow.

Key Changes from Legacy API:
- /v2/me is DEPRECATED (returns 403 ACCESS_DENIED)
- Use /v2/userinfo instead (OIDC compliant)
- Use ugCPosts endpoint for creating posts
- Required scopes: openid, profile, email, w_member_social
"""

import os
import json
import datetime
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class LinkedInAPI:
    """Modern LinkedIn API Client (OIDC Compliant)"""
    
    def __init__(self):
        # API Configuration
        self.base_url = "https://api.linkedin.com/v2"
        self.auth_url = "https://www.linkedin.com/oauth/v2"
        
        # Credentials from .env
        self.client_id = os.getenv("LINKEDIN_CLIENT_ID")
        self.client_secret = os.getenv("LINKEDIN_CLIENT_SECRET")
        self.redirect_uri = os.getenv("LINKEDIN_REDIRECT_URI")
        self.access_token = os.getenv("LINKEDIN_ACCESS_TOKEN")
        
        # Cached user data
        self.user_info = None
        self.person_urn = None
        
        # Validate credentials
        if not all([self.client_id, self.client_secret, self.redirect_uri]):
            raise ValueError("Missing LinkedIn credentials in .env file")
    
    # ============================================================
    # AUTHENTICATION (OAuth 2.0 / OIDC)
    # ============================================================
    
    def get_authorization_url(self, state=None):
        """
        Generate OAuth 2.0 authorization URL.
        
        Required Scopes:
        - openid: OIDC basic profile access
        - profile: User profile information
        - email: User email address
        - w_member_social: Post to LinkedIn as member
        
        Returns:
            str: Authorization URL to open in browser
        """
        if state is None:
            state = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        
        scopes = ["openid", "profile", "email", "w_member_social"]
        
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": " ".join(scopes),
            "state": state
        }
        
        # Build query string
        query = "&".join(f"{k}={v}" for k, v in params.items())
        auth_url = f"{self.auth_url}/authorization?{query}"
        
        return auth_url
    
    def exchange_code_for_token(self, authorization_code):
        """
        Exchange authorization code for access token.
        
        Args:
            authorization_code: Code from OAuth callback
            
        Returns:
            dict: Token response with access_token, expires_in, etc.
        """
        token_url = f"{self.auth_url}/accessToken"
        
        payload = {
            "grant_type": "authorization_code",
            "code": authorization_code,
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        response = requests.post(token_url, data=payload, headers=headers)
        response.raise_for_status()
        
        token_data = response.json()
        
        # Save token for future use
        self.access_token = token_data.get("access_token")
        
        return token_data
    
    def validate_token(self):
        """
        Validate current access token by calling userinfo endpoint.
        
        Returns:
            bool: True if token is valid, False otherwise
        """
        if not self.access_token:
            return False
        
        try:
            user_info = self.get_user_info()
            return user_info is not None
        except Exception:
            return False
    
    # ============================================================
    # USER INFO (OIDC Compliant)
    # ============================================================
    
    def get_user_info(self):
        """
        Get current user's profile information using OIDC /v2/userinfo endpoint.
        
        Why /v2/userinfo instead of /v2/me?
        - /v2/me is DEPRECATED and returns 403 ACCESS_DENIED
        - /v2/userinfo is OIDC compliant (OpenID Connect)
        - Works with openid, profile, email scopes
        - Returns standardized user information
        
        Returns:
            dict: User profile data with id, name, email, etc.
                  None if request fails
        """
        if self.user_info:
            return self.user_info
        
        if not self.access_token:
            print("No access token available")
            return None
        
        # OIDC-compliant userinfo endpoint
        url = f"{self.base_url}/userinfo"
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            self.user_info = response.json()

            # Extract person URN from sub field (format: urn:li:person:XXXXX)
            sub_value = self.user_info.get("sub")
            
            # Ensure the URN is in full format: urn:li:person:{id}
            # The sub field may return just the ID or the full URN
            if sub_value and not sub_value.startswith("urn:li:person:"):
                self.person_urn = f"urn:li:person:{sub_value}"
            else:
                self.person_urn = sub_value

            return self.user_info
            
        except requests.exceptions.HTTPError as e:
            print(f"HTTP Error getting user info: {e}")
            print(f"Response: {e.response.text}")
            return None
        except Exception as e:
            print(f"Error getting user info: {e}")
            return None
    
    def get_person_urn(self):
        """
        Get the person's URN (LinkedIn user ID).
        
        Format: urn:li:person:{id}
        Example: urn:li:person:ACoAABkD3jQBqKZ9X8vN5Q
        
        Returns:
            str: Person URN or None
        """
        if self.person_urn:
            return self.person_urn
        
        user_info = self.get_user_info()
        if user_info:
            return self.person_urn
        
        return None
    
    # ============================================================
    # LINKEDIN POSTING (UGC Posts API)
    # ============================================================
    
    def create_text_post(self, text, visibility="PUBLIC"):
        """
        Create a text post on LinkedIn using ugCPosts endpoint.
        
        Args:
            text: Post content (max 3000 characters)
            visibility: "PUBLIC" or "CONNECTIONS"
            
        Returns:
            dict: Post creation response with id, or None if failed
            
        Endpoint: POST /ugcPosts
        Documentation: https://learn.microsoft.com/en-us/linkedin/marketing/integrations/community-management/shares/ugc-post-api
        """
        if not self.access_token:
            print("No access token available")
            return None
        
        # Get person URN
        person_urn = self.get_person_urn()
        if not person_urn:
            print("Could not get person URN")
            return None
        
        # Validate text length
        if len(text) > 3000:
            text = text[:2997] + "..."
            print("Warning: Text truncated to 3000 characters")
        
        # Construct UGC Post payload
        # Documentation: https://learn.microsoft.com/en-us/linkedin/marketing/integrations/community-management/shares/ugc-posts-api?view=li-lms-2024-02&tabs=http#sample-request
        payload = {
            "author": person_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": text
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": visibility
            }
        }
        
        # API endpoint
        url = f"{self.base_url}/ugcPosts"
        
        # Required headers
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            post_id = result.get("id")
            
            print(f"Post created successfully!")
            print(f"Post ID: {post_id}")
            print(f"Post URL: https://www.linkedin.com/feed/update/{post_id}")
            
            return result
            
        except requests.exceptions.HTTPError as e:
            print(f"HTTP Error creating post: {e}")
            print(f"Status Code: {e.response.status_code}")
            print(f"Response: {e.response.text}")
            return None
        except Exception as e:
            print(f"Error creating post: {e}")
            return None
    
    def create_post_with_image(self, text, image_url, title="Image", visibility="PUBLIC"):
        """
        Create a post with an image on LinkedIn.
        
        Args:
            text: Post commentary text
            image_url: URL of the image to share
            title: Title for the image
            visibility: "PUBLIC" or "CONNECTIONS"
            
        Returns:
            dict: Post creation response or None
        """
        if not self.access_token:
            print("No access token available")
            return None
        
        person_urn = self.get_person_urn()
        if not person_urn:
            return None
        
        payload = {
            "author": person_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": text
                    },
                    "shareMediaCategory": "IMAGE",
                    "media": [
                        {
                            "status": "READY",
                            "description": {
                                "text": title
                            },
                            "originalUrl": image_url,
                            "title": {
                                "text": title
                            }
                        }
                    ]
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": visibility
            }
        }
        
        url = f"{self.base_url}/ugcPosts"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error creating post with image: {e}")
            return None
    
    # ============================================================
    # TOKEN MANAGEMENT
    # ============================================================
    
    def save_token_to_env(self, token):
        """Save access token to .env file"""
        import re
        
        env_file = ".env"
        env_content = ""
        
        if os.path.exists(env_file):
            with open(env_file, 'r', encoding='utf-8') as f:
                env_content = f.read()
        
        if "LINKEDIN_ACCESS_TOKEN=" in env_content:
            env_content = re.sub(
                r'LINKEDIN_ACCESS_TOKEN=.*',
                f'LINKEDIN_ACCESS_TOKEN={token}',
                env_content
            )
        else:
            env_content += f"\nLINKEDIN_ACCESS_TOKEN={token}\n"
        
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        self.access_token = token
        print("Token saved to .env file")


# ============================================================
# USAGE EXAMPLES
# ============================================================

def example_full_workflow():
    """Complete example: Auth -> Get User Info -> Post"""
    
    print("="*60)
    print("LINKEDIN API - FULL WORKFLOW EXAMPLE")
    print("="*60)
    
    # Initialize API client
    api = LinkedInAPI()
    
    # Step 1: Get authorization URL
    print("\n1. Authorization URL:")
    auth_url = api.get_authorization_url()
    print(f"   {auth_url}")
    print("\n   Open this URL in your browser and authorize the app.")
    
    # Step 2: Exchange code for token (after user authorizes)
    auth_code = input("\n2. Enter authorization code: ").strip()
    if not auth_code:
        print("No code provided")
        return
    
    token_data = api.exchange_code_for_token(auth_code)
    print(f"\n3. Access Token: {token_data.get('access_token', '')[:20]}...")
    print(f"   Expires In: {token_data.get('expires_in', 0)} seconds")
    
    # Save token
    api.save_token_to_env(token_data["access_token"])
    
    # Step 3: Get user info
    print("\n4. Getting user info...")
    user_info = api.get_user_info()
    if user_info:
        print(f"   Name: {user_info.get('name', 'N/A')}")
        print(f"   Email: {user_info.get('email', 'N/A')}")
        print(f"   URN: {user_info.get('sub', 'N/A')}")
    
    # Step 4: Create a post
    print("\n5. Creating a post...")
    post_text = "Hello LinkedIn! This is my first post using the new OIDC-compliant API. #LinkedIn #API #Python"
    result = api.create_text_post(post_text)
    
    if result:
        print(f"\n   ✓ SUCCESS! Post created: {result.get('id')}")
    else:
        print("\n   ✗ FAILED to create post")


def example_quick_post():
    """Quick post example (assuming token already exists in .env)"""
    
    api = LinkedInAPI()
    
    # Validate token
    if not api.validate_token():
        print("Invalid or missing access token!")
        print("Run authorization first.")
        return
    
    # Get user info
    user_info = api.get_user_info()
    print(f"Logged in as: {user_info.get('name', 'Unknown')}")
    
    # Create post
    text = "Testing LinkedIn API integration! 🚀 #Automation #AI"
    result = api.create_text_post(text)
    
    if result:
        print(f"Post URL: https://www.linkedin.com/feed/update/{result.get('id')}")


if __name__ == "__main__":
    # Run full workflow example
    example_full_workflow()
    
    # Or use quick post (uncomment below)
    # example_quick_post()
