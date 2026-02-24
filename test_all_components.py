"""
Comprehensive Test Suite for All Components
Tests all major functionality and generates test report
"""

import os
import sys
import json
import requests
from pathlib import Path
from datetime import datetime

# Results storage
TEST_RESULTS = {
    'timestamp': datetime.now().isoformat(),
    'tests': [],
    'summary': {
        'total': 0,
        'passed': 0,
        'failed': 0
    }
}

def log_test(name, status, message='', details=None):
    """Log test result"""
    result = {
        'name': name,
        'status': status,  # 'PASS', 'FAIL', 'SKIP'
        'message': message,
        'details': details or {}
    }
    TEST_RESULTS['tests'].append(result)
    TEST_RESULTS['summary']['total'] += 1
    if status == 'PASS':
        TEST_RESULTS['summary']['passed'] += 1
    elif status == 'FAIL':
        TEST_RESULTS['summary']['failed'] += 1
    
    # Use ASCII-safe icons for Windows console compatibility
    icon = '[OK]' if status == 'PASS' else '[FAIL]' if status == 'FAIL' else '[SKIP]'
    print(f"{icon} {name}: {status}")
    if message:
        print(f"   {message}")


# =============================================================================
# Test 1: Module Imports
# =============================================================================
def test_imports():
    print("\n=== Testing Module Imports ===")
    
    modules_to_test = [
        ('watcher', 'Inbox Watcher'),
        ('reasoning_loop', 'Reasoning Loop'),
        ('gmail_watcher', 'Gmail Watcher'),
        ('email_approval_workflow', 'Email Approval Workflow'),
        ('agent_interface', 'Agent Interface'),
        ('mcp_social_server', 'Social Media MCP'),
        ('mcp_email_server', 'Email MCP'),
        ('mcp_browser_server', 'Browser MCP'),
    ]
    
    for module_name, display_name in modules_to_test:
        try:
            __import__(module_name)
            log_test(f"Import: {display_name}", 'PASS', 'Module imported successfully')
        except Exception as e:
            log_test(f"Import: {display_name}", 'FAIL', str(e))


# =============================================================================
# Test 2: Directory Structure
# =============================================================================
def test_directories():
    print("\n=== Testing Directory Structure ===")
    
    required_dirs = [
        'Inbox',
        'Needs_Action',
        'Pending_Approval',
        'Approved',
        'Completed',
        'Plans',
        'Sent',
        'Briefings',
    ]
    
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        exists = dir_path.exists()
        if not exists:
            try:
                dir_path.mkdir(exist_ok=True)
                log_test(f"Directory: {dir_name}", 'PASS', 'Created successfully')
            except Exception as e:
                log_test(f"Directory: {dir_name}", 'FAIL', f'Cannot create: {str(e)}')
        else:
            log_test(f"Directory: {dir_name}", 'PASS', 'Exists')


# =============================================================================
# Test 3: Environment Configuration
# =============================================================================
def test_env_config():
    print("\n=== Testing Environment Configuration ===")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check .env file exists
    env_file = Path('.env')
    if env_file.exists():
        log_test('Config: .env file', 'PASS', 'Environment file exists')
    else:
        log_test('Config: .env file', 'FAIL', '.env file not found')
    
    # Check social config
    social_configured = bool(os.getenv('FACEBOOK_PAGE_ID')) and bool(os.getenv('INSTAGRAM_ACCOUNT_ID'))
    if social_configured:
        log_test('Config: Social Media', 'PASS', 'Facebook and Instagram configured')
    else:
        log_test('Config: Social Media', 'FAIL', 'Missing FACEBOOK_PAGE_ID or INSTAGRAM_ACCOUNT_ID',
                {'facebook_page_id': bool(os.getenv('FACEBOOK_PAGE_ID')),
                 'instagram_account_id': bool(os.getenv('INSTAGRAM_ACCOUNT_ID'))})


