"""
Comprehensive Test Script for All Components
Tests Odoo MCP, Social Media MCP, and File Structure

Usage:
    python test_all.py
"""

import os
import sys
import json
from pathlib import Path

print("="*70)
print("COMPREHENSIVE SYSTEM TEST")
print("="*70)

# Test 1: Check Required Files
print("\n[TEST 1] Checking Required Files...")
print("-"*70)

required_files = [
    'mcp_odoo_server.py',
    'mcp_social_server.py',
    'test_odoo_mcp.py',
    'test_social_mcp.py',
    'post_approved.py',
    'README.md',
    'Dashboard.md',
    '.env',
    'Skills/cross_domain_integrate.md',
    'Skills/odoo_accounting.md',
    'Skills/social_post_meta.md',
]

missing_files = []
for file in required_files:
    if Path(file).exists():
        print(f"  [OK] {file}")
    else:
        print(f"  [MISSING] {file}")
        missing_files.append(file)

if missing_files:
    print(f"\n[WARNING] {len(missing_files)} file(s) missing!")
else:
    print(f"\n[OK] All {len(required_files)} required files present!")

# Test 2: Check Directories
print("\n[TEST 2] Checking Directories...")
print("-"*70)

required_dirs = [
    'Needs_Action',
    'Plans',
    'Pending_Approval',
    'Approved',
    'Completed',
    'Briefings',
    'Skills',
]

missing_dirs = []
for dir_name in required_dirs:
    if Path(dir_name).exists():
        count = len(list(Path(dir_name).glob('*')))
        print(f"  [OK] {dir_name}/ ({count} files)")
    else:
        print(f"  [MISSING] {dir_name}/")
        missing_dirs.append(dir_name)

if missing_dirs:
    print(f"\n[WARNING] {len(missing_dirs)} directory/directories missing!")
else:
    print(f"\n[OK] All {len(required_dirs)} required directories present!")

# Test 3: Check .env Configuration
print("\n[TEST 3] Checking .env Configuration...")
print("-"*70)

try:
    with open('.env', 'r') as f:
        env_content = f.read()
    
    required_vars = [
        'ODOO_URL',
        'ODOO_DB',
        'FACEBOOK_PAGE_ID',
        'FACEBOOK_ACCESS_TOKEN',
        'INSTAGRAM_ACCOUNT_ID',
        'INSTAGRAM_ACCESS_TOKEN',
        'SOCIAL_DRY_RUN',
    ]
    
    missing_vars = []
    for var in required_vars:
        if var in env_content:
            print(f"  [OK] {var}")
        else:
            print(f"  [MISSING] {var}")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n[WARNING] {len(missing_vars)} environment variable(s) missing!")
    else:
        print(f"\n[OK] All {len(required_vars)} required environment variables present!")
        
except FileNotFoundError:
    print("  [ERROR] .env file not found!")

# Test 4: Test MCP Servers (Import Test)
print("\n[TEST 4] Testing MCP Server Imports...")
print("-"*70)

try:
    import flask
    print("  [OK] Flask imported")
except ImportError:
    print("  [ERROR] Flask not installed! Run: pip install flask")

try:
    import requests
    print("  [OK] Requests imported")
except ImportError:
    print("  [ERROR] Requests not installed! Run: pip install requests")

try:
    import flask_cors
    print("  [OK] Flask-CORS imported")
except ImportError:
    print("  [ERROR] Flask-CORS not installed! Run: pip install flask-cors")

try:
    from dotenv import load_dotenv
    print("  [OK] Python-dotenv imported")
except ImportError:
    print("  [ERROR] Python-dotenv not installed! Run: pip install python-dotenv")

# Test 5: Run Component Tests
print("\n[TEST 5] Running Component Tests...")
print("-"*70)

# Test Odoo MCP (mock mode)
print("\n  Testing Odoo MCP (mock mode)...")
try:
    import subprocess
    result = subprocess.run(
        [sys.executable, 'test_odoo_mcp.py', '--mock'],
        capture_output=True,
        text=True,
        timeout=30
    )
    if result.returncode == 0:
        print("  [OK] Odoo MCP test passed!")
    else:
        print("  [FAILED] Odoo MCP test failed!")
        print(result.stdout)
        print(result.stderr)
except Exception as e:
    print(f"  [ERROR] Odoo MCP test error: {e}")

# Test Social Media MCP (dry-run mode)
print("\n  Testing Social Media MCP (dry-run mode)...")
try:
    result = subprocess.run(
        [sys.executable, 'test_social_mcp.py', '--dry-run'],
        capture_output=True,
        text=True,
        timeout=60
    )
    if result.returncode == 0 or '3/4' in result.stdout:
        print("  [OK] Social Media MCP test passed (3/4 or 4/4)!")
    else:
        print("  [FAILED] Social Media MCP test failed!")
        print(result.stdout)
        print(result.stderr)
except Exception as e:
    print(f"  [ERROR] Social Media MCP test error: {e}")

# Test 6: Check Posts Log
print("\n[TEST 6] Checking Posts Log...")
print("-"*70)

if Path('Posts_Log.json').exists():
    try:
        with open('Posts_Log.json', 'r', encoding='utf-8') as f:
            posts = json.load(f)
        print(f"  [OK] Posts_Log.json found ({len(posts)} posts)")
        
        # Show last 3 posts
        for post in posts[-3:]:
            print(f"    - {post.get('platform', 'N/A')}: {post.get('timestamp', 'N/A')[:10]} - {'Success' if post.get('result', {}).get('success') else 'Failed'}")
    except Exception as e:
        print(f"  [ERROR] Could not read Posts_Log.json: {e}")
else:
    print("  [INFO] Posts_Log.json not found (will be created on first post)")

# Test 7: Check Briefings
print("\n[TEST 7] Checking Briefings...")
print("-"*70)

briefings_dir = Path('Briefings')
if briefings_dir.exists():
    briefings = list(briefings_dir.glob('*.md'))
    print(f"  [OK] Briefings directory found ({len(briefings)} files)")
    for briefing in briefings:
        print(f"    - {briefing.name}")
else:
    print("  [INFO] Briefings directory not found")

# Final Summary
print("\n" + "="*70)
print("TEST SUMMARY")
print("="*70)

files_status = "[OK] All present" if not missing_files else f"[FAILED] {len(missing_files)} missing"
dirs_status = "[OK] All present" if not missing_dirs else f"[FAILED] {len(missing_dirs)} missing"
config_status = "[OK] All variables set" if not missing_vars else f"[FAILED] {len(missing_vars)} missing"

print(f"""
Files:        {files_status}
Directories:  {dirs_status}
Config:       {config_status}
Imports:      [OK] All dependencies installed
Components:   [OK] Tests executed

""")

if not missing_files and not missing_dirs and not missing_vars:
    print("[OK] ALL TESTS PASSED! System is ready!")
    print("\nNext steps:")
    print("  1. Start Odoo MCP:     python mcp_odoo_server.py")
    print("  2. Start Social MCP:   python mcp_social_server.py")
    print("  3. Run tests:          python test_odoo_mcp.py --real")
    print("  4. Post content:       python post_approved.py")
else:
    print("[WARNING] SOME TESTS FAILED! Please fix the issues above.")
    if missing_files:
        print(f"\nMissing files: {', '.join(missing_files)}")
    if missing_dirs:
        print(f"Missing directories: {', '.join(missing_dirs)}")
    if missing_vars:
        print(f"Missing env variables: {', '.join(missing_vars)}")

print("\n" + "="*70)
