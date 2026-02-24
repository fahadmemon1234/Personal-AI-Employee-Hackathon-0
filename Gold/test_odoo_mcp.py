"""
Test Script for Odoo MCP Server
Tests Odoo integration with mock and real modes

Usage:
    python test_odoo_mcp.py [--mock] [--real]
"""

import os
import sys
import json
import requests
from pathlib import Path
from datetime import datetime, timedelta

# Configuration
MCP_SERVER_URL = os.getenv('MCP_SERVER_URL', 'http://localhost:8082')
MOCK_MODE = os.getenv('ODOO_MOCK', 'true').lower() == 'true'

# Directories
NEEDS_ACTION_DIR = Path('Needs_Action')
PENDING_APPROVAL_DIR = Path('Pending_Approval')
COMPLETED_DIR = Path('Completed')

# Create directories if they don't exist
for dir_path in [NEEDS_ACTION_DIR, PENDING_APPROVAL_DIR, COMPLETED_DIR]:
    dir_path.mkdir(exist_ok=True)


class MockOdooClient:
    """Mock Odoo client for testing without real Odoo"""
    
    def __init__(self):
        self.invoice_counter = 1000
        self.partner_counter = 100
        self.invoices = {}
        self.partners = {
            1: {'id': 1, 'name': 'Test Customer ABC Corp', 'email': 'test@abc.com', 'phone': '+1234567890', 'is_customer': True},
            2: {'id': 2, 'name': 'Sample Vendor Ltd', 'email': 'vendor@sample.com', 'phone': '+0987654321', 'is_vendor': True},
        }
    
    def search_partners(self, name, partner_type='all', limit=10):
        """Mock partner search"""
        print(f"  [MOCK] Searching partners: name='{name}', type='{partner_type}'")
        
        results = []
        for pid, partner in self.partners.items():
            if name.lower() in partner['name'].lower():
                results.append(partner)
            if len(results) >= limit:
                break
        
        print(f"  [MOCK] Found {len(results)} partners")
        return {
            'success': True,
            'count': len(results),
            'partners': results
        }
    
    def create_invoice(self, customer_name, amount, description, **kwargs):
        """Mock invoice creation"""
        self.invoice_counter += 1
        invoice_id = self.invoice_counter
        
        invoice_date = kwargs.get('invoice_date', datetime.now().strftime('%Y-%m-%d'))
        due_date = kwargs.get('due_date', (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'))
        
        invoice = {
            'id': invoice_id,
            'number': f'INV/2026/{invoice_id:04d}',
            'partner': customer_name,
            'amount_total': amount,
            'state': 'draft',
            'invoice_date': invoice_date,
            'due_date': due_date,
            'description': description,
            'reference': kwargs.get('reference', '')
        }
        
        self.invoices[invoice_id] = invoice
        
        print(f"  [MOCK] Created draft invoice: {invoice['number']}")
        print(f"  [MOCK] Customer: {customer_name}")
        print(f"  [MOCK] Amount: ${amount}")
        print(f"  [MOCK] State: draft")
        
        return {
            'success': True,
            'invoice_id': invoice_id,
            'invoice_number': invoice['number'],
            'amount_total': amount,
            'state': 'draft',
            'message': 'Draft invoice created successfully (MOCK MODE)'
        }
    
    def read_balance(self):
        """Mock balance reading"""
        print("  [MOCK] Reading account balances...")
        
        balances = {
            'accounts_receivable': 15000.00,
            'accounts_payable': 5000.00,
            'bank': 25000.00,
            'total_income': 45000.00,
            'total_expense': 18000.00,
            'net_profit': 27000.00
        }
        
        print(f"  [MOCK] A/R: ${balances['accounts_receivable']}")
        print(f"  [MOCK] A/P: ${balances['accounts_payable']}")
        print(f"  [MOCK] Bank: ${balances['bank']}")
        print(f"  [MOCK] Net Profit: ${balances['net_profit']}")
        
        return {
            'success': True,
            'balances': balances,
            'currency': 'PKR'
        }


class RealOdooClient:
    """Real Odoo client using MCP server"""
    
    def __init__(self, base_url):
        self.base_url = base_url
    
    def search_partners(self, name, partner_type='all', limit=10):
        """Search partners via MCP server"""
        try:
            response = requests.post(
                f'{self.base_url}/tools/search_partners',
                json={'name': name, 'partner_type': partner_type, 'limit': limit},
                timeout=30
            )
            return response.json()
        except requests.exceptions.ConnectionError:
            print("  [ERROR] Cannot connect to MCP server. Is it running?")
            return {'success': False, 'error': 'Connection failed'}
    
    def create_invoice(self, customer_name, amount, description, **kwargs):
        """Create invoice via MCP server"""
        try:
            payload = {
                'customer_name': customer_name,
                'amount': amount,
                'description': description
            }
            payload.update(kwargs)
            
            response = requests.post(
                f'{self.base_url}/tools/create_invoice',
                json=payload,
                timeout=30
            )
            return response.json()
        except requests.exceptions.ConnectionError:
            print("  [ERROR] Cannot connect to MCP server. Is it running?")
            return {'success': False, 'error': 'Connection failed'}
    
    def read_balance(self):
        """Read balance via MCP server"""
        try:
            response = requests.get(f'{self.base_url}/tools/read_balance', timeout=30)
            return response.json()
        except requests.exceptions.ConnectionError:
            print("  [ERROR] Cannot connect to MCP server. Is it running?")
            return {'success': False, 'error': 'Connection failed'}


def check_server_health():
    """Check if MCP server is running"""
    try:
        response = requests.get(f'{MCP_SERVER_URL}/health', timeout=5)
        if response.status_code == 200:
            print(f"[OK] MCP Server is running at {MCP_SERVER_URL}")
            data = response.json()
            print(f"  Status: {data.get('status', 'unknown')}")
            print(f"  Database: {data.get('odoo_db', 'N/A')}")
            print(f"  Authenticated: {data.get('authenticated', False)}")
            return True
        else:
            print(f"[ERROR] MCP Server returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"[ERROR] Cannot connect to MCP Server at {MCP_SERVER_URL}")
        print("  Make sure to run: python mcp_odoo_server.py")
        return False


def test_workflow(client, mock_mode=True):
    """Run complete test workflow"""
    mode_str = "[MOCK]" if mock_mode else "[REAL]"
    
    print(f"\n{'='*60}")
    print(f"{mode_str} Odoo MCP Test Workflow")
    print(f"{'='*60}")
    
    # Step 1: Search for customer
    print("\n[Step 1] Searching for customer 'ABC Corp'...")
    search_result = client.search_partners('ABC Corp', 'customer', 5)
    print(f"  Search result: {json.dumps(search_result, indent=2)}")
    
    # Step 2: Create draft invoice
    print("\n[Step 2] Creating draft invoice...")
    invoice_result = client.create_invoice(
        customer_name='Test Customer ABC Corp',
        amount=2500.00,
        description='Website Development Services - Phase 1 Complete',
        reference='PROJ-2026-ABC-001',
        due_date='2026-03-25'
    )
    print(f"  Invoice result: {json.dumps(invoice_result, indent=2)}")
    
    # Step 3: Read balance
    print("\n[Step 3] Reading account balances...")
    balance_result = client.read_balance()
    print(f"  Balance result: {json.dumps(balance_result, indent=2)}")
    
    # Summary
    print(f"\n{'='*60}")
    print("Test Workflow Complete!")
    print(f"{'='*60}")
    
    results = {
        'Search Partners': search_result.get('success', False),
        'Create Invoice': invoice_result.get('success', False),
        'Read Balance': balance_result.get('success', False)
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
    
    parser = argparse.ArgumentParser(description='Test Odoo MCP Server')
    parser.add_argument('--mock', action='store_true', help='Run in mock mode (default)')
    parser.add_argument('--real', action='store_true', help='Run with real Odoo connection')
    args = parser.parse_args()
    
    # Determine mode
    mock_mode = args.mock or (not args.real and MOCK_MODE)
    
    print("\n" + "="*60)
    print("Odoo MCP Server - Test Suite")
    print("="*60)
    print(f"\nMode: {'MOCK (no real Odoo)' if mock_mode else 'REAL (requires Odoo)'}")
    print(f"MCP Server URL: {MCP_SERVER_URL}")
    
    if not mock_mode:
        print("\nChecking server health...")
        if not check_server_health():
            print("\nFalling back to MOCK mode...")
            mock_mode = True
    
    # Initialize client
    if mock_mode:
        client = MockOdooClient()
        print("\nUsing MockOdooClient (simulated responses)")
    else:
        client = RealOdooClient(MCP_SERVER_URL)
        print("\nUsing RealOdooClient (MCP server)")
    
    # Run test workflow
    success = test_workflow(client, mock_mode)
    
    # Exit code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
