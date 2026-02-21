import xmlrpc.client
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class OdooConnector:
    """
    Connector class for interacting with Odoo via JSON-RPC
    """
    
    def __init__(self, url: str, db: str, username: str, password: str):
        """
        Initialize the Odoo connector
        
        Args:
            url: Odoo instance URL (e.g., 'http://localhost:8069')
            db: Database name
            username: User email
            password: User password
        """
        self.url = url
        self.db = db
        self.username = username
        self.password = None  # Will be set securely
        
        # Create the connection objects
        self.common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        self.models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
        
        # Authenticate and get user ID
        try:
            self.uid = self.common.authenticate(db, username, password, {})
            if not self.uid:
                raise Exception("Authentication failed")
            self.password = password
            print(f"Successfully connected to Odoo database: {db}")
        except Exception as e:
            print(f"Failed to connect to Odoo: {str(e)}")
            raise
    
    def get_total_outstanding_invoices(self) -> float:
        """
        Get the total amount of outstanding invoices
        
        Returns:
            Total outstanding amount
        """
        try:
            # Search for invoices that are not paid
            invoice_ids = self.models.execute_kw(
                self.db, self.uid, self.password,
                'account.move', 'search',
                [[['state', '=', 'posted'], ['payment_state', '!=', 'paid'], ['move_type', '=', 'out_invoice']]]
            )
            
            if not invoice_ids:
                return 0.0
            
            # Get the total amount for these invoices
            invoices = self.models.execute_kw(
                self.db, self.uid, self.password,
                'account.move', 'read',
                [invoice_ids],
                {'fields': ['amount_total', 'amount_residual']}
            )
            
            total_outstanding = sum(invoice['amount_residual'] for invoice in invoices)
            return round(total_outstanding, 2)
        
        except Exception as e:
            print(f"Error getting outstanding invoices: {str(e)}")
            return 0.0
    
    def get_monthly_revenue(self, month_offset: int = 0) -> float:
        """
        Get revenue for a specific month
        
        Args:
            month_offset: 0 for current month, -1 for last month, etc.
        
        Returns:
            Monthly revenue amount
        """
        try:
            # Calculate the date range for the specified month
            today = datetime.now()
            target_month = today.month + month_offset
            target_year = today.year
            
            # Adjust year if needed
            if target_month > 12:
                target_year += 1
                target_month = target_month - 12
            elif target_month < 1:
                target_year -= 1
                target_month = target_month + 12
            
            # Find the start and end dates of the month
            start_date = datetime(target_year, target_month, 1)
            if target_month == 12:
                end_date = datetime(target_year + 1, 1, 1) - timedelta(days=1)
            else:
                end_date = datetime(target_year, target_month + 1, 1) - timedelta(days=1)
            
            # Search for paid invoices in the specified month
            invoice_ids = self.models.execute_kw(
                self.db, self.uid, self.password,
                'account.move', 'search',
                [[
                    ['state', '=', 'posted'],
                    ['payment_state', '=', 'paid'],
                    ['move_type', '=', 'out_invoice'],
                    ['invoice_date', '>=', start_date.strftime('%Y-%m-%d')],
                    ['invoice_date', '<=', end_date.strftime('%Y-%m-%d')]
                ]]
            )
            
            if not invoice_ids:
                return 0.0
            
            # Get the total amount for these invoices
            invoices = self.models.execute_kw(
                self.db, self.uid, self.password,
                'account.move', 'read',
                [invoice_ids],
                {'fields': ['amount_total']}
            )
            
            monthly_revenue = sum(invoice['amount_total'] for invoice in invoices)
            return round(monthly_revenue, 2)
        
        except Exception as e:
            print(f"Error getting monthly revenue: {str(e)}")
            return 0.0
    
    def create_draft_invoice(self, partner_id: int, lines: List[Dict], invoice_data: Dict = None) -> int:
        """
        Create a draft invoice in Odoo
        
        Args:
            partner_id: Customer ID
            lines: List of invoice line dictionaries
            invoice_data: Additional invoice data
        
        Returns:
            Created invoice ID
        """
        try:
            # Prepare invoice values
            vals = {
                'partner_id': partner_id,
                'move_type': 'out_invoice',
                'state': 'draft',
                'invoice_line_ids': [(0, 0, line) for line in lines]
            }
            
            # Add any additional data
            if invoice_data:
                vals.update(invoice_data)
            
            # Create the invoice
            invoice_id = self.models.execute_kw(
                self.db, self.uid, self.password,
                'account.move', 'create',
                [vals]
            )
            
            print(f"Created draft invoice with ID: {invoice_id}")
            return invoice_id
        
        except Exception as e:
            print(f"Error creating draft invoice: {str(e)}")
            raise
    
    def get_completed_projects(self) -> List[Dict]:
        """
        Get completed projects from the /Done folder or other sources
        
        Returns:
            List of completed project data
        """
        # This would typically read from the /Done folder
        # For now, returning an empty list - this would be implemented
        # based on the actual project file structure
        return []
    
    def search_model(self, model: str, domain: List, fields: List = None) -> List[Dict]:
        """
        Generic method to search any Odoo model
        
        Args:
            model: Model name (e.g., 'res.partner', 'account.move')
            domain: Search domain
            fields: Fields to return
        
        Returns:
            List of records
        """
        try:
            record_ids = self.models.execute_kw(
                self.db, self.uid, self.password,
                model, 'search',
                [domain]
            )
            
            if not record_ids:
                return []
            
            if fields is None:
                fields = ['id']
            
            records = self.models.execute_kw(
                self.db, self.uid, self.password,
                model, 'read',
                [record_ids],
                {'fields': fields}
            )
            
            return records
        
        except Exception as e:
            print(f"Error searching model {model}: {str(e)}")
            return []


# Example usage
def get_odoo_connection():
    """
    Helper function to get Odoo connection using environment variables or config
    """
    # These should be configured in a secure way in production
    odoo_url = os.getenv('ODOO_URL', 'http://fahadmemon.odoo.com')
    odoo_db = os.getenv('ODOO_DB', 'FahadMemon')
    odoo_username = os.getenv('ODOO_USERNAME', 'fahadmemon131@gmail.com')
    odoo_password = os.getenv('ODOO_PASSWORD', '')

    try:
        return OdooConnector(odoo_url, odoo_db, odoo_username, odoo_password)
    except Exception as e:
        print(f"Failed to connect to Odoo: {str(e)}")
        return None


if __name__ == "__main__":
    # Example usage
    try:
        odoo = get_odoo_connection()
        
        # Get financial data
        outstanding = odoo.get_total_outstanding_invoices()
        monthly_rev = odoo.get_monthly_revenue()
        
        print(f"Total Outstanding Invoices: ${outstanding}")
        print(f"Monthly Revenue: ${monthly_rev}")
        
    except Exception as e:
        print(f"Could not connect to Odoo: {str(e)}")