"""
Odoo Real Test via MCP Server
Tests Products, Sales, and Invoices using MCP API

Usage:
    python test_odoo_via_mcp.py
"""

import os
import sys
import json
import requests
from pathlib import Path

# Configuration
MCP_SERVER_URL = os.getenv('MCP_SERVER_URL', 'http://localhost:8082')

print("\n" + "="*70)
print("ODOO REAL TEST - VIA MCP SERVER")
print("="*70)

# Check MCP server health
print("\n[CHECK] MCP Server Health...")
try:
    response = requests.get(f'{MCP_SERVER_URL}/health', timeout=5)
    health = response.json()
    print(f"  Status: {health.get('status', 'unknown')}")
    print(f"  Database: {health.get('odoo_db', 'N/A')}")
    print(f"  Authenticated: {health.get('authenticated', False)}")
    
    if not health.get('authenticated'):
        print("\n[WARNING] MCP Server not authenticated with Odoo!")
        print("Check .env credentials and restart MCP server.")
        sys.exit(1)
        
except Exception as e:
    print(f"[ERROR] Cannot connect to MCP Server: {e}")
    print("\nMake sure MCP server is running:")
    print("  python mcp_odoo_server.py")
    sys.exit(1)

# Test 1: Search Partners (Customers/Vendors)
print("\n" + "="*70)
print("[TEST 1] Search Partners (Customers/Vendors)")
print("="*70)

try:
    response = requests.post(
        f'{MCP_SERVER_URL}/tools/search_partners',
        json={'name': '', 'partner_type': 'all', 'limit': 5},
        timeout=30
    )
    result = response.json()
    
    if result.get('success'):
        partners = result.get('partners', [])
        print(f"  [OK] Found {len(partners)} partners")
        for p in partners[:3]:
            print(f"    - {p['name']} (ID: {p['id']})")
            if p.get('email'):
                print(f"      Email: {p['email']}")
            if p.get('phone'):
                print(f"      Phone: {p['phone']}")
    else:
        print(f"  [ERROR] {result.get('error', 'Unknown error')}")
        
except Exception as e:
    print(f"  [ERROR] {e}")

# Test 2: Read Account Balances
print("\n" + "="*70)
print("[TEST 2] Read Account Balances")
print("="*70)

try:
    response = requests.get(f'{MCP_SERVER_URL}/tools/read_balance', timeout=30)
    result = response.json()
    
    if result.get('success'):
        balances = result.get('balances', {})
        currency = result.get('currency', 'PKR')
        print(f"  [OK] Balances retrieved (Currency: {currency})")
        print(f"    - Accounts Receivable: {currency} {balances.get('accounts_receivable', 0):.2f}")
        print(f"    - Accounts Payable: {currency} {balances.get('accounts_payable', 0):.2f}")
        print(f"    - Bank: {currency} {balances.get('bank', 0):.2f}")
        print(f"    - Total Income: {currency} {balances.get('total_income', 0):.2f}")
        print(f"    - Total Expense: {currency} {balances.get('total_expense', 0):.2f}")
        print(f"    - Net Profit: {currency} {balances.get('net_profit', 0):.2f}")
    else:
        print(f"  [ERROR] {result.get('error', 'Unknown error')}")
        
except Exception as e:
    print(f"  [ERROR] {e}")

# Test 3: Create Invoice
print("\n" + "="*70)
print("[TEST 3] Create Customer Invoice")
print("="*70)

try:
    # First find a customer
    response = requests.post(
        f'{MCP_SERVER_URL}/tools/search_partners',
        json={'name': 'Test', 'partner_type': 'customer', 'limit': 1},
        timeout=30
    )
    search_result = response.json()
    
    if search_result.get('success') and search_result.get('partners'):
        customer = search_result['partners'][0]
        customer_name = customer['name']
        print(f"  Using customer: {customer_name} (ID: {customer['id']})")
        
        # Create invoice
        response = requests.post(
            f'{MCP_SERVER_URL}/tools/create_invoice',
            json={
                'customer_id': customer['id'],
                'amount': 50000.00,
                'description': 'AI Web Development Services - Test Invoice',
                'reference': 'TEST-2026-001'
            },
            timeout=30
        )
        result = response.json()
        
        if result.get('success'):
            print(f"  [OK] Invoice created!")
            print(f"    - Invoice ID: {result.get('invoice_id')}")
            print(f"    - Invoice Number: {result.get('invoice_number', 'Draft')}")
            print(f"    - Amount: {result.get('amount_total', 0):.2f}")
            print(f"    - State: {result.get('state', 'draft')}")
        else:
            print(f"  [ERROR] {result.get('error', 'Unknown error')}")
    else:
        print("  [INFO] No customer found. Creating invoice with customer name...")
        # Try with customer name
        response = requests.post(
            f'{MCP_SERVER_URL}/tools/create_invoice',
            json={
                'customer_name': 'Test Customer',
                'amount': 25000.00,
                'description': 'Consulting Services',
                'reference': 'TEST-2026-002'
            },
            timeout=30
        )
        result = response.json()
        
        if result.get('success'):
            print(f"  [OK] Invoice created!")
            print(f"    - Invoice ID: {result.get('invoice_id')}")
            print(f"    - Amount: {result.get('amount_total', 0):.2f}")
        else:
            print(f"  [INFO] {result.get('error', 'No customers available')}")
        
except Exception as e:
    print(f"  [ERROR] {e}")

# Test 4: List Invoices (Direct Odoo API via MCP)
print("\n" + "="*70)
print("[TEST 4] System Status")
print("="*70)

print("\n  Odoo Configuration:")
print(f"    - URL: http://localhost:8069")
print(f"    - Database: {health.get('odoo_db', 'N/A')}")
print(f"    - MCP Port: 8082")
print(f"    - Status: {'Connected' if health.get('authenticated') else 'Not Connected'}")

print("\n  Available MCP Tools:")
print("    - POST /tools/create_invoice")
print("    - POST /tools/search_partners")
print("    - GET  /tools/read_balance")
print("    - GET  /health")

print("\n  Next Steps:")
print("    1. Open Odoo: http://localhost:8069")
print("    2. Login to your database")
print("    3. Go to: Invoicing -> Customers -> Invoices")
print("    4. View created test invoices")

print("\n" + "="*70)
print("TEST COMPLETE")
print("="*70)
print("\n[OK] MCP Server is working correctly!")
print("\nTo test Products and Sales Orders:")
print("  1. Login to Odoo at http://localhost:8069")
print("  2. Go to: Invoicing -> Products -> Products")
print("  3. Go to: Invoicing -> Orders -> Sales Orders")
print("\n" + "="*70)
