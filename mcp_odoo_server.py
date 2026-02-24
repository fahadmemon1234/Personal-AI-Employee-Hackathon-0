"""
MCP Odoo Server - Accounting Integration
Exposes Odoo JSON-RPC API tools for invoice management, partner search, and balance queries
"""

import os
import json
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('mcp_odoo_server')

# Flask app for MCP server
app = Flask(__name__)
CORS(app)

# Configuration from environment variables
ODOO_CONFIG = {
    'url': os.getenv('ODOO_URL', 'http://localhost:8069'),
    'db': os.getenv('ODOO_DB', 'fahad-graphic-developer'),
    'username': os.getenv('ODOO_USERNAME', 'fahadmemon131@gmail.com'),
    'password': os.getenv('ODOO_PASSWORD', ''),
    'api_key': os.getenv('ODOO_API_KEY', ''),
}

# Session cache for authenticated UID
_odo_session = {
    'uid': None,
    'authenticated_at': None
}


class OdooJSONRPC:
    """Odoo JSON-RPC 2.0 Client for External API Access"""
    
    def __init__(self, config: Dict[str, str]):
        self.url = config['url'].rstrip('/')
        self.db = config['db']
        self.username = config['username']
        self.password = config['password'] or config.get('api_key', '')
        self.session_uid = None
        
    def authenticate(self) -> Optional[int]:
        """Authenticate and get user UID"""
        if _odo_session.get('uid') and _odo_session.get('authenticated_at'):
            from datetime import timedelta
            if datetime.now() - _odo_session['authenticated_at'] < timedelta(hours=1):
                return _odo_session['uid']
        
        try:
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
                uid = result['result']
                _odo_session['uid'] = uid
                _odo_session['authenticated_at'] = datetime.now()
                logger.info(f"Authenticated successfully. UID: {uid}")
                return uid
            else:
                logger.error("Authentication failed - invalid credentials")
                return None
                
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return None
    
    def execute(self, model: str, method: str, args: List = None, kwargs: Dict = None) -> Any:
        """Execute a method on an Odoo model"""
        uid = self.authenticate()
        if not uid:
            raise Exception("Not authenticated. Check credentials.")
        
        endpoint = f"{self.url}/jsonrpc"
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "service": "object",
                "method": "execute_kw",
                "args": [
                    self.db,
                    uid,
                    self.password,
                    model,
                    method,
                    args or [],
                    kwargs or {}
                ]
            },
            "id": 1
        }
        
        headers = {"Content-Type": "application/json"}
        
        try:
            response = requests.post(endpoint, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            if 'error' in result:
                error = result['error']
                logger.error(f"Odoo execute error: {error}")
                raise Exception(f"Odoo Error: {error.get('message', 'Unknown error')}")
            
            return result.get('result')
        except Exception as e:
            logger.error(f"Request failed: {e}")
            raise Exception(f"Connection to Odoo failed: {str(e)}")
    
    def search_read(self, model: str, domain: List = None, fields: List = None, limit: int = 80) -> List[Dict]:
        """Search and read records from a model"""
        return self.execute(model, 'search_read', 
                           args=[domain or []], 
                           kwargs={'fields': fields, 'limit': limit})
    
    def create(self, model: str, values: Dict) -> int:
        """Create a new record"""
        return self.execute(model, 'create', args=[values])
    
    def write(self, model: str, ids: List, values: Dict) -> bool:
        """Update existing records"""
        return self.execute(model, 'write', args=[ids, values])
    
    def search(self, model: str, domain: List = None, limit: int = 80) -> List[int]:
        """Search for record IDs"""
        return self.execute(model, 'search', args=[domain or []], kwargs={'limit': limit})
    
    def read(self, model: str, ids: List, fields: List = None) -> List[Dict]:
        """Read specific records"""
        return self.execute(model, 'read', args=[ids], kwargs={'fields': fields})


# Initialize Odoo client
odoo_client = OdooJSONRPC(ODOO_CONFIG)


# ============================================================================
# MCP Tool Endpoints
# ============================================================================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'mcp-odoo-server',
        'odoo_url': ODOO_CONFIG['url'],
        'odoo_db': ODOO_CONFIG['db'],
        'authenticated': _odo_session.get('uid') is not None,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/tools/create_invoice', methods=['POST'])
def create_invoice():
    """Create a draft customer invoice in Odoo"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        if not data.get('customer_id') and not data.get('customer_name'):
            return jsonify({'success': False, 'error': 'customer_id or customer_name is required'}), 400
        
        if not data.get('amount'):
            return jsonify({'success': False, 'error': 'amount is required'}), 400
        
        # Find customer if name provided
        customer_id = data.get('customer_id')
        if not customer_id and data.get('customer_name'):
            partners = odoo_client.search_read(
                'res.partner',
                domain=[('name', 'ilike', data['customer_name'])],
                fields=['id', 'name'],
                limit=1
            )
            if partners:
                customer_id = partners[0]['id']
            else:
                return jsonify({
                    'success': False, 
                    'error': f"Customer '{data['customer_name']}' not found"
                }), 404
        
        # Prepare invoice line
        invoice_line_vals = {
            'name': data.get('description', 'Services'),
            'price_unit': data.get('amount', 0),
            'quantity': 1,
        }
        
        # Prepare invoice
        invoice_vals = {
            'move_type': 'out_invoice',
            'partner_id': customer_id,
            'invoice_line_ids': [(0, 0, invoice_line_vals)],
            'narration': data.get('description', ''),
        }
        
        if data.get('reference'):
            invoice_vals['ref'] = data['reference']
        
        if data.get('invoice_date'):
            invoice_vals['invoice_date'] = data['invoice_date']
        
        # Create invoice
        invoice_id = odoo_client.create('account.move', invoice_vals)
        
        # Read back the created invoice
        invoice_data = odoo_client.read('account.move', [invoice_id], 
                                        fields=['name', 'amount_total', 'state', 'invoice_date', 'invoice_date_due'])
        
        invoice = invoice_data[0] if invoice_data else {}
        
        # Update due date if provided
        if data.get('due_date') and invoice_id:
            odoo_client.write('account.move', [invoice_id], {
                'invoice_date_due': data['due_date']
            })
        
        logger.info(f"Created invoice {invoice_id} for customer {customer_id}")
        
        return jsonify({
            'success': True,
            'invoice_id': invoice_id,
            'invoice_number': invoice.get('name', 'N/A'),
            'amount_total': invoice.get('amount_total', data.get('amount')),
            'state': invoice.get('state', 'draft'),
            'message': 'Draft invoice created successfully. Requires approval before posting.'
        })
        
    except Exception as e:
        logger.error(f"Error creating invoice: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/tools/search_partners', methods=['POST'])
def search_partners():
    """Search for business partners (customers/vendors) in Odoo"""
    try:
        data = request.get_json() or {}
        
        search_term = data.get('name', '')
        partner_type = data.get('partner_type', 'all')
        limit = min(data.get('limit', 10), 100)
        
        domain = []
        if search_term:
            domain.append(('name', 'ilike', search_term))
        
        if partner_type == 'customer':
            domain.append(('customer_rank', '>', 0))
        elif partner_type == 'vendor':
            domain.append(('supplier_rank', '>', 0))
        
        partners = odoo_client.search_read(
            'res.partner',
            domain=domain,
            fields=['id', 'name', 'email', 'phone', 'street', 'city', 
                    'country_id', 'customer_rank', 'supplier_rank', 'vat'],
            limit=limit
        )
        
        formatted_partners = []
        for p in partners:
            formatted_partners.append({
                'id': p['id'],
                'name': p.get('name', ''),
                'email': p.get('email', ''),
                'phone': p.get('phone') or p.get('mobile', ''),
                'address': f"{p.get('street', '')}, {p.get('city', '')}".strip(','),
                'country': p.get('country_id', [None, ''])[1] if p.get('country_id') else '',
                'vat': p.get('vat', ''),
                'is_customer': p.get('customer_rank', 0) > 0,
                'is_vendor': p.get('supplier_rank', 0) > 0
            })
        
        return jsonify({
            'success': True,
            'count': len(formatted_partners),
            'partners': formatted_partners
        })
        
    except Exception as e:
        logger.error(f"Error searching partners: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/tools/read_balance', methods=['GET'])
def read_balance():
    """Read account balances from Odoo"""
    try:
        account_type = request.args.get('account_type', '')
        partner_id = request.args.get('partner_id', '')
        
        balances = {}
        
        # Get Accounts Receivable balance
        ar_domain = [('account_type', '=', 'asset_receivable')]
        ar_accounts = odoo_client.search_read('account.account', domain=ar_domain, fields=['id'])
        ar_ids = [a['id'] for a in ar_accounts]
        
        if ar_ids:
            ar_lines = odoo_client.search_read(
                'account.move.line',
                domain=[('account_id', 'in', ar_ids), ('parent_state', '=', 'posted')],
                fields=['debit', 'credit', 'balance']
            )
            balances['accounts_receivable'] = sum(line.get('balance', 0) for line in ar_lines)
        
        # Get Accounts Payable balance
        ap_domain = [('account_type', '=', 'liability_payable')]
        ap_accounts = odoo_client.search_read('account.account', domain=ap_domain, fields=['id'])
        ap_ids = [a['id'] for a in ap_accounts]
        
        if ap_ids:
            ap_lines = odoo_client.search_read(
                'account.move.line',
                domain=[('account_id', 'in', ap_ids), ('parent_state', '=', 'posted')],
                fields=['debit', 'credit', 'balance']
            )
            balances['accounts_payable'] = sum(line.get('balance', 0) for line in ap_lines)
        
        # Get Bank/Cash balance
        bank_domain = [('account_type', 'in', ['asset_cash', 'asset_bank'])]
        bank_accounts = odoo_client.search_read('account.account', domain=bank_domain, fields=['id'])
        bank_ids = [a['id'] for a in bank_accounts]
        
        if bank_ids:
            bank_lines = odoo_client.search_read(
                'account.move.line',
                domain=[('account_id', 'in', bank_ids), ('parent_state', '=', 'posted')],
                fields=['debit', 'credit', 'balance']
            )
            balances['bank'] = sum(line.get('balance', 0) for line in bank_lines)
        
        # Get Income accounts
        income_domain = [('account_type', '=', 'income')]
        income_accounts = odoo_client.search_read('account.account', domain=income_domain, fields=['id'])
        income_ids = [a['id'] for a in income_accounts]
        
        if income_ids:
            income_lines = odoo_client.search_read(
                'account.move.line',
                domain=[('account_id', 'in', income_ids), ('parent_state', '=', 'posted')],
                fields=['debit', 'credit', 'balance']
            )
            balances['total_income'] = abs(sum(line.get('balance', 0) for line in income_lines))
        
        # Get Expense accounts
        expense_domain = [('account_type', '=', 'expense')]
        expense_accounts = odoo_client.search_read('account.account', domain=expense_domain, fields=['id'])
        expense_ids = [a['id'] for a in expense_accounts]
        
        if expense_ids:
            expense_lines = odoo_client.search_read(
                'account.move.line',
                domain=[('account_id', 'in', expense_ids), ('parent_state', '=', 'posted')],
                fields=['debit', 'credit', 'balance']
            )
            balances['total_expense'] = abs(sum(line.get('balance', 0) for line in expense_lines))
        
        # Calculate net profit
        balances['net_profit'] = balances.get('total_income', 0) - balances.get('total_expense', 0)
        
        # Get company currency
        company = odoo_client.search_read('res.company', domain=[], fields=['currency_id'], limit=1)
        currency = company[0].get('currency_id', [None, 'USD'])[1] if company else 'USD'
        
        return jsonify({
            'success': True,
            'balances': balances,
            'currency': currency,
            'as_of': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error reading balance: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("MCP Odoo Server - Accounting Integration")
    print("="*60)
    print(f"\nOdoo URL: {ODOO_CONFIG['url']}")
    print(f"Odoo Database: {ODOO_CONFIG['db']}")
    print(f"Username: {ODOO_CONFIG['username']}")
    print("\nAvailable Tools:")
    print("  POST /tools/create_invoice  - Create draft customer invoice")
    print("  POST /tools/search_partners - Search customers/vendors")
    print("  GET  /tools/read_balance    - Get account balances")
    print("  GET  /health                - Health check")
    print("\nStarting server on http://localhost:8082")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=8082, debug=False)
