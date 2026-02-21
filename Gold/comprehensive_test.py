"""
comprehensive_test.py
Comprehensive test suite for all Gold Tier components
"""

import os
import sys
from pathlib import Path
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("="*70)
print("COMPREHENSIVE GOLD TIER COMPONENT TEST")
print("="*70)

# Test results tracking
tests_passed = 0
tests_failed = 0
tests_warning = 0

def test_result(name, passed, message=""):
    global tests_passed, tests_failed, tests_warning
    if passed:
        print(f"[PASS] {name}")
        tests_passed += 1
    elif passed is None:
        print(f"[WARN] {name} - {message}")
        tests_warning += 1
    else:
        print(f"[FAIL] {name} - {message}")
        tests_failed += 1

# Test 1: Environment Variables
print("\n1. ENVIRONMENT VARIABLES")
print("-"*70)

env_vars = {
    "ODOO_URL": False,
    "ODOO_DB": False,
    "ODOO_USERNAME": False,
    "ODOO_PASSWORD": False,
    "GMAIL_CREDENTIALS_FILE": False,
    "TWITTER_API_KEY": False,
    "TWITTER_API_SECRET": False,
    "TWITTER_ACCESS_TOKEN": False,
    "TWITTER_ACCESS_TOKEN_SECRET": False,
    "META_ACCESS_TOKEN": False,
    "FACEBOOK_PAGE_ID": False,
    "INSTAGRAM_BUSINESS_ACCOUNT_ID": False,
}

for var, required in env_vars.items():
    value = os.getenv(var)
    if value:
        test_result(f"{var}", True)
    else:
        test_result(f"{var}", None, "Not set (optional for testing)")

# Test 2: File Existence
print("\n2. CORE FILES")
print("-"*70)

core_files = [
    "gmail_watcher.py",
    "whatsapp_watcher.py",
    "reasoning_loop.py",
    "agent_interface.py",
    "linkedin_poster.py",
    "ceo_briefing_skill.py",
    "requirements.txt",
    "mcp.json",
    "ARCHITECTURE.md",
]

for file in core_files:
    exists = Path(file).exists()
    test_result(f"{file}", exists, "Missing" if not exists else "")

# Test 3: Directory Structure
print("\n3. DIRECTORY STRUCTURE")
print("-"*70)

directories = [
    "odoo_integration",
    "social_media_integration",
    ".qwen/skills",
    "Needs_Action",
    "Approved",
    "Completed",
    "Briefings",
    "Bank_Transactions",
]

for dir_path in directories:
    exists = Path(dir_path).is_dir()
    test_result(f"{dir_path}/", exists, "Missing" if not exists else "")

# Test 4: Odoo Integration
print("\n4. ODOO INTEGRATION")
print("-"*70)

odoo_files = [
    "odoo_integration/odoo_connector.py",
    "odoo_integration/mcp_server.py",
    "odoo_integration/sync_invoices.py",
]

for file in odoo_files:
    exists = Path(file).exists()
    test_result(f"{file}", exists, "Missing" if not exists else "")

# Test Odoo connection
try:
    from odoo_integration.odoo_connector import get_odoo_connection
    odoo_conn = get_odoo_connection()
    if odoo_conn:
        test_result("Odoo Connection", True)
    else:
        test_result("Odoo Connection", None, "Could not connect (check credentials)")
except Exception as e:
    test_result("Odoo Connection", False, str(e))

# Test 5: Social Media Integration
print("\n5. SOCIAL MEDIA INTEGRATION")
print("-"*70)

social_files = [
    "social_media_integration/twitter_connector.py",
    "social_media_integration/twitter_mcp_server.py",
    "social_media_integration/facebook_instagram_connector.py",
    "social_media_integration/facebook_instagram_mcp_server.py",
]

for file in social_files:
    exists = Path(file).exists()
    test_result(f"{file}", exists, "Missing" if not exists else "")

# Test Twitter connection
try:
    from social_media_integration.twitter_connector import get_twitter_connection
    twitter_conn = get_twitter_connection()
    if twitter_conn:
        test_result("Twitter Connection", True)
    else:
        test_result("Twitter Connection", None, "Could not connect (check credentials)")
except Exception as e:
    test_result("Twitter Connection", False, str(e))

