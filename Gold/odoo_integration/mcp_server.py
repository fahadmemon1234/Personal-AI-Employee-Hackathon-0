"""
MCP Server for Odoo Integration
Provides skills to interact with Odoo accounting system
"""

import asyncio
import json
from typing import Dict, Any
from aiohttp import web, WSMsgType
import logging

from odoo_integration.odoo_connector import OdooConnector, get_odoo_connection

routes = web.RouteTableDef()

class OdooMCPServer:
    def __init__(self):
        self.app = web.Application()
        self.setup_routes()
        self.odoo_conn = None
        
    def setup_routes(self):
        """Setup HTTP routes for the MCP server"""
        self.app.router.add_get('/health', self.health_check)
        self.app.router.add_post('/execute_skill', self.handle_skill_request)
        
    async def health_check(self, request):
        """Health check endpoint"""
        return web.json_response({"status": "healthy", "service": "Odoo MCP Server"})
    
    async def handle_skill_request(self, request):
        """Handle incoming skill requests"""
        try:
            data = await request.json()
            skill_name = data.get('skill_name')
            params = data.get('params', {})
            
            # Connect to Odoo if not already connected
            if not self.odoo_conn:
                try:
                    self.odoo_conn = get_odoo_connection()
                except Exception as e:
                    return web.json_response({
                        "error": f"Could not connect to Odoo: {str(e)}"
                    }, status=500)
            
            # Route to appropriate skill handler
            if skill_name == "get_financial_records":
                result = await self.get_financial_records(params)
            elif skill_name == "sync_invoices":
                result = await self.sync_invoices(params)
            elif skill_name == "get_outstanding_invoices":
                result = await self.get_outstanding_invoices(params)
            elif skill_name == "get_monthly_revenue":
                result = await self.get_monthly_revenue(params)
            else:
                return web.json_response({
                    "error": f"Unknown skill: {skill_name}"
                }, status=400)
                
            return web.json_response({"result": result})
            
        except Exception as e:
            logging.error(f"Error handling skill request: {str(e)}")
            return web.json_response({
                "error": str(e)
            }, status=500)
    
    async def get_financial_records(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get financial records from Odoo"""
        try:
            # This would implement the logic to fetch financial records
            # based on the parameters provided
            records = self.odoo_conn.search_model(
                params.get('model', 'account.move'),
                params.get('domain', []),
                params.get('fields', ['id', 'name', 'amount_total'])
            )
            
            return {
                "records": records,
                "count": len(records),
                "success": True
            }
        except Exception as e:
            logging.error(f"Error getting financial records: {str(e)}")
            raise
    
    async def sync_invoices(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Sync invoices from Done folder to Odoo"""
        try:
            # This would implement the logic to scan the /Done folder
            # and create corresponding invoices in Odoo
            from pathlib import Path
            
            done_folder = Path(params.get('done_folder', './Done'))
            if not done_folder.exists():
                return {
                    "message": f"Done folder does not exist: {done_folder}",
                    "created_invoices": 0,
                    "success": False
                }
            
            # Count processed files
            processed_count = 0
            created_invoices = []
            
            for file_path in done_folder.glob('*'):
                if file_path.is_file():
                    # Process each file and create invoice
                    # This is a simplified implementation
                    # In reality, you'd parse the file content to extract invoice details
                    try:
                        # Extract project details from file name or content
                        project_name = file_path.stem
                        partner_id = params.get('default_partner_id', 1)  # Default customer
                        
                        # Create a sample invoice line
                        line_vals = {
                            'name': f'Service for {project_name}',
                            'quantity': 1,
                            'price_unit': params.get('default_price', 100.0)
                        }
                        
                        # Create the invoice in Odoo
                        invoice_id = self.odoo_conn.create_draft_invoice(
                            partner_id=partner_id,
                            lines=[line_vals],
                            invoice_data={'ref': f'Project-{project_name}'}
                        )
                        
                        created_invoices.append({
                            'file': str(file_path),
                            'invoice_id': invoice_id,
                            'project_name': project_name
                        })
                        processed_count += 1
                        
                    except Exception as e:
                        logging.warning(f"Could not process file {file_path}: {str(e)}")
                        continue
            
            return {
                "message": f"Processed {processed_count} files, created {len(created_invoices)} invoices",
                "created_invoices": created_invoices,
                "success": True
            }
            
        except Exception as e:
            logging.error(f"Error syncing invoices: {str(e)}")
            raise
    
    async def get_outstanding_invoices(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get total outstanding invoices amount"""
        try:
            total_outstanding = self.odoo_conn.get_total_outstanding_invoices()
            
            return {
                "total_outstanding": total_outstanding,
                "currency": params.get('currency', 'USD'),
                "success": True
            }
        except Exception as e:
            logging.error(f"Error getting outstanding invoices: {str(e)}")
            raise
    
    async def get_monthly_revenue(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get monthly revenue"""
        try:
            month_offset = params.get('month_offset', 0)
            monthly_revenue = self.odoo_conn.get_monthly_revenue(month_offset)
            
            return {
                "monthly_revenue": monthly_revenue,
                "currency": params.get('currency', 'USD'),
                "month_offset": month_offset,
                "success": True
            }
        except Exception as e:
            logging.error(f"Error getting monthly revenue: {str(e)}")
            raise
    
    def run(self, host='localhost', port=8080):
        """Run the MCP server"""
        print(f"Starting Odoo MCP Server on {host}:{port}")
        web.run_app(self.app, host=host, port=port)


if __name__ == "__main__":
    server = OdooMCPServer()
    server.run()