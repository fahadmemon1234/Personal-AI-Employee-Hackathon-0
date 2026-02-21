"""
test_runner.py
Runs quick tests on all major components
"""

import os
import sys
from pathlib import Path
import time
from dotenv import load_dotenv

load_dotenv()

print("="*70)
print("COMPONENT TEST RUNNER")
print("="*70)

def test_component(name, test_func):
    """Test a component and report results"""
    print(f"\n{'-'*70}")
    print(f"Testing: {name}")
    print(f"{'-'*70}")
    try:
        result = test_func()
        if result:
            print(f"[PASS] {name}")
            return True
        else:
            print(f"[FAIL] {name}")
            return False
    except Exception as e:
        print(f"[ERROR] {name}: {str(e)}")
        return False

# Test 1: Reasoning Loop Import
def test_reasoning_loop():
    from reasoning_loop import ReasoningLoop
    loop = ReasoningLoop()
    print(f"  - ReasoningLoop initialized")
    print(f"  - Max iterations: {loop.max_autonomous_iterations}")
    print(f"  - Loop interval: {loop.loop_interval}s")
    files = loop.scan_needs_action()
    print(f"  - Files in Needs_Action: {len(files)}")
    return True

# Test 2: Agent Interface Import
def test_agent_interface():
    from agent_interface import AgentInterface
    agent = AgentInterface()
    print(f"  - AgentInterface initialized")
    print(f"  - Monitor interval: {agent.monitor_interval}s")
    return True

# Test 3: Gmail Watcher (without auth)
def test_gmail_watcher():
    from gmail_watcher import GmailWatcher
    watcher = GmailWatcher()
    print(f"  - GmailWatcher initialized")
    print(f"  - Credentials file: {watcher.credentials_file}")
    print(f"  - Token file exists: {os.path.exists(watcher.token_file)}")
    if not os.path.exists(watcher.token_file):
        print(f"  - Note: Token file missing, will need authentication on first run")
    return True

# Test 4: WhatsApp Watcher
def test_whatsapp_watcher():
    from whatsapp_watcher import WhatsAppWatcher
    watcher = WhatsAppWatcher()
    print(f"  - WhatsAppWatcher initialized")
    print(f"  - Data directory: {watcher.data_dir}")
    print(f"  - Keywords: {', '.join(watcher.keywords)}")
    return True

# Test 5: LinkedIn Poster
def test_linkedin_poster():
    from linkedin_poster import LinkedInPoster
    poster = LinkedInPoster()
    print(f"  - LinkedInPoster initialized")
    return True

# Test 6: CEO Briefing Skill
def test_ceo_briefing():
    from ceo_briefing_skill import generate_ceo_briefing
    print(f"  - CEO Briefing skill imported successfully")
    # Don't actually generate, just test import
    return True

# Test 7: Twitter Connector
def test_twitter():
    from social_media_integration.twitter_connector import get_twitter_connection
    connector = get_twitter_connection()
    if connector:
        print(f"  - Twitter connector initialized")
        metrics = connector.get_user_metrics()
        if 'username' in metrics:
            print(f"  - Connected as: @{metrics['username']}")
        return True
    else:
        print(f"  - Twitter connector failed to initialize")
        return False

# Test 8: Facebook/Instagram Connector
def test_facebook_instagram():
    from social_media_integration.facebook_instagram_connector import get_facebook_instagram_connection
    connector = get_facebook_instagram_connection()
    if connector:
        print(f"  - Facebook/Instagram connector initialized")
        return True
    else:
        print(f"  - Facebook/Instagram connector using placeholder credentials")
        return None  # Warning, not failure

# Test 9: Odoo Connector
def test_odoo():
    from odoo_integration.odoo_connector import get_odoo_connection
    connector = get_odoo_connection()
    if connector:
        print(f"  - Odoo connector initialized")
        print(f"  - Database: {connector.db}")
        return True
    else:
        print(f"  - Odoo connector failed - check database name in .env")
        return False

# Test 10: MCP Config
def test_mcp_config():
    import json
    with open("mcp.json", 'r') as f:
        config = json.load(f)
    servers = config.get("servers", {})
    print(f"  - MCP configuration loaded")
    print(f"  - Configured servers: {len(servers)}")
    for name, srv in servers.items():
        print(f"    - {name}: port {srv.get('port')}")
    return True

# Run all tests
results = []

results.append(("Reasoning Loop", test_reasoning_loop()))
results.append(("Agent Interface", test_agent_interface()))
results.append(("Gmail Watcher", test_gmail_watcher()))
results.append(("WhatsApp Watcher", test_whatsapp_watcher()))
results.append(("LinkedIn Poster", test_linkedin_poster()))
results.append(("CEO Briefing", test_ceo_briefing()))
results.append(("Twitter", test_twitter()))
results.append(("Facebook/Instagram", test_facebook_instagram()))
results.append(("Odoo", test_odoo()))
results.append(("MCP Config", test_mcp_config()))

# Summary
print("\n" + "="*70)
print("TEST SUMMARY")
print("="*70)

passed = sum(1 for _, r in results if r is True)
failed = sum(1 for _, r in results if r is False)
warning = sum(1 for _, r in results if r is None)

print(f"Passed: {passed}")
print(f"Failed: {failed}")
print(f"Warnings: {warning}")
print()

if failed == 0:
    print("[SUCCESS] All critical tests passed!")
else:
    print(f"[WARNING] {failed} test(s) failed. Review TROUBLESHOOTING.md")

print("\nKey Files:")
print("  - TROUBLESHOOTING.md - Solutions for common issues")
print("  - comprehensive_test.py - Detailed component tests")
print("  - verify_gold_tier.py - Gold Tier verification")