# =============================================================================
# Test 4: Social Media MCP Server
# =============================================================================
def test_social_mcp_server():
    print("\n=== Testing Social Media MCP Server ===")
    
    server_url = os.getenv('MCP_SOCIAL_URL', 'http://localhost:8083')
    
    # Check if server is running
    try:
        response = requests.get(f'{server_url}/health', timeout=5)
        if response.status_code == 200:
            data = response.json()
            log_test('Social MCP: Health Check', 'PASS', f'Server running at {server_url}',
                    {'facebook_configured': data.get('facebook_configured'),
                     'instagram_configured': data.get('instagram_configured'),
                     'dry_run': data.get('dry_run')})
        else:
            log_test('Social MCP: Health Check', 'FAIL', f'Server returned {response.status_code}')
    except requests.exceptions.ConnectionError:
        log_test('Social MCP: Health Check', 'FAIL', 'Server not running. Start with: python mcp_social_server.py')
    except Exception as e:
        log_test('Social MCP: Health Check', 'FAIL', str(e))
    
    # Test Instagram post endpoint (dry run)
    try:
        payload = {
            "account_id": "test_account",
            "caption": "Test caption for Instagram #test",
            "media_path": str(Path(__file__).parent / 'test_image.txt'),
            "dry_run": True
        }
        
        # Create test image placeholder
        test_img = Path('test_image.txt')
        test_img.write_text('Test image placeholder')
        
        response = requests.post(f'{server_url}/tools/post_to_instagram', json=payload, timeout=30)
        result = response.json()
        
        if result.get('success'):
            log_test('Social MCP: Instagram Post', 'PASS', 'Instagram post endpoint working (dry run)')
        else:
            log_test('Social MCP: Instagram Post', 'FAIL', result.get('error', 'Unknown error'))
            
    except Exception as e:
        log_test('Social MCP: Instagram Post', 'FAIL', str(e))
    
    # Test Facebook post endpoint (dry run)
    try:
        payload = {
            "page_id": "test_page",
            "message": "Test message for Facebook",
            "dry_run": True
        }
        
        response = requests.post(f'{server_url}/tools/post_to_facebook', json=payload, timeout=30)
        result = response.json()
        
        if result.get('success'):
            log_test('Social MCP: Facebook Post', 'PASS', 'Facebook post endpoint working (dry run)')
        else:
            log_test('Social MCP: Facebook Post', 'FAIL', result.get('error', 'Unknown error'))
            
    except Exception as e:
        log_test('Social MCP: Facebook Post', 'FAIL', str(e))


# =============================================================================
# Test 5: Email MCP Server
# =============================================================================
def test_email_mcp_server():
    print("\n=== Testing Email MCP Server ===")
    
    server_url = os.getenv('MCP_EMAIL_URL', 'http://localhost:8080')
    
    try:
        response = requests.get(f'{server_url}/health', timeout=5)
        if response.status_code == 200:
            data = response.json()
            log_test('Email MCP: Health Check', 'PASS', f'Server running at {server_url}',
                    {'gmail_configured': data.get('gmail_configured')})
        else:
            log_test('Email MCP: Health Check', 'FAIL', f'Server returned {response.status_code}')
    except requests.exceptions.ConnectionError:
        log_test('Email MCP: Health Check', 'FAIL', 'Server not running. Start with: python mcp_email_server.py')
    except Exception as e:
        log_test('Email MCP: Health Check', 'FAIL', str(e))


# =============================================================================
# Test 6: Browser MCP Server
# =============================================================================
def test_browser_mcp_server():
    print("\n=== Testing Browser MCP Server ===")
    
    server_url = os.getenv('MCP_BROWSER_URL', 'http://localhost:8081')
    
    try:
        response = requests.get(f'{server_url}/health', timeout=5)
        if response.status_code == 200:
            data = response.json()
            log_test('Browser MCP: Health Check', 'PASS', f'Server running at {server_url}')
        else:
            log_test('Browser MCP: Health Check', 'FAIL', f'Server returned {response.status_code}')
    except requests.exceptions.ConnectionError:
        log_test('Browser MCP: Health Check', 'FAIL', 'Server not running. Start with: python mcp_browser_server.py')
    except Exception as e:
        log_test('Browser MCP: Health Check', 'FAIL', str(e))


# =============================================================================
# Test 7: Agent Skills
# =============================================================================
def test_agent_skills():
    print("\n=== Testing Agent Skills ===")
    
    skills_dir = Path('.qwen/skills')
    
    if skills_dir.exists():
        log_test('Agent Skills: Directory', 'PASS', 'Skills directory exists')
        
        skills = list(skills_dir.iterdir())
        if skills:
            log_test('Agent Skills: Count', 'PASS', f'{len(skills)} skills found',
                    {'skills': [s.name for s in skills]})
        else:
            log_test('Agent Skills: Count', 'FAIL', 'No skills found')
    else:
        log_test('Agent Skills: Directory', 'FAIL', 'Skills directory not found')


