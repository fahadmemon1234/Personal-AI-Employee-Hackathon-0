"""
Odoo Customer Creator Script
Creates test customers in Odoo for testing MCP integration
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

ODOO_URL = os.getenv('ODOO_URL', 'http://localhost:8069')
ODOO_DB = os.getenv('ODOO_DB', 'fahad-graphic-developer')
ODOO_USERNAME = os.getenv('ODOO_USERNAME', 'fahadmemon131@gmail.com')
ODOO_PASSWORD = os.getenv('ODOO_PASSWORD', 'memonggc1235Q')

class OdooClient:
    """Simple Odoo Client for creating customers"""
    
    def __init__(self):
        self.url = ODOO_URL
        self.db = ODOO_DB
        self.username = ODOO_USERNAME
        self.password = ODOO_PASSWORD
        self.uid = None
        
    def authenticate(self):
        """Authenticate with Odoo"""
        endpoint = f"{self.url}/jsonrpc"
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "service": "common",
                "method": "authenticate",
                "args": [self.db, self.username, self.password, {}]
            },
            "id": 1
        }
        
        response = requests.post(endpoint, json=payload, timeout=30)
        result = response.json()
        
        if 'result' in result and result['result']:
            self.uid = result['result']
            print(f"✓ Authenticated successfully. UID: {self.uid}")
            return True
        else:
            print(f"✗ Authentication failed!")
            return False
    
    def create_customer(self, name, email, phone="", street="", city="", country=""):
        """Create a customer in Odoo"""
        if not self.uid:
            print("✗ Not authenticated!")
            return None
        
        endpoint = f"{self.url}/jsonrpc"
        
        # Prepare customer data
        customer_vals = {
            'name': name,
            'email': email,
            'customer_rank': 1,  # Mark as customer
            'company_type': 'company',
        }
        
        if phone:
            customer_vals['phone'] = phone
        if street:
            customer_vals['street'] = street
        if city:
            customer_vals['city'] = city
        if country:
            customer_vals['country_id'] = country
        
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "service": "object",
                "method": "execute_kw",
                "args": [
                    self.db,
                    self.uid,
                    self.password,
                    'res.partner',  # Model
                    'create',       # Method
                    [customer_vals] # Args
                ]
            },
            "id": 1
        }
        
        response = requests.post(endpoint, json=payload, timeout=30)
        result = response.json()
        
        if 'result' in result:
            customer_id = result['result']
            print(f"✓ Customer created successfully!")
            print(f"  ID: {customer_id}")
            print(f"  Name: {name}")
            print(f"  Email: {email}")
            return customer_id
        else:
            print(f"✗ Failed to create customer!")
            if 'error' in result:
                print(f"  Error: {result['error']}")
            return None
    
    def search_customers(self, search_term=""):
        """Search for customers"""
        if not self.uid:
            return []
        
        endpoint = f"{self.url}/jsonrpc"
        
        domain = [('customer_rank', '>', 0)]
        if search_term:
            domain.append(('name', 'ilike', search_term))
        
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "service": "object",
                "method": "execute_kw",
                "args": [
                    self.db,
                    self.uid,
                    self.password,
                    'res.partner',
                    'search_read',
                    [domain],
                    {'fields': ['id', 'name', 'email', 'phone'], 'limit': 10}
                ]
            },
            "id": 1
        }
        
        response = requests.post(endpoint, json=payload, timeout=30)
        result = response.json()
        
        if 'result' in result:
            return result['result']
        return []


def main():
    print("\n" + "="*60)
    print("Odoo Customer Creator")
    print("="*60)
    print(f"\nOdoo URL: {ODOO_URL}")
    print(f"Database: {ODOO_DB}")
    print(f"Username: {ODOO_USERNAME}")
    print()
    
    # Initialize client
    client = OdooClient()
    
    # Authenticate
    if not client.authenticate():
        print("\n✗ Authentication failed! Check credentials in .env file")
        return
    
    # Show existing customers
    print("\n[Existing Customers]")
    customers = client.search_customers()
    if customers:
        for c in customers:
            print(f"  - {c['name']} (ID: {c['id']})")
            print(f"    Email: {c.get('email', 'N/A')}")
            print(f"    Phone: {c.get('phone', 'N/A')}")
    else:
        print("  No customers found.")
    
    # Create test customers
    print("\n[Creating Test Customers]")
    
    test_customers = [
        {
            'name': 'Test Customer ABC Corp',
            'email': 'test@abccorp.com',
            'phone': '+92-300-1234567',
            'street': '123 Business Road',
            'city': 'Karachi'
        },
        {
            'name': 'XYZ Technologies',
            'email': 'info@xyztech.com',
            'phone': '+92-321-9876543',
            'street': '456 Tech Park',
            'city': 'Lahore'
        },
        {
            'name': 'Fahad Graphic Design Client',
            'email': 'client@fahadgraphic.com',
            'phone': '+92-333-5556666',
            'street': '789 Design Street',
            'city': 'Islamabad'
        }
    ]
    
    created_ids = []
    for customer in test_customers:
        print(f"\nCreating: {customer['name']}...")
        customer_id = client.create_customer(**customer)
        if customer_id:
            created_ids.append(customer_id)
    
    # Show updated list
    print("\n" + "="*60)
    print("[All Customers]")
    print("="*60)
    customers = client.search_customers()
    if customers:
        for i, c in enumerate(customers, 1):
            print(f"\n{i}. {c['name']}")
            print(f"   ID: {c['id']}")
            print(f"   Email: {c.get('email', 'N/A')}")
            print(f"   Phone: {c.get('phone', 'N/A')}")
    else:
        print("No customers found.")
    
    print("\n" + "="*60)
    print(f"Created {len(created_ids)} new customers")
    print("="*60)
    
    if created_ids:
        print("\n✓ Now you can create invoices for these customers!")
        print("\nTest invoice creation:")
        print("  python test_odoo_mcp.py --real")
        print("\nOr use MCP API:")
        print("  Invoke-RestMethod -Uri http://localhost:8082/tools/create_invoice ...")


if __name__ == '__main__':
    main()
