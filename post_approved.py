"""
Post Approved Social Media Content
Run this after moving files to /Approved/ folder
"""

import requests
import shutil
from pathlib import Path

MCP_URL = "http://localhost:8083"
APPROVED = Path("Approved")
COMPLETED = Path("Completed")

print("="*60)
print("Posting Approved Content")
print("="*60)

if not APPROVED.exists():
    print("No Approved folder found!")
    exit(1)

# Find all approval files
files = list(APPROVED.glob("SOCIAL_POST_*.md"))

if not files:
    print("No approval files found in /Approved/ folder")
    print("Move files from /Pending_Approval/ to /Approved/ first")
    exit(1)

print(f"Found {len(files)} file(s) to process\n")

for file in files:
    print(f"Processing: {file.name}")
    
    try:
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract content from markdown
        import re
        match = re.search(r'```\n(.*?)\n```', content, re.DOTALL)
        
        if not match:
            print(f"  [SKIP] No content found in file")
            continue
        
        message = match.group(1)
        
        # Determine platform and post
        if "FACEBOOK" in file.name:
            print("  Posting to Facebook...")
            resp = requests.post(
                f"{MCP_URL}/tools/post_to_facebook",
                json={
                    "page_id": "110326951910826",
                    "message": message,
                    "dry_run": False  # REAL POST
                },
                timeout=30
            )
            result = resp.json()
            
        elif "INSTAGRAM" in file.name:
            print("  Posting to Instagram...")
            resp = requests.post(
                f"{MCP_URL}/tools/post_to_instagram",
                json={
                    "account_id": "17841457182813798",
                    "caption": message,
                    "image_url": "https://img.freepik.com/free-photo/waterfall-chae-son-national-park-lampang-thailand_554837-639.jpg",
                    "dry_run": False  # REAL POST
                },
                timeout=30
            )
            result = resp.json()
        
        else:
            print(f"  [SKIP] Unknown platform")
            continue
        
        # Check result
        if result.get('success'):
            print(f"  [OK] Posted successfully!")
            if result.get('post_id'):
                print(f"       Post ID: {result.get('post_id')}")
            # Move to Completed
            shutil.move(str(file), str(COMPLETED / file.name))
            print(f"       Moved to /Completed/")
        else:
            print(f"  [FAILED] {result.get('error')}")
    
    except Exception as e:
        print(f"  [ERROR] {e}")

print("\n" + "="*60)
print("Done!")
print("="*60)
