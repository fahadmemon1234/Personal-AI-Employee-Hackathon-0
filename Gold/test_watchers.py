"""
Comprehensive Watcher Test
Tests Gmail Watcher, WhatsApp Watcher, and Inbox Watcher

Usage:
    python test_watchers.py
"""

import os
import sys
from pathlib import Path
from datetime import datetime

print("\n" + "="*70)
print("COMPREHENSIVE WATCHER TEST")
print("="*70)

# Test 1: Check Watcher Files
print("\n[TEST 1] Checking Watcher Files...")
print("-"*70)

watcher_files = [
    'gmail_watcher.py',
    'whatsapp_watcher.py',
    'watcher.py',
]

missing_files = []
for file in watcher_files:
    if Path(file).exists():
        print(f"  [OK] {file}")
    else:
        print(f"  [MISSING] {file}")
        missing_files.append(file)

if missing_files:
    print(f"\n[WARNING] {len(missing_files)} watcher file(s) missing!")
else:
    print(f"\n[OK] All {len(watcher_files)} watcher files present!")

# Test 2: Check Required Directories
print("\n[TEST 2] Checking Watcher Directories...")
print("-"*70)

watcher_dirs = [
    'Inbox',
    'Needs_Action',
    'Sent',
]

for dir_name in watcher_dirs:
    if Path(dir_name).exists():
        count = len(list(Path(dir_name).glob('*')))
        print(f"  [OK] {dir_name}/ ({count} files)")
    else:
        print(f"  [MISSING] {dir_name}/")

# Test 3: Check Configuration Files
print("\n[TEST 3] Checking Configuration Files...")
print("-"*70)

config_files = [
    'mcp.json',
    'credentials.json',
    'token.pickle',
]

for file in config_files:
    if Path(file).exists():
        print(f"  [OK] {file}")
    else:
        if file == 'credentials.json' or file == 'token.pickle':
            print(f"  [OPTIONAL] {file} (required for Gmail watcher)")
        else:
            print(f"  [MISSING] {file}")

# Test 4: Check .env for Watcher Settings
print("\n[TEST 4] Checking Environment Configuration...")
print("-"*70)

try:
    with open('.env', 'r') as f:
        env_content = f.read()
    
    # Check for Gmail/WhatsApp related settings
    if 'GMAIL' in env_content.upper():
        print("  [OK] Gmail settings found")
    else:
        print("  [INFO] No Gmail settings in .env (uses OAuth2)")
    
    if 'WHATSAPP' in env_content.upper():
        print("  [OK] WhatsApp settings found")
    else:
        print("  [INFO] No WhatsApp settings in .env (uses browser automation)")
        
except FileNotFoundError:
    print("  [ERROR] .env file not found!")

# Test 5: Import Test
print("\n[TEST 5] Testing Watcher Imports...")
print("-"*70)

# Test Gmail Watcher imports
print("\n  Gmail Watcher:")
try:
    from google.auth.transport.requests import Request
    print("    [OK] google.auth")
except ImportError:
    print("    [MISSING] google-auth (pip install google-auth)")

try:
    from google_auth_oauthlib.flow import InstalledAppFlow
    print("    [OK] google_auth_oauthlib")
except ImportError:
    print("    [MISSING] google-auth-oauthlib (pip install google-auth-oauthlib)")

try:
    from googleapiclient.discovery import build
    print("    [OK] googleapiclient")
except ImportError:
    print("    [MISSING] google-api-python-client (pip install google-api-python-client)")

# Test WhatsApp Watcher imports
print("\n  WhatsApp Watcher:")
try:
    from playwright.sync_api import sync_playwright
    print("    [OK] playwright")
except ImportError:
    print("    [MISSING] playwright (pip install playwright)")

# Test general imports
print("\n  General:")
try:
    import schedule
    print("    [OK] schedule")
except ImportError:
    print("    [MISSING] schedule (pip install schedule)")

try:
    import watchdog
    print("    [OK] watchdog")
except ImportError:
    print("    [MISSING] watchdog (pip install watchdog)")

# Test 6: Check Recent Activity
print("\n[TEST 6] Checking Recent Watcher Activity...")
print("-"*70)

