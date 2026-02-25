"""
Test Script for X (Twitter) MCP Server
Tests tweet posting and summary generation

Usage:
    python test_x_mcp.py [--dry-run] [--real]
"""

import os
import sys
import json
import requests
from pathlib import Path
from datetime import datetime

# Configuration
MCP_SERVER_URL = os.getenv('MCP_X_URL', 'http://localhost:8084')
DRY_RUN = os.getenv('X_DRY_RUN', 'true').lower() == 'true'

# Directories
BRIEFINGS_DIR = Path('Briefings')
BRIEFINGS_DIR.mkdir(exist_ok=True)


def check_server_health():
    """Check if MCP server is running"""
    try:
        response = requests.get(f'{MCP_SERVER_URL}/health', timeout=5)
        if response.status_code == 200:
            print(f"[OK] MCP X Server is running at {MCP_SERVER_URL}")
            data = response.json()
            print(f"  Status: {data.get('status', 'unknown')}")
            print(f"  Username: @{data.get('username', 'N/A')}")
            print(f"  API Configured: {data.get('api_configured', False)}")
            print(f"  Dry Run: {data.get('dry_run', True)}")
            return True
        else:
            print(f"[ERROR] MCP Server returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"[ERROR] Cannot connect to MCP Server at {MCP_SERVER_URL}")
        print("  Make sure to run: python mcp_x_server.py")
        return False


def test_post_tweet(dry_run=True):
    """Test tweet posting"""
    print("\n[Test] Posting tweet...")
    
    # Test tweet (under 280 chars)
    tweet_text = "🚀 Exciting news! We're launching AI-driven web development services! \n\n✅ 50% faster delivery\n✅ Higher quality code\n✅ 24/7 support\n\n#AI #WebDev #Pakistan #Tech #Innovation"
    
    payload = {
        "text": tweet_text,
        "dry_run": dry_run
    }
    
    try:
        response = requests.post(
            f'{MCP_SERVER_URL}/tools/post_tweet',
            json=payload,
            timeout=30
        )
        result = response.json()
        
        print(f"  Response: {json.dumps(result, indent=2)}")
        
        if result.get('success'):
            print("  [OK] Tweet test passed!")
            if result.get('character_count'):
                print(f"  Character count: {result.get('character_count')}/280")
            return True
        else:
            print(f"  [FAILED] Tweet failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"  [ERROR] {e}")
        return False


def test_get_recent_posts():
    """Test getting recent posts"""
    print("\n[Test] Getting recent posts...")
    
    try:
        response = requests.get(f'{MCP_SERVER_URL}/tools/get_recent_posts?limit=5', timeout=30)
        result = response.json()
        
        print(f"  Found {result.get('count', 0)} posts")
        
        if result.get('success'):
            posts = result.get('posts', [])
            for i, post in enumerate(posts[-3:], 1):
                print(f"  {i}. {post.get('timestamp', 'N/A')[:16].replace('T', ' ')}")
                content = post.get('content', {})
                text = content.get('text', 'N/A')[:50]
                print(f"     Tweet: {text}...")
            
            return True
        else:
            print(f"  [FAILED] Get posts failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"  [ERROR] {e}")
        return False


def test_generate_summary():
    """Test summary generation"""
    print("\n[Test] Generating weekly summary...")
    
    try:
        response = requests.get(f'{MCP_SERVER_URL}/tools/generate_x_summary', timeout=30)
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


def run_full_test(dry_run=True):
    """Run complete test workflow"""
    mode_str = "[DRY RUN]" if dry_run else "[REAL]"
    
    print(f"\n{'='*60}")
    print(f"{mode_str} X MCP Test Workflow")
    print(f"{'='*60}")
    
    # Check server health
    print("\n[Step 1] Checking server health...")
    if not check_server_health():
        print("  Server not running. Start with: python mcp_x_server.py")
        return False
    
    # Test tweet posting
    print("\n[Step 2] Testing tweet posting...")
    tweet_result = test_post_tweet(dry_run)
    
    # Test get recent posts
    print("\n[Step 3] Testing get recent posts...")
    posts_result = test_get_recent_posts()
    
    # Test summary generation
    print("\n[Step 4] Testing summary generation...")
    summary_result = test_generate_summary()
    
    # Summary
    print(f"\n{'='*60}")
    print("Test Workflow Complete!")
    print(f"{'='*60}")
    
    results = {
        'Post Tweet': tweet_result,
        'Get Recent Posts': posts_result,
        'Generate Summary': summary_result
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
    
    parser = argparse.ArgumentParser(description='Test X (Twitter) MCP Server')
    parser.add_argument('--dry-run', action='store_true', help='Run in dry-run mode (default)')
    parser.add_argument('--real', action='store_true', help='Run with real posting (requires API tokens)')
    args = parser.parse_args()
    
    # Determine mode
    dry_run = not args.real  # Default to dry-run unless --real specified
    
    print("\n" + "="*60)
    print("X (Twitter) MCP Server - Test Suite")
    print("="*60)
    print(f"\nMode: {'DRY RUN (simulated)' if dry_run else 'REAL (will post!)'}")
    print(f"MCP Server URL: {MCP_SERVER_URL}")
    
    if not dry_run:
        print("\n⚠️  WARNING: Real posting enabled! Tweets will be published.")
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
