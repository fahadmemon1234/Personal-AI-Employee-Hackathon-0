"""
Test Script for Social Media MCP Server
Tests Facebook/Instagram posting with dry-run mode

Usage:
    python test_social_mcp.py [--dry-run] [--real]
"""

import os
import sys
import json
import requests
from pathlib import Path
from datetime import datetime

# Configuration
MCP_SERVER_URL = os.getenv('MCP_SOCIAL_URL', 'http://localhost:8083')
DRY_RUN = os.getenv('SOCIAL_DRY_RUN', 'true').lower() == 'true'

# Directories
NEEDS_ACTION_DIR = Path('Needs_Action')
PENDING_APPROVAL_DIR = Path('Pending_Approval')
COMPLETED_DIR = Path('Completed')
BRIEFINGS_DIR = Path('Briefings')

# Create directories
for dir_path in [NEEDS_ACTION_DIR, PENDING_APPROVAL_DIR, COMPLETED_DIR, BRIEFINGS_DIR]:
    dir_path.mkdir(exist_ok=True)


def check_server_health():
    """Check if MCP server is running"""
    try:
        response = requests.get(f'{MCP_SERVER_URL}/health', timeout=5)
        if response.status_code == 200:
            print(f"[OK] MCP Social Server is running at {MCP_SERVER_URL}")
            data = response.json()
            print(f"  Status: {data.get('status', 'unknown')}")
            print(f"  Facebook configured: {data.get('facebook_configured', False)}")
            print(f"  Instagram configured: {data.get('instagram_configured', False)}")
            print(f"  Dry Run: {data.get('dry_run', True)}")
            return True
        else:
            print(f"[ERROR] MCP Server returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"[ERROR] Cannot connect to MCP Server at {MCP_SERVER_URL}")
        print("  Make sure to run: python mcp_social_server.py")
        return False


def test_post_to_facebook(dry_run=True):
    """Test Facebook posting"""
    print("\n[Test] Posting to Facebook...")
    
    payload = {
        "page_id": "110326951910826",
        "message": "🎉 Exciting News!\n\nWe're thrilled to announce our new AI-driven web development services!\n\n✅ Faster delivery times\n✅ Higher quality code\n✅ Better customer support\n\n📞 +92-300-1234567\n\n#WebDev #AI #Pakistan #Tech",
        "dry_run": dry_run
    }
    
    try:
        response = requests.post(
            f'{MCP_SERVER_URL}/tools/post_to_facebook',
            json=payload,
            timeout=30
        )
        result = response.json()
        
        print(f"  Response: {json.dumps(result, indent=2)}")
        
        if result.get('success'):
            print("  [OK] Facebook post test passed!")
            return True
        else:
            print(f"  [FAILED] Facebook post failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"  [ERROR] {e}")
        return False


def test_post_to_instagram(dry_run=True):
    """Test Instagram posting"""
    print("\n[Test] Posting to Instagram...")
    
    payload = {
        "account_id": "17841457182813798",
        "caption": "🚀 Transform your business with AI-powered solutions!\n\n#WebDevelopment #AI #Tech #Pakistan #Business #Innovation",
        "image_url": "https://img.freepik.com/free-photo/waterfall-chae-son-national-park-lampang-thailand_554837-639.jpg",
        "dry_run": dry_run
    }
    
    try:
        response = requests.post(
            f'{MCP_SERVER_URL}/tools/post_to_instagram',
            json=payload,
            timeout=30
        )
        result = response.json()
        
        print(f"  Response: {json.dumps(result, indent=2)}")
        
        if result.get('success'):
            print("  [OK] Instagram post test passed!")
            return True
        else:
            print(f"  [FAILED] Instagram post failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"  [ERROR] {e}")
        return False


def test_generate_summary():
    """Test summary generation"""
    print("\n[Test] Generating weekly summary...")
    
    try:
        response = requests.get(f'{MCP_SERVER_URL}/tools/generate_summary', timeout=30)
        result = response.json()
        
        print(f"  Response: {json.dumps(result, indent=2)}")
        
        if result.get('success'):
            summary = result.get('summary', {})
            print(f"  [OK] Summary generated!")
            print(f"    Period: {summary.get('period', 'N/A')}")
            print(f"    Total Posts: {summary.get('total_posts', 0)}")
            print(f"    Success Rate: {summary.get('success_rate', 'N/A')}")
            
            if result.get('saved_to'):
                print(f"    Saved to: {result.get('saved_to')}")
            
            return True
        else:
            print(f"  [FAILED] Summary generation failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"  [ERROR] {e}")
        return False


def test_list_posts():
    """Test listing posts"""
    print("\n[Test] Listing recent posts...")
    
    try:
        response = requests.get(f'{MCP_SERVER_URL}/tools/list_posts?limit=5', timeout=30)
        result = response.json()
        
        print(f"  Found {result.get('count', 0)} posts")
        
        if result.get('success'):
            posts = result.get('posts', [])
            for i, post in enumerate(posts[-3:], 1):
                print(f"  {i}. {post.get('platform', 'N/A')} - {post.get('timestamp', 'N/A')[:10]}")
                content = post.get('content', {})
                msg = content.get('message', content.get('caption', 'N/A'))
                msg_clean = msg.encode('ascii', 'ignore').decode('ascii')[:50]
                print(f"     Content: {msg_clean}...")
            
            return True
        else:
            print(f"  [FAILED] List posts failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"  [ERROR] {e}")
        return False


def run_full_test(dry_run=True):
    """Run complete test workflow"""
    mode_str = "[DRY RUN]" if dry_run else "[REAL]"
    
    print(f"\n{'='*60}")
    print(f"{mode_str} Social Media MCP Test Workflow")
    print(f"{'='*60}")
    
    # Check server health
    print("\n[Step 1] Checking server health...")
    if not check_server_health():
        print("  Server not running. Start with: python mcp_social_server.py")
        return False
    
    # Test Facebook post
    print("\n[Step 2] Testing Facebook post...")
    fb_result = test_post_to_facebook(dry_run)
    
    # Test Instagram post
    print("\n[Step 3] Testing Instagram post...")
    ig_result = test_post_to_instagram(dry_run)
    
    # Test list posts
    print("\n[Step 4] Testing list posts...")
    list_result = test_list_posts()
    
    # Test summary generation
    print("\n[Step 5] Testing summary generation...")
    summary_result = test_generate_summary()
    
    # Summary
    print(f"\n{'='*60}")
    print("Test Workflow Complete!")
    print(f"{'='*60}")
    
    results = {
        'Facebook Post': fb_result,
        'Instagram Post': ig_result,
        'List Posts': list_result,
        'Summary': summary_result
    }
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    for test, result in results.items():
        status = "[OK]" if result else "[FAILED]"
        print(f"  {status} {test}")
    
    return passed == total


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test Social Media MCP Server')
    parser.add_argument('--dry-run', action='store_true', help='Run in dry-run mode (default)')
    parser.add_argument('--real', action='store_true', help='Run with real posting (requires API tokens)')
    args = parser.parse_args()
    
    # Determine mode
    dry_run = not args.real  # Default to dry-run unless --real specified
    
    print("\n" + "="*60)
    print("Social Media MCP Server - Test Suite")
    print("="*60)
    print(f"\nMode: {'DRY RUN (simulated)' if dry_run else 'REAL (will post!)'}")
    print(f"MCP Server URL: {MCP_SERVER_URL}")
    
    if not dry_run:
        print("\n⚠️  WARNING: Real posting enabled! Posts will be published.")
        confirm = input("Continue? (yes/no): ")
        if confirm.lower() != 'yes':
            print("Aborted.")
            return
    
    # Run tests
    success = run_full_test(dry_run)
    
    # Exit code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
