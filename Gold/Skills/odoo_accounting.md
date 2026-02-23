# Agent Skill: Odoo Accounting Integration

## Skill ID: `odoo_accounting`

**Version:** 1.0  
**Created:** 2026-02-23  
**Author:** AI Digital FTE  
**Dependencies:** MCP Odoo Server (`mcp_odoo_server.py`), Odoo 19 Community (self-hosted)

---

## Purpose

Automate accounting operations by integrating with self-hosted Odoo 19 Community Edition. Create draft invoices, search partners, post invoices (with approval), and read financial balances—all while maintaining Human-in-the-Loop (HITL) for sensitive financial actions.

---

## Trigger Conditions

- Invoice creation request detected in `/Needs_Action/` (email, WhatsApp, file)
- Payment inquiry from customer/vendor
- Monthly balance report request
- Manual invocation: `python reasoning_loop.py --skill=odoo_accounting`

---

## Input

- `/Needs_Action/` files containing invoice requests
- Email/WhatsApp messages with keywords: "invoice", "bill", "payment", "balance"
- Direct API calls to MCP Odoo server

---

## Output

- Draft invoices created in Odoo (`account.move` in "draft" state)
- Approval files in `/Pending_Approval/INVOICE_*.md`
- Balance reports in `/Reports/`
- Status updates in `/Audit_Log.md`

---

## MCP Server Configuration

### Environment Variables

Create `.env` file in project root:

```bash
# Odoo Connection Settings
ODOO_URL=http://localhost:8069
ODOO_DB=my_business_db
ODOO_USERNAME=mcp@yourbusiness.local
ODOO_PASSWORD=YourSecurePassword123
ODOO_API_KEY=

# MCP Server Settings
MCP_ODOO_PORT=8082
MCP_ODOO_HOST=localhost
```

### Start MCP Odoo Server

```bash
# Load environment and start server
python mcp_odoo_server.py
```

Server runs on: `http://localhost:8082`

---

## Available Tools (MCP Endpoints)

| Tool | Method | Endpoint | Description | Approval Required |
|------|--------|----------|-------------|-------------------|
| `create_invoice` | POST | `/tools/create_invoice` | Create draft customer invoice | No (draft only) |
| `search_partners` | POST | `/tools/search_partners` | Search customers/vendors | No |
| `post_invoice` | POST | `/tools/post_invoice` | Confirm/post draft invoice | **Yes** |
| `read_balance` | GET | `/tools/read_balance` | Get account balances | No |
| `get_invoice` | GET | `/tools/get_invoice` | Get invoice details | No |
| `list_invoices` | GET | `/tools/list_invoices` | List invoices with filters | No |

---

## Procedure

### Step 1: Detect Invoice Request

Scan `/Needs_Action/` for files containing:
- Keywords: "invoice", "bill", "payment due", "send invoice"
- Email subject patterns: "Invoice Request", "Billing", "Payment"
- WhatsApp messages with invoice-related content

**Classification:**
```python
INVOICE_KEYWORDS = ['invoice', 'bill', 'payment', 'amount due', 'send invoice', 'create bill']
BALANCE_KEYWORDS = ['balance', 'financial report', 'accounts', 'receivable', 'payable']
```

### Step 2: Extract Invoice Details

Parse the request to extract:

| Field | Source | Required |
|-------|--------|----------|
| Customer Name/ID | Email body, WhatsApp message | Yes |
| Amount | Email body, attachment | Yes |
| Description | Email subject/body | Yes |
| Invoice Date | Email date or specified | No (defaults to today) |
| Due Date | Specified or terms | No (defaults to +30 days) |
| Reference | Email subject | No |

### Step 3: Search/Create Customer

```python
# Search for existing customer
response = requests.post('http://localhost:8082/tools/search_partners', json={
    "name": customer_name,
    "partner_type": "customer",
    "limit": 1
})

if response.json()['count'] == 0:
    # Customer not found - flag for manual creation
    create_approval_request("New customer needs to be created in Odoo")
```

### Step 4: Create Draft Invoice

```python
# Create draft invoice in Odoo
response = requests.post('http://localhost:8082/tools/create_invoice', json={
    "customer_name": customer_name,
    "amount": amount,
    "description": description,
    "invoice_date": invoice_date,
    "due_date": due_date,
    "reference": reference
})

invoice_data = response.json()
```

