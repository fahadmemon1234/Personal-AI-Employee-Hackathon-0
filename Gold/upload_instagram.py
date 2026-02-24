"""
Instagram Post Upload Script
Run this to post to Instagram
"""
import requests

# Configuration
INSTAGRAM_ACCOUNT_ID = '17841436842078450'
IMAGE_URL = 'https://images.pexels.com/photos/1172675/pexels-photo-1172675.jpeg'
CAPTION = 'Beautiful view! #Photography #Nature #Pakistan #AI #Tech'

# Post payload
payload = {
    'account_id': INSTAGRAM_ACCOUNT_ID,
    'caption': CAPTION,
    'media_path': IMAGE_URL,
    'dry_run': False  # Set to True for testing, False for real post
}

print("=" * 60)
print("Instagram Post Upload")
print("=" * 60)
print(f"Caption: {CAPTION}")
print(f"Image: {IMAGE_URL}")
print(f"Dry Run: {payload['dry_run']}")
print("=" * 60)

try:
    # Send post request
    response = requests.post(
        'http://localhost:8083/tools/post_to_instagram',
        json=payload,
        timeout=60
    )
    
    result = response.json()
    
    print("\nResult:")
    if result.get('success'):
        print('✅ Post Successful!')
        print(f'Post ID: {result.get("post_id")}')
    else:
        print('❌ Post Failed')
        print(f'Error: {result.get("error")}')
    
    print("\nFull Response:")
    print(result)
    
except requests.exceptions.ConnectionError:
    print('❌ Connection Error!')
    print('Make sure MCP Social Server is running:')
    print('   python mcp_social_server.py')
except Exception as e:
    print(f'❌ Error: {e}')

print("=" * 60)
