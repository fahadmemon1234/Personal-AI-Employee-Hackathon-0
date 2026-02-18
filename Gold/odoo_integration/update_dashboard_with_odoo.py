"""
update_dashboard_with_odoo.py
Script to update Dashboard.md with real Odoo financial data
"""

import sys
from pathlib import Path
import re
from datetime import datetime

# Add the project root to the path so we can import modules
sys.path.append(str(Path(__file__).parent))

from odoo_integration.odoo_connector import get_odoo_connection


def update_dashboard_with_odoo_data():
    """
    Update the Dashboard.md file with real Odoo financial data
    """
    try:
        # Connect to Odoo
        odoo_conn = get_odoo_connection()
        
        # Get financial data from Odoo
        total_outstanding = odoo_conn.get_total_outstanding_invoices()
        
        # Get current month revenue
        current_month_revenue = odoo_conn.get_monthly_revenue(0)  # Current month
        
        # Get last month revenue
        last_month_revenue = odoo_conn.get_monthly_revenue(-1)  # Last month
        
        # Get count of outstanding invoices
        outstanding_invoice_ids = odoo_conn.models.execute_kw(
            odoo_conn.db, odoo_conn.uid, odoo_conn.password,
            'account.move', 'search',
            [[['state', '=', 'posted'], ['payment_state', '!=', 'paid'], ['move_type', '=', 'out_invoice']]]
        )
        outstanding_count = len(outstanding_invoice_ids)
        
        # Get latest invoice details if any exist
        latest_invoice_id = None
        latest_invoice_date = None
        latest_invoice_amount = 0.0
        
        if outstanding_invoice_ids:
            # Sort by ID descending to get the latest invoice
            latest_invoice_id = max(outstanding_invoice_ids)
            
            # Get details of the latest invoice
            latest_invoice = odoo_conn.models.execute_kw(
                odoo_conn.db, odoo_conn.uid, odoo_conn.password,
                'account.move', 'read',
                [[latest_invoice_id]],
                {'fields': ['invoice_date', 'amount_total', 'name']}
            )
            
            if latest_invoice:
                latest_inv = latest_invoice[0]
                latest_invoice_date = latest_inv.get('invoice_date', 'N/A')
                latest_invoice_amount = latest_inv.get('amount_total', 0.0)
        
        # Read the current dashboard file
        dashboard_path = Path("Dashboard.md")
        if not dashboard_path.exists():
            print(f"Dashboard.md not found at {dashboard_path}")
            return False
            
        with open(dashboard_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Update the placeholders with actual data
        content = re.sub(r'\[ODOO_OUTSTANDING_AMOUNT\]', f"{total_outstanding:.2f}", content)
        content = re.sub(r'\[ODOO_OUTSTANDING_COUNT\]', str(outstanding_count), content)
        content = re.sub(r'\[ODOO_MONTHLY_REVENUE\]', f"{current_month_revenue:.2f}", content)
        content = re.sub(r'\[ODOO_LAST_MONTH_REVENUE\]', f"{last_month_revenue:.2f}", content)
        content = re.sub(r'\[LATEST_INVOICE_ID\]', str(latest_invoice_id or 'N/A'), content)
        content = re.sub(r'\[LATEST_INVOICE_DATE\]', str(latest_invoice_date or 'N/A'), content)
        content = re.sub(r'\[LATEST_INVOICE_AMOUNT\]', f"{latest_invoice_amount:.2f}", content)
        
        # Update the last updated timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        content = re.sub(r'## Last Updated: \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', f'## Last Updated: {timestamp}', content)
        
        # Write the updated content back to the file
        with open(dashboard_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Dashboard.md updated successfully with Odoo financial data:")
        print(f"- Total Outstanding Amount: ${total_outstanding:.2f}")
        print(f"- Outstanding Invoice Count: {outstanding_count}")
        print(f"- Current Month Revenue: ${current_month_revenue:.2f}")
        print(f"- Last Month Revenue: ${last_month_revenue:.2f}")
        print(f"- Latest Invoice ID: {latest_invoice_id or 'N/A'}")
        print(f"- Latest Invoice Amount: ${latest_invoice_amount:.2f}")
        
        return True
        
    except Exception as e:
        print(f"Error updating dashboard with Odoo data: {str(e)}")
        return False


def update_dashboard_cli():
    """
    Command-line interface for updating dashboard with Odoo data
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Update Dashboard.md with Odoo financial data")
    parser.add_argument("--dashboard-path", default="Dashboard.md", 
                       help="Path to the Dashboard.md file")
    
    args = parser.parse_args()
    
    # Temporarily update the global path if needed
    global dashboard_path
    dashboard_path = args.dashboard_path
    
    success = update_dashboard_with_odoo_data()
    
    if success:
        print("\nDashboard updated successfully!")
    else:
        print("\nFailed to update dashboard.")
        sys.exit(1)


if __name__ == "__main__":
    update_dashboard_cli()