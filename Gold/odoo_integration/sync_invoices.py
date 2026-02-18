"""
sync_invoices.py
Skill to check the /Done folder for completed project files and automatically create 'Draft Invoice' in Odoo.
"""

import os
import sys
from pathlib import Path
import re
from datetime import datetime
import json

# Add the project root to the path so we can import modules
sys.path.append(str(Path(__file__).parent))

from odoo_integration.odoo_connector import get_odoo_connection, OdooConnector


def extract_project_info_from_filename(filename):
    """
    Extract project information from filename
    Expected format: 'client_project_description_date.ext' or similar
    """
    # Remove extension and split by common separators
    name_part = Path(filename).stem
    parts = re.split(r'[_\- ]+', name_part)
    
    # Simple heuristic to extract client and project info
    # This could be enhanced based on your specific naming convention
    if len(parts) >= 2:
        client = parts[0]  # First part often represents client
        project = '_'.join(parts[1:])  # Remaining parts represent project
    else:
        client = "Unknown Client"
        project = name_part
    
    return {
        "client": client,
        "project": project,
        "filename": filename
    }


def get_partner_id_by_name(odoo_conn, partner_name):
    """
    Find or create a partner (customer) by name
    """
    try:
        # Search for existing partner
        partner_ids = odoo_conn.models.execute_kw(
            odoo_conn.db, odoo_conn.uid, odoo_conn.password,
            'res.partner', 'search',
            [[['name', 'ilike', partner_name]]]
        )
        
        if partner_ids:
            return partner_ids[0]  # Return first match
        
        # If not found, create a new partner
        partner_id = odoo_conn.models.execute_kw(
            odoo_conn.db, odoo_conn.uid, odoo_conn.password,
            'res.partner', 'create',
            [{
                'name': partner_name,
                'is_company': True,
                'customer_rank': 1  # Mark as customer
            }]
        )
        
        print(f"Created new partner: {partner_name} with ID: {partner_id}")
        return partner_id
        
    except Exception as e:
        print(f"Error finding/creating partner {partner_name}: {str(e)}")
        return 1  # Return default partner ID


def process_done_folder(done_folder_path="./Done", default_price_per_project=500.0):
    """
    Process files in the /Done folder and create corresponding invoices in Odoo
    """
    done_path = Path(done_folder_path)
    
    if not done_path.exists():
        print(f"Done folder does not exist: {done_path}")
        # Create the folder if it doesn't exist
        done_path.mkdir(parents=True, exist_ok=True)
        print(f"Created Done folder: {done_path}")
    
    # Connect to Odoo
    try:
        odoo_conn = get_odoo_connection()
    except Exception as e:
        print(f"Could not connect to Odoo: {str(e)}")
        return {"success": False, "error": str(e)}
    
    # Track processing results
    results = {
        "processed_files": [],
        "created_invoices": [],
        "errors": [],
        "summary": {}
    }
    
    # Process each file in the Done folder
    for file_path in done_path.iterdir():
        if file_path.is_file():
            try:
                # Extract project information from the filename
                proj_info = extract_project_info_from_filename(file_path.name)
                
                # Get or create the partner (customer)
                partner_id = get_partner_id_by_name(odoo_conn, proj_info["client"])
                
                # Create invoice lines based on project
                line_vals = [{
                    'name': f'Service for {proj_info["project"]}',
                    'quantity': 1,
                    'price_unit': default_price_per_project,
                    'account_id': 1,  # Default account, should be configured properly
                }]
                
                # Additional invoice data
                invoice_data = {
                    'ref': f'Done-{proj_info["filename"]}',  # Reference based on filename
                    'invoice_date': datetime.now().strftime('%Y-%m-%d'),
                    'narration': f'Invoice created from completed project file: {proj_info["filename"]}'
                }
                
                # Create the draft invoice in Odoo
                invoice_id = odoo_conn.create_draft_invoice(
                    partner_id=partner_id,
                    lines=line_vals,
                    invoice_data=invoice_data
                )
                
                # Record the success
                file_result = {
                    "filename": proj_info["filename"],
                    "client": proj_info["client"],
                    "project": proj_info["project"],
                    "invoice_id": invoice_id,
                    "status": "success"
                }
                
                results["processed_files"].append(file_result)
                results["created_invoices"].append(invoice_id)
                
                print(f"Created invoice {invoice_id} for file: {proj_info['filename']}")
                
            except Exception as e:
                error_msg = f"Error processing file {file_path.name}: {str(e)}"
                print(error_msg)
                results["errors"].append({
                    "filename": file_path.name,
                    "error": str(e),
                    "status": "error"
                })
    
    # Create summary
    results["summary"] = {
        "total_files_processed": len(results["processed_files"]),
        "total_invoices_created": len(results["created_invoices"]),
        "total_errors": len(results["errors"]),
        "timestamp": datetime.now().isoformat()
    }
    
    print(f"\nProcessing Summary:")
    print(f"- Files processed: {results['summary']['total_files_processed']}")
    print(f"- Invoices created: {results['summary']['total_invoices_created']}")
    print(f"- Errors: {results['summary']['total_errors']}")
    
    return results


def sync_invoices_cli():
    """
    Command-line interface for the sync_invoices skill
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Sync invoices from Done folder to Odoo")
    parser.add_argument("--done-folder", default="./Done", help="Path to the Done folder")
    parser.add_argument("--default-price", type=float, default=500.0, 
                       help="Default price per project if not specified in file")
    parser.add_argument("--output-json", action="store_true", 
                       help="Output results in JSON format")
    
    args = parser.parse_args()
    
    results = process_done_folder(
        done_folder_path=args.done_folder,
        default_price_per_project=args.default_price
    )
    
    if args.output_json:
        print(json.dumps(results, indent=2))
    else:
        print(f"\nCompleted processing. Created {results['summary']['total_invoices_created']} invoices.")


if __name__ == "__main__":
    sync_invoices_cli()