### Step 5: Create Approval File

Create `/Pending_Approval/INVOICE_{invoice_id}.md`:

```markdown
# Invoice Approval Request

**Created:** 2026-02-23 10:30:00  
**Odoo Invoice ID:** 789  
**Invoice Number:** INV/2026/0001 (draft)

## Invoice Details

| Field | Value |
|-------|-------|
| Customer | ABC Corporation |
| Amount | $1,000.00 |
| Description | Web Development Services - February 2026 |
| Invoice Date | 2026-02-23 |
| Due Date | 2026-03-23 |
| Reference | PROJ-2026-001 |
| State | Draft |

## Source Request

- **File:** email_Invoice_Request_ABC_Corp_20260223.md
- **From:** client@abccorp.com
- **Received:** 2026-02-23 09:15:00

## Actions Required

- [ ] **Review invoice details** - Verify amount and description
- [ ] **Approve for posting** - Move to /Approved to post in Odoo
- [ ] **Send to customer** - Email invoice after posting

## Approval Instructions

1. Review the invoice details above
2. If correct, move this file to `/Approved/`
3. The system will post the invoice in Odoo and email to customer
4. If changes needed, edit this file and add comments

---

*Created by odoo_accounting skill*
```

### Step 6: Wait for Approval

- File remains in `/Pending_Approval/` until human reviews
- Human moves file to `/Approved/` to authorize posting
- System posts invoice in Odoo and sends to customer

### Step 7: Post Invoice (After Approval)

```python
# Post the invoice (only after approval)
response = requests.post('http://localhost:8082/tools/post_invoice', json={
    "invoice_id": invoice_id
})

if response.json()['success']:
    # Send email to customer
    send_invoice_email(invoice_id, customer_email)
    
    # Move to Completed
    move_to_completed(invoice_approval_file)
```

---

## Request Templates

### Invoice Request Format (for /Needs_Action files)

```markdown
# Invoice Request

**Customer:** [Customer Name]
**Amount:** [Amount in PKR/USD]
**Description:** [Service/Product description]
**Due Date:** [Optional: YYYY-MM-DD]
**Reference:** [Optional: Project/Order reference]

---

[Additional notes or context]
```

### Example Email Detection

```
Subject: Invoice Request - ABC Corp Project

Hi Team,

Please create an invoice for ABC Corporation:
- Amount: $2,500
- Service: Website Redesign - Final Payment
- Due: 30 days
- Reference: ABC-WEB-2026

Thanks,
Sales Team
```

**Parsed as:**
```json
{
    "customer_name": "ABC Corporation",
    "amount": 2500,
    "description": "Website Redesign - Final Payment",
    "due_date": "2026-03-25",
    "reference": "ABC-WEB-2026"
}
```

---

## Company Handbook Compliance

| Rule | Implementation |
|------|----------------|
| **Efficiency First** | Automated draft creation, manual approval only for posting |
| **Data Integrity** | All invoices logged in Odoo with audit trail |
| **Security** | Credentials via environment variables, no hardcoding |
| **Transparency** | Approval files in `/Pending_Approval/` with full details |
| **Proactivity** | Auto-detect invoice requests from emails/WhatsApp |
| **Polite Tone** | All customer communications maintain professionalism |
| **Payment Flag** | All invoices require approval before posting |
| **Urgent Priority** | Invoices with "urgent" keyword prioritized |

---

## Error Handling

| Error | Action |
|-------|--------|
| Odoo connection failed | Log error, create task for manual review, notify admin |
| Customer not found | Create approval request for new customer creation |
| Invalid amount format | Flag for manual correction, move to `/Needs_Action/Errors/` |
| Duplicate invoice detected | Alert user, provide link to existing invoice |
| Posting failed | Keep in `/Pending_Approval/`, add error details, retry option |

---

## Usage Examples

### Example 1: Create Invoice from Email

**Input:** `/Needs_Action/email_Invoice_Request_ABC_Corp_20260223.md`

**Skill Execution:**
```bash
python reasoning_loop.py --skill=odoo_accounting
```