# =============================================================================
# Test 8: Dashboard and Documentation
# =============================================================================
def test_documentation():
    print("\n=== Testing Documentation ===")
    
    docs = [
        ('Dashboard.md', 'Dashboard'),
        ('Company_Handbook.md', 'Company Handbook'),
        ('Audit_Log.md', 'Audit Log'),
        ('README.md', 'README'),
    ]
    
    for doc_file, doc_name in docs:
        doc_path = Path(doc_file)
        if doc_path.exists():
            log_test(f'Doc: {doc_name}', 'PASS', f'{doc_file} exists')
        else:
            log_test(f'Doc: {doc_name}', 'FAIL', f'{doc_file} not found')


# =============================================================================
# Test 9: Reasoning Loop
# =============================================================================
def test_reasoning_loop():
    print("\n=== Testing Reasoning Loop ===")
    
    try:
        from reasoning_loop import ReasoningLoop
        
        loop = ReasoningLoop()
        log_test('Reasoning Loop: Init', 'PASS', 'ReasoningLoop initialized')
        
        # Check Plans directory
        plans_dir = Path('Plans')
        if plans_dir.exists():
            plan_files = list(plans_dir.glob('*.md'))
            log_test('Reasoning Loop: Plans', 'PASS', f'{len(plan_files)} plan files found')
        else:
            log_test('Reasoning Loop: Plans', 'FAIL', 'Plans directory not found')
            
    except Exception as e:
        log_test('Reasoning Loop: Init', 'FAIL', str(e))


# =============================================================================
# Test 10: Agent Interface
# =============================================================================
def test_agent_interface():
    print("\n=== Testing Agent Interface ===")
    
    try:
        from agent_interface import AgentInterface
        
        agent = AgentInterface()
        log_test('Agent Interface: Init', 'PASS', 'AgentInterface initialized')
        
        # Check directories
        dirs_to_check = [
            ('pending_approval_dir', 'Pending Approval'),
            ('approved_dir', 'Approved'),
            ('completed_dir', 'Completed'),
        ]
        
        for dir_attr, dir_name in dirs_to_check:
            if hasattr(agent, dir_attr):
                dir_path = getattr(agent, dir_attr)
                if dir_path.exists():
                    log_test(f'Agent Interface: {dir_name}', 'PASS', 'Directory exists')
                else:
                    log_test(f'Agent Interface: {dir_name}', 'FAIL', 'Directory not found')
            else:
                log_test(f'Agent Interface: {dir_name}', 'FAIL', 'Attribute not found')
                
    except Exception as e:
        log_test('Agent Interface: Init', 'FAIL', str(e))


# =============================================================================
# Generate Test Report
# =============================================================================
def generate_report():
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    total = TEST_RESULTS['summary']['total']
    passed = TEST_RESULTS['summary']['passed']
    failed = TEST_RESULTS['summary']['failed']
    
    print(f"\nTotal Tests: {total}")
    print(f"Passed: {passed} ({(passed/total*100) if total > 0 else 0:.1f}%)")
    print(f"Failed: {failed} ({(failed/total*100) if total > 0 else 0:.1f}%)")
    
    print("\nDetailed Results:")
    print("-"*60)
    
    for test in TEST_RESULTS['tests']:
        icon = '[OK]' if test['status'] == 'PASS' else '[FAIL]' if test['status'] == 'FAIL' else '[SKIP]'
        print(f"{icon} {test['name']}: {test['status']}")
        if test['message']:
            print(f"   {test['message']}")
    
    # Save report to file
    report_file = Path('Test_Report.json')
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(TEST_RESULTS, f, indent=2, ensure_ascii=False)
    
    print(f"\nReport saved to: {report_file}")
    
    return failed == 0


# =============================================================================
# Main
# =============================================================================
def main():
    print("\n" + "="*60)
    print("COMPREHENSIVE COMPONENT TESTING SUITE")
    print("="*60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run all tests
    test_imports()
    test_directories()
    test_env_config()
    test_social_mcp_server()
    test_email_mcp_server()
    test_browser_mcp_server()
    test_agent_skills()
    test_documentation()
    test_reasoning_loop()
    test_agent_interface()
    
    # Generate report
    all_passed = generate_report()
    
    print("\n" + "="*60)
    if all_passed:
        print("[OK] ALL TESTS PASSED!")
    else:
        print("[FAIL] SOME TESTS FAILED - Check report for details")
    print("="*60)
    
    return 0 if all_passed else 1


if __name__ == '__main__':
    sys.exit(main())
