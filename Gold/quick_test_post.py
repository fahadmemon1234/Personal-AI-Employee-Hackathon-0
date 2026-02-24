"""
Quick Social Media Post Test
Facebook & Instagram Real Post
"""

import requests
import json

MCP_URL = "http://localhost:8083"

print("="*60)
print("Social Media Real Post Test")
print("="*60)

# Facebook Post
print("\n[1] Facebook Post...")
fb_response = requests.post(
    f"{MCP_URL}/tools/post_to_facebook",
    json={
        "page_id": "106665648626271",
        "message": "🎉 Hello from my AI Employee System!\n\nThis is a test post from my automated MCP integration.\n\n✅ Odoo Accounting\n✅ Social Media Automation\n✅ AI-Driven Workflows\n\n#AI #Tech #Pakistan #Automation",
        "dry_run": False  # REAL POST
    },
    timeout=30
)

fb_result = fb_response.json()
print(f"  Response: {json.dumps(fb_result, indent=2)}")

if fb_result.get('success'):
    print("  [OK] FACEBOOK POST SUCCESS!")
    print(f"  Post ID: {fb_result.get('post_id')}")
    print(f"  Check: https://www.facebook.com/106665648626271")
else:
    print(f"  [FAILED] FACEBOOK POST FAILED: {fb_result.get('error')}")

# Instagram Post
print("\n[2] Instagram Post...")
ig_response = requests.post(
    f"{MCP_URL}/tools/post_to_instagram",
    json={
        "account_id": "17841436842078450",
        "caption": "🚀 AI Automation Test!\n\n#AI #Tech #Pakistan #Business #Automation",
        "media_path": "test_image.jpg",
        "dry_run": False  # REAL POST
    },
    timeout=30
)

ig_result = ig_response.json()
print(f"  Response: {json.dumps(ig_result, indent=2)}")

if ig_result.get('success'):
    print("  [OK] INSTAGRAM POST SUCCESS!")
    print(f"  Post ID: {ig_result.get('post_id')}")
else:
    print(f"  [FAILED] INSTAGRAM POST FAILED: {ig_result.get('error')}")

print("\n" + "="*60)
print("Test Complete!")
print("="*60)