# Test Facebook/Instagram connection
try:
    from social_media_integration.facebook_instagram_connector import get_facebook_instagram_connection
    fb_ig_conn = get_facebook_instagram_connection()
    if fb_ig_conn:
        test_result("Facebook/Instagram Connection", True)
    else:
        test_result("Facebook/Instagram Connection", None, "Could not connect (check credentials)")
except Exception as e:
    test_result("Facebook/Instagram Connection", False, str(e))

# Test 6: Agent Skills
print("\n6. AGENT SKILLS")
print("-"*70)

skills = [
    ".qwen/skills/gmail_skill",
    ".qwen/skills/whatsapp_skill",
    ".qwen/skills/linkedin_skill",
    ".qwen/skills/twitter_skill",
    ".qwen/skills/facebook_instagram_skill",
]

for skill in skills:
    exists = Path(skill).is_dir()
    test_result(f"{skill}/", exists, "Missing" if not exists else "")

# Test CEO Briefing Skill
try:
    from ceo_briefing_skill import generate_ceo_briefing
    test_result("CEO Briefing Skill Import", True)
except Exception as e:
    test_result("CEO Briefing Skill Import", False, str(e))

# Test 7: MCP Configuration
print("\n7. MCP CONFIGURATION")
print("-"*70)

try:
    with open("mcp.json", 'r') as f:
        mcp_config = json.load(f)
    
    servers = mcp_config.get("servers", {})
    required_servers = ["email-mcp", "browser-mcp", "odoo-mcp", "twitter-mcp", "facebook-instagram-mcp"]
    
    for server in required_servers:
        exists = server in servers
        test_result(f"MCP Server: {server}", exists, "Missing" if not exists else "")
    
    test_result("MCP Configuration Valid", True)
except Exception as e:
    test_result("MCP Configuration", False, str(e))

# Test 8: Import Tests
print("\n8. MODULE IMPORT TESTS")
print("-"*70)

modules_to_test = [
    ("Gmail Watcher", "gmail_watcher"),
    ("WhatsApp Watcher", "whatsapp_watcher"),
    ("Reasoning Loop", "reasoning_loop"),
    ("Agent Interface", "agent_interface"),
    ("LinkedIn Poster", "linkedin_poster"),
    ("Email Approval Workflow", "email_approval_workflow"),
    ("Scheduler", "scheduler"),
]

for name, module_name in modules_to_test:
    try:
        __import__(module_name)
        test_result(f"{name} Import", True)
    except Exception as e:
        test_result(f"{name} Import", False, str(e))

# Test 9: Credentials Files
print("\n9. CREDENTIALS FILES")
print("-"*70)

credential_files = [
    ("Gmail Credentials", "credentials.json"),
    (".env File", ".env"),
]

for name, file_path in credential_files:
    exists = Path(file_path).exists()
    test_result(f"{name}", exists, "Missing" if not exists else "")

# Test 10: Syntax Check
print("\n10. PYTHON SYNTAX CHECK")
print("-"*70)

import py_compile

python_files = [
    "gmail_watcher.py",
    "whatsapp_watcher.py",
    "reasoning_loop.py",
    "agent_interface.py",
    "ceo_briefing_skill.py",
    "odoo_integration/odoo_connector.py",
    "odoo_integration/mcp_server.py",
    "social_media_integration/twitter_connector.py",
    "social_media_integration/twitter_mcp_server.py",
    "social_media_integration/facebook_instagram_connector.py",
    "social_media_integration/facebook_instagram_mcp_server.py",
]

for file in python_files:
    try:
        py_compile.compile(file, doraise=True)
        test_result(f"{file} Syntax", True)
    except Exception as e:
        test_result(f"{file} Syntax", False, str(e))

# Summary
print("\n" + "="*70)
print("TEST SUMMARY")
print("="*70)
print(f"[PASS] Passed: {tests_passed}")
print(f"[WARN] Warnings: {tests_warning}")
print(f"[FAIL] Failed: {tests_failed}")
print()

total = tests_passed + tests_failed
success_rate = (tests_passed / total * 100) if total > 0 else 0

print(f"Success Rate: {success_rate:.1f}%")

if tests_failed == 0:
    print("\n[SUCCESS] ALL TESTS PASSED!")
else:
    print(f"\n[WARNING] {tests_failed} test(s) failed. Review the errors above.")

sys.exit(0 if tests_failed == 0 else 1)
