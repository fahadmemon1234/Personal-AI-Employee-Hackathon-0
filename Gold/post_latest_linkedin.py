"""
Auto-approve and post the latest LinkedIn post
"""
import sys
import codecs

# Fix Unicode encoding for Windows
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

from pathlib import Path
from linkedin_poster import LinkedInPoster

# Get latest pending post
pending_dir = Path("Pending_Approval")
posts = list(pending_dir.glob("linkedin_post_*.txt"))
posts.sort(key=lambda x: x.stat().st_mtime, reverse=True)

if posts:
    latest = posts[0]
    print(f"Latest post: {latest.name}")
    
    # Show content
    with open(latest, 'r', encoding='utf-8') as f:
        content = f.read()
    print("\nContent:")
    print(content)
    print("\n" + "="*60)
    
    # Move to approved
    approved_dir = Path("Approved")
    approved_dir.mkdir(exist_ok=True)
    approved_path = approved_dir / latest.name
    latest.rename(approved_path)
    print(f"[OK] Moved to Approved: {approved_path.name}")
    
    # Execute post
    poster = LinkedInPoster()
    success = poster.execute_approved_post(approved_path)
    
    if success:
        print("[OK] LinkedIn post published successfully!")
    else:
        print("[FAIL] Post failed validation")
else:
    print("No pending posts found")
