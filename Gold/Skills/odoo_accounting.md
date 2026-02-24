# Agent Skill: Odoo Accounting Integration

## Skill ID: `odoo_accounting`

**Purpose:** Automate invoice creation, partner search, and balance queries via Odoo ERP.

## MCP Server

- **Port:** 8082
- **URL:** http://localhost:8082

## Available Tools

| Tool | Endpoint | Method |
|------|----------|--------|
| Create Invoice | `/tools/create_invoice` | POST |
| Search Partners | `/tools/search_partners` | POST |
| Read Balance | `/tools/read_balance` | GET |

## Usage

```bash
# Start server
python mcp_odoo_server.py

# Test
python test_odoo_mcp.py --real
```

## Configuration (.env)

```env
ODOO_URL=http://localhost:8069
ODOO_DB=fahad-graphic-developer
ODOO_USERNAME=fahadmemon131@gmail.com
ODOO_PASSWORD=your_password
```

## Workflow

```
/Needs_Action/invoice_request.md
    ↓
[Create draft in Odoo]
    ↓
/Pending_Approval/INVOICE_*.md
    ↓ (human approval)
[Post invoice]
    ↓
/Completed/
```

---

*For full documentation, see the original skill implementation*
