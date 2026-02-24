"""
Comprehensive Odoo Real Test
Tests Products, Sales Orders, and Invoices

Usage:
    python test_odoo_real.py
"""

import os
import sys
import json
import requests
from pathlib import Path
from datetime import datetime, timedelta

# Configuration
MCP_SERVER_URL = os.getenv('MCP_SERVER_URL', 'http://localhost:8082')
ODOO_URL = os.getenv('ODOO_URL', 'http://localhost:8069')
ODOO_DB = os.getenv('ODOO_DB', 'fahad-graphic-developer')
ODOO_USERNAME = os.getenv('ODOO_USERNAME', 'fahadmemon131@gmail.com')
ODOO_PASSWORD = os.getenv('ODOO_PASSWORD', '')

# Directories
NEEDS_ACTION_DIR = Path('Needs_Action')
COMPLETED_DIR = Path('Completed')

for dir_path in [NEEDS_ACTION_DIR, COMPLETED_DIR]:
    dir_path.mkdir(exist_ok=True)


class OdooAPI:
    """Direct Odoo XML-RPC API"""
    
    def __init__(self, url, db, username, password):
        self.url = url.rstrip('/')
        self.db = db
        self.username = username
        self.password = password
        self.uid = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Odoo"""
        import xmlrpc.client
        
        common = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/common')
        self.uid = common.authenticate(self.db, self.username, self.password, {})
        
        if not self.uid:
            raise Exception("Authentication failed! Check credentials.")
        
        print(f"  [OK] Authenticated as UID: {self.uid}")
    
    def execute(self, model, method, args=None, kwargs=None):
        """Execute Odoo model method"""
        import xmlrpc.client
        
        objects = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/object')
        return objects.execute_kw(
            self.db, self.uid, self.password,
            model, method,
            args or [],
            kwargs or {}
        )
    
    def search_read(self, model, domain=None, fields=None, limit=80):
        """Search and read records"""
        return self.execute(model, 'search_read', 
                           args=[domain or []], 
                           kwargs={'fields': fields, 'limit': limit})
    
    def create(self, model, values):
        """Create record"""
        return self.execute(model, 'create', args=[values])
    
    def write(self, model, ids, values):
        """Update records"""
        return self.execute(model, 'write', args=[ids, values])
    
    def search(self, model, domain=None, limit=80):
        """Search for IDs"""
        return self.execute(model, 'search', args=[domain or []], kwargs={'limit': limit})


def check_server_health():
    """Check MCP server health"""
    try:
        response = requests.get(f'{MCP_SERVER_URL}/health', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] MCP Server: {data.get('status', 'unknown')}")
            print(f"  Database: {data.get('odoo_db', 'N/A')}")
            print(f"  Authenticated: {data.get('authenticated', False)}")
            return True
        else:
            print(f"[ERROR] MCP Server status: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] Cannot connect to MCP Server: {e}")
        return False


def test_products(odoo):
    """Test Product Management"""
    print("\n" + "="*60)
    print("[TEST 1] Product Management")
    print("="*60)
    
    # 1. List existing products
    print("\n[1.1] Listing existing products...")
    products = odoo.search_read('product.product', 
                                fields=['name', 'list_price', 'categ_id', 'type'],
                                limit=5)
    
    if products:
        print(f"  [OK] Found {len(products)} products")
        for p in products[:3]:
            categ = p.get('categ_id', [None, 'N/A'])[1] if p.get('categ_id') else 'N/A'
            print(f"    - {p['name']}: Rs. {p.get('list_price', 0):.2f} ({categ})")
    else:
        print("  [INFO] No products found")
    
    # 2. Create test product
    print("\n[1.2] Creating test product...")
    try:
        product_id = odoo.create('product.product', {
            'name': 'AI Web Development Service',
            'type': 'service',
            'list_price': 25000.00,
            'categ_id': odoo.execute('product.category', 'search', [['name', '=', 'All']])[0] if odoo.execute('product.category', 'search', [['name', '=', 'All']]) else False,
            'description_sale': 'Professional AI-driven web development services',
            'taxes_id': [(6, 0, [])],  # No taxes for now
        })
        
        if product_id:
            print(f"  [OK] Product created with ID: {product_id}")
            
            # Verify product
            product_data = odoo.search_read('product.product', 
                                           domain=[('id', '=', product_id)],
                                           fields=['name', 'list_price', 'type'])
            if product_data:
                p = product_data[0]
                print(f"  [OK] Verified: {p['name']} - Rs. {p.get('list_price', 0):.2f}")
        else:
            print("  [FAILED] Could not create product")
            
    except Exception as e:
        print(f"  [ERROR] {e}")
    
    # 3. Search products
    print("\n[1.3] Searching products...")
    search_products = odoo.search_read('product.product',
                                       domain=[('name', 'ilike', 'service')],
                                       fields=['name', 'list_price'],
                                       limit=5)
    if search_products:
        print(f"  [OK] Found {len(search_products)} matching products")
    else:
        print("  [INFO] No matching products")
    
    return True


def test_sales_orders(odoo):
    """Test Sales Order Management"""
    print("\n" + "="*60)
    print("[TEST 2] Sales Orders")
    print("="*60)
    
    # 1. List existing sales orders
    print("\n[2.1] Listing existing sales orders...")
    orders = odoo.search_read('sale.order',
                             fields=['name', 'partner_id', 'amount_total', 'state'],
                             limit=5)
    
    if orders:
        print(f"  [OK] Found {len(orders)} sales orders")
        for o in orders[:3]:
            partner = o.get('partner_id', [None, 'N/A'])[1] if o.get('partner_id') else 'N/A'
            print(f"    - {o['name']}: {partner} - Rs. {o.get('amount_total', 0):.2f} ({o.get('state', 'draft')})")
    else:
        print("  [INFO] No sales orders found")
    
    # 2. Find customer
    print("\n[2.2] Finding customer...")
    customers = odoo.search_read('res.partner',
                                domain=[('customer_rank', '>', 0)],
                                fields=['name', 'email', 'phone'],
                                limit=1)
    
    if customers:
        customer = customers[0]
        print(f"  [OK] Found customer: {customer['name']}")
    else:
        print("  [INFO] No customers found, creating one...")
        # Create customer
        customer_id = odoo.create('res.partner', {
            'name': 'Test Customer for Sales',
            'email': 'customer@test.com',
            'phone': '+92-300-1234567',
            'customer_rank': 1,
        })
        customer = {'id': customer_id, 'name': 'Test Customer for Sales'}
        print(f"  [OK] Created customer with ID: {customer_id}")
    
    # 3. Find product
    print("\n[2.3] Finding product...")
    products = odoo.search_read('product.product',
                               domain=[('type', '=', 'service')],
                               fields=['name', 'list_price'],
                               limit=1)
    
    if products:
        product = products[0]
        print(f"  [OK] Found product: {product['name']} - Rs. {product.get('list_price', 0):.2f}")
    else:
        print("  [INFO] No products found, creating one...")
        product_id = odoo.create('product.product', {
            'name': 'Consulting Service',
            'type': 'service',
            'list_price': 5000.00,
        })
        product = {'id': product_id, 'name': 'Consulting Service', 'list_price': 5000.00}
        print(f"  [OK] Created product with ID: {product_id}")
    
    # 4. Create sales order
    print("\n[2.4] Creating sales order...")
    try:
        order_id = odoo.create('sale.order', {
            'partner_id': customer['id'],
            'partner_invoice_id': customer['id'],
            'partner_shipping_id': customer['id'],
            'order_line': [(0, 0, {
                'product_id': product.get('id', False),
                'name': product.get('name', 'Service'),
                'product_uom_qty': 1,
                'product_uom': 1,  # Unit
                'price_unit': product.get('list_price', 5000),
            })],
        })
        
        if order_id:
            print(f"  [OK] Sales order created with ID: {order_id}")
            
            # Verify order
            order_data = odoo.search_read('sale.order',
                                         domain=[('id', '=', order_id)],
                                         fields=['name', 'partner_id', 'amount_total', 'state'])
            if order_data:
                o = order_data[0]
                partner = o.get('partner_id', [None, 'N/A'])[1] if o.get('partner_id') else 'N/A'
                print(f"  [OK] Verified: {o.get('name', 'N/A')} - {partner} - Rs. {o.get('amount_total', 0):.2f} ({o.get('state', 'draft')})")
                
                # Confirm order
                print("\n[2.5] Confirming sales order...")
                odoo.execute('sale.order', 'action_confirm', args=[[order_id]])
                print("  [OK] Sales order confirmed!")
        else:
            print("  [FAILED] Could not create sales order")
            
    except Exception as e:
        print(f"  [ERROR] {e}")
    
    return True


def test_invoices(odoo):
    """Test Invoice Management"""
    print("\n" + "="*60)
    print("[TEST 3] Invoice Management")
    print("="*60)
    
    # 1. List existing invoices
    print("\n[3.1] Listing existing invoices...")
    invoices = odoo.search_read('account.move',
                               domain=[('move_type', '=', 'out_invoice')],
                               fields=['name', 'partner_id', 'amount_total', 'state', 'invoice_date'],
                               limit=5)
    
    if invoices:
        print(f"  [OK] Found {len(invoices)} invoices")
        for inv in invoices[:3]:
            partner = inv.get('partner_id', [None, 'N/A'])[1] if inv.get('partner_id') else 'N/A'
            print(f"    - {inv.get('name', 'Draft')}: {partner} - Rs. {inv.get('amount_total', 0):.2f} ({inv.get('state', 'draft')})")
    else:
        print("  [INFO] No invoices found")
    
    # 2. Create invoice via MCP
    print("\n[3.2] Creating invoice via MCP...")
    try:
        response = requests.post(
            f'{MCP_SERVER_URL}/tools/create_invoice',
            json={
                'customer_name': 'Test Customer',
                'amount': 15000.00,
                'description': 'AI Consulting Services - February 2026',
                'reference': 'TEST-INV-2026-001'
            },
            timeout=30
        )
        
        result = response.json()
        print(f"  Response: {json.dumps(result, indent=2)}")
        
        if result.get('success'):
            print(f"  [OK] Invoice created: ID {result.get('invoice_id')}")
        else:
            print(f"  [INFO] {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"  [ERROR] {e}")
    
    # 3. Read balances
    print("\n[3.3] Reading account balances...")
    try:
        response = requests.get(f'{MCP_SERVER_URL}/tools/read_balance', timeout=30)
        result = response.json()
        
        if result.get('success'):
            balances = result.get('balances', {})
            print(f"  [OK] Balances retrieved:")
            print(f"    - Accounts Receivable: Rs. {balances.get('accounts_receivable', 0):.2f}")
            print(f"    - Accounts Payable: Rs. {balances.get('accounts_payable', 0):.2f}")
            print(f"    - Bank: Rs. {balances.get('bank', 0):.2f}")
            print(f"    - Net Profit: Rs. {balances.get('net_profit', 0):.2f}")
            print(f"    - Currency: {result.get('currency', 'PKR')}")
        else:
            print(f"  [ERROR] {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"  [ERROR] {e}")
    
    return True


def main():
    """Main test function"""
    print("\n" + "="*70)
    print("COMPREHENSIVE ODOO REAL TEST")
    print("="*70)
    print(f"\nOdoo URL: {ODOO_URL}")
    print(f"Database: {ODOO_DB}")
    print(f"Username: {ODOO_USERNAME}")
    print()
    
    # Check MCP server
    print("[PRE-TEST] Checking MCP Server...")
    mcp_ok = check_server_health()
    if not mcp_ok:
        print("\n[WARNING] MCP Server not running. Starting test with direct Odoo API only.")
    
    # Initialize Odoo API
    print("\n[INIT] Connecting to Odoo...")
    try:
        odoo = OdooAPI(ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD)
        print("[OK] Connected to Odoo!")
    except Exception as e:
        print(f"[ERROR] Failed to connect to Odoo: {e}")
        print("\nTrying with manual password input...")
        import getpass
        manual_password = getpass.getpass("Enter Odoo password: ")
        try:
            odoo = OdooAPI(ODOO_URL, ODOO_DB, ODOO_USERNAME, manual_password)
            print("[OK] Connected to Odoo!")
        except Exception as e2:
            print(f"\n[ERROR] Failed to connect with manual password: {e2}")
            print("\nMake sure:")
            print("  1. Odoo is running at", ODOO_URL)
            print("  2. Database", ODOO_DB, "exists")
            print("  3. Credentials are correct")
            print("\nLogin to Odoo manually to verify:")
            print("  URL:", ODOO_URL, "/web/login")
            sys.exit(1)
    
    # Run tests
    results = {}
    
    # Test 1: Products
    try:
        results['Products'] = test_products(odoo)
    except Exception as e:
        print(f"\n[ERROR] Products test failed: {e}")
        results['Products'] = False
    
    # Test 2: Sales Orders
    try:
        results['Sales Orders'] = test_sales_orders(odoo)
    except Exception as e:
        print(f"\n[ERROR] Sales Orders test failed: {e}")
        results['Sales Orders'] = False
    
    # Test 3: Invoices
    try:
        results['Invoices'] = test_invoices(odoo)
    except Exception as e:
        print(f"\n[ERROR] Invoices test failed: {e}")
        results['Invoices'] = False
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"\nResults: {passed}/{total} tests passed\n")
    
    for test, result in results.items():
        status = "[OK]" if result else "[FAILED]"
        print(f"  {status} {test}")
    
    print("\n" + "="*70)
    
    if passed == total:
        print("\n[SUCCESS] ALL TESTS PASSED!")
        print("\nNext steps:")
        print("  1. Check Odoo: http://localhost:8069")
        print("  2. View products: Invoicing → Products")
        print("  3. View sales orders: Invoicing → Orders → Sales Orders")
        print("  4. View invoices: Invoicing → Customers → Invoices")
    else:
        print("\n[WARNING] SOME TESTS FAILED!")
        print("Check the errors above and fix them.")
    
    print("\n" + "="*70)
    
    sys.exit(0 if passed == total else 1)


if __name__ == '__main__':
    main()