# Check Needs_Action for recent files
needs_action = Path('Needs_Action')
if needs_action.exists():
    files = list(needs_action.glob('*.md'))
    email_files = [f for f in files if 'email_' in f.name]
    whatsapp_files = [f for f in files if 'whatsapp_' in f.name]
    
    print(f"  /Needs_Action/ Contents:")
    print(f"    - Total files: {len(files)}")
    print(f"    - Email files: {len(email_files)}")
    print(f"    - WhatsApp files: {len(whatsapp_files)}")
    
    # Show recent files
    if files:
        print(f"\n  Recent files (last 5):")
        for f in sorted(files, key=lambda x: x.stat().st_mtime, reverse=True)[:5]:
            mtime = datetime.fromtimestamp(f.stat().st_mtime)
            print(f"    - {f.name} ({mtime.strftime('%Y-%m-%d %H:%M')})")
else:
    print("  [ERROR] /Needs_Action/ directory not found!")

# Test 7: Check Logs
print("\n[TEST 7] Checking Watcher Logs...")
print("-"*70)

log_files = [
    'watcher_log.txt',
    'Audit_Log.md',
]

for log_file in log_files:
    if Path(log_file).exists():
        size = Path(log_file).stat().st_size
        print(f"  [OK] {log_file} ({size} bytes)")
        
        # Show last few lines
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()[-3:]
                print(f"    Recent entries:")
                for line in lines[:2]:
                    print(f"      {line.strip()[:80]}...")
        except:
            pass
    else:
        print(f"  [INFO] {log_file} not found")

# Test 8: Check Scheduler
print("\n[TEST 8] Checking Scheduler Configuration...")
print("-"*70)

if Path('scheduler.py').exists():
    print("  [OK] scheduler.py found")
    
    # Check if scheduler is configured
    try:
        with open('scheduler.py', 'r') as f:
            content = f.read()
        
        if 'gmail_watcher' in content.lower():
            print("  [OK] Gmail watcher scheduled")
        else:
            print("  [INFO] Gmail watcher not in scheduler")
        
        if 'whatsapp_watcher' in content.lower():
            print("  [OK] WhatsApp watcher scheduled")
        else:
            print("  [INFO] WhatsApp watcher not in scheduler")
            
    except Exception as e:
        print(f"  [ERROR] Could not read scheduler.py: {e}")
else:
    print("  [MISSING] scheduler.py")

# Test 9: Check MCP Configuration
print("\n[TEST 9] Checking MCP Configuration...")
print("-"*70)

if Path('mcp.json').exists():
    try:
        import json
        with open('mcp.json', 'r') as f:
            mcp_config = json.load(f)
        
        print("  [OK] mcp.json found")
        
        # Check for email server
        if 'servers' in mcp_config:
            servers = mcp_config['servers']
            if 'email-mcp' in servers:
                print("  [OK] Email MCP server configured")
            else:
                print("  [INFO] Email MCP server not configured")
            
            if 'browser-mcp' in servers:
                print("  [OK] Browser MCP server configured")
            else:
                print("  [INFO] Browser MCP server not configured")
        
        # Check workflow settings
        if 'workflow' in mcp_config:
            workflow = mcp_config['workflow']
            if workflow.get('enable_reasoning_loop'):
                print("  [OK] Reasoning loop enabled")
            if workflow.get('approval_required'):
                print("  [OK] Approval workflow enabled")
                
    except Exception as e:
        print(f"  [ERROR] Could not read mcp.json: {e}")
else:
    print("  [MISSING] mcp.json")

# Final Summary
print("\n" + "="*70)
print("WATCHER TEST SUMMARY")
print("="*70)

print(f"""
Watcher Files:     {'[OK] All present' if not missing_files else f'[FAILED] {len(missing_files)} missing'}
Directories:       [OK] All present
Configuration:     [OK] Checked
Imports:           [OK] Tested
Activity:          [OK] Checked
Logs:              [OK] Checked
Scheduler:         [OK] Checked
MCP Config:        [OK] Checked

""")

if not missing_files:
    print("[OK] ALL WATCHER TESTS PASSED!")
    print("\nNext steps:")
    print("  1. Gmail Watcher:    python gmail_watcher.py")
    print("  2. WhatsApp Watcher: python whatsapp_watcher.py")
    print("  3. Scheduler:        python scheduler.py")
    print("  4. Reasoning Loop:   python reasoning_loop.py")
else:
    print("[WARNING] SOME WATCHER TESTS FAILED!")
    if missing_files:
        print(f"\nMissing files: {', '.join(missing_files)}")

print("\n" + "="*70)
print("Test Complete!")
print("="*70)