**Output:**
- Draft invoice created in Odoo (ID: 789)
- Approval file: `/Pending_Approval/INVOICE_789.md`
- Log entry in `Audit_Log.md`

### Example 2: Check Account Balance

**Input:** `/Needs_Action/email_Balance_Request_20260223.md`

**Skill Execution:**
```bash
curl http://localhost:8082/tools/read_balance
```

**Output:**
```json
{
    "success": true,
    "balances": {
        "accounts_receivable": 15000.00,
        "accounts_payable": 5000.00,
        "bank": 25000.00,
        "net_profit": 35000.00
    },
    "currency": "USD"
}
```

### Example 3: Search Customer Before Invoice

**Input:** WhatsApp message "Send invoice to Muhammad Ahmed for consulting"

**Skill Execution:**
```bash
curl -X POST http://localhost:8082/tools/search_partners \
  -H "Content-Type: application/json" \
  -d '{"name": "Muhammad Ahmed", "partner_type": "customer"}'
```

**Output:**
```json
{
    "success": true,
    "count": 1,
    "partners": [
        {
            "id": 45,
            "name": "Muhammad Ahmed Enterprises",
            "email": "muhammad@ahmed.com",
            "phone": "+92-300-1234567",
            "is_customer": true
        }
    ]
}
```

---

## Integration with Approval Workflow

### File Movement Pattern

```
/Needs_Action/invoice_request.md
       ↓ (detected by skill)
[Create draft in Odoo]
       ↓
/Pending_Approval/INVOICE_{id}.md
       ↓ (human moves to Approved)
[Post invoice in Odoo]
[Send email to customer]
       ↓
/Completed/INVOICE_{id}_posted.md
```

### Approval File States

| Location | State | Action |
|----------|-------|--------|
| `/Pending_Approval/` | Awaiting Review | Human must review and approve |
| `/Approved/` | Approved | System will post and send |
| `/Completed/` | Executed | Invoice posted and sent |
| `/Rejected/` | Rejected | Invoice cancelled, reason logged |

---

## Testing

### Test Without Real Odoo (Mock Mode)

```bash
# Set mock mode
export ODOO_MOCK=true

# Run skill - will log actions instead of API calls
python reasoning_loop.py --skill=odoo_accounting --mock
```

### Test With Real Odoo

```bash
# 1. Ensure Odoo is running
# 2. Start MCP server
python mcp_odoo_server.py

# 3. Create test invoice request
echo "Invoice Request
Customer: Test Customer
Amount: 100
Description: Test Invoice" > Needs_Action/test_invoice.md

# 4. Run skill
python reasoning_loop.py --skill=odoo_accounting

# 5. Check results
cat Pending_Approval/INVOICE_*.md
```

---

## Audit Trail

All actions logged in `Audit_Log.md`:

```markdown
## 2026-02-23 10:30:00 - Odoo Accounting Skill

- **Action:** Invoice Created
- **Customer:** ABC Corporation
- **Amount:** $1,000.00
- **Odoo ID:** 789
- **Invoice Number:** INV/2026/0001
- **State:** Draft
- **Approval File:** /Pending_Approval/INVOICE_789.md
- **Status:** Awaiting Approval
```

---

## Future Enhancements

- [ ] Automatic customer creation (with approval)
- [ ] Multi-currency support
- [ ] Recurring invoice automation
- [ ] Payment reconciliation
- [ ] Financial report generation (PDF)
- [ ] Email invoice delivery automation
- [ ] WhatsApp invoice delivery
- [ ] Payment reminder automation

---

## Troubleshooting

### "Authentication failed"
```bash
# Check credentials
echo $ODOO_USERNAME
echo $ODOO_PASSWORD

# Test connection
curl http://localhost:8069/jsonrpc \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"call","params":{"service":"common","method":"authenticate","args":["my_business_db","mcp@yourbusiness.local","YourPassword",{}]},"id":1}'
```

### "Invoice not created"
```bash
# Check MCP server logs
tail -f mcp_odoo_server.log

# Check Odoo logs
sudo journalctl -u odoo19 -f
```

### "Customer not found"
```bash
# Search manually in Odoo
# Go to: http://localhost:8069
# Apps → Contacts → Search customer name
```

---

*End of Skill Document*
