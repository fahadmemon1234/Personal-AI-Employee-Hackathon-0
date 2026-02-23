# Odoo MCP Integration - Testing Guide

## Quick Start

### Test Without Installing Odoo (Mock Mode)

```bash
# Navigate to Gold directory
cd "D:\Fahad Project\AI-Driven\Personal-AI-Employee-Hackathon-0\Gold"

# Run test in mock mode (no Odoo required)
python test_odoo_mcp.py --mock
```

**Expected Output:**
```
============================================================
Odoo MCP Server - Test Suite
============================================================

Mode: MOCK (no real Odoo)
MCP Server URL: http://localhost:8082

Using MockOdooClient (simulated responses)

============================================================
[MOCK] Odoo MCP Test Workflow
============================================================

[Step 1] Creating test invoice request...
✓ Created test invoice request: Needs_Action\email_Invoice_Request_ABC_Corp_20260223_100000.md

[Step 2] Searching for customer 'ABC Corp'...
  [MOCK] Searching partners: name='ABC Corp', type='customer'
  [MOCK] Found 1 partners
  Search result: {"success": true, "count": 1, "partners": [...]}

[Step 3] Creating draft invoice...
  [MOCK] Created draft invoice: INV/2026/1001
  [MOCK] Customer: Test Customer ABC Corp
  [MOCK] Amount: $2500.0
  [MOCK] State: draft
  Invoice result: {"success": true, "invoice_id": 1001, ...}

[Step 4] Creating approval file...
✓ Created approval file: Pending_Approval\INVOICE_1001.md

[Step 5] Simulating approval process (MOCK)...

[Step 6] Posting invoice...
  [MOCK] Posted invoice: INV/2026/1001
  [MOCK] New state: posted

[Step 7] Reading account balances...
  [MOCK] Reading account balances...
  [MOCK] A/R: $15000.0
  [MOCK] A/P: $5000.0
  [MOCK] Bank: $25000.0
  [MOCK] Net Profit: $27000.0

============================================================
Test Workflow Complete!
============================================================
```

---

## Full Test with Real Odoo

### Prerequisites

1. **Odoo 19 Community installed** (see `ODOO_INSTALLATION.md`)
2. **Python dependencies installed:**
   ```bash
   pip install requests flask flask-cors
   ```

### Step 1: Install Odoo 19 Community

Follow the complete guide in `ODOO_INSTALLATION.md`:

```bash
# On Ubuntu/Debian server
# 1. Install dependencies
sudo apt install -y python3 python3-pip postgresql postgresql-contrib

# 2. Clone Odoo 19
git clone https://github.com/odoo/odoo.git --depth 1 --branch 19.0

# 3. Install Python requirements
pip install -r requirements.txt

# 4. Create database
sudo -u postgres createuser -s odoo19

# 5. Start Odoo
./odoo-bin -c odoo.conf
```

### Step 2: Configure Environment Variables

Create `.env` file in the Gold directory:

```bash
# .env file
ODOO_URL=http://localhost:8069
ODOO_DB=my_business_db
ODOO_USERNAME=mcp@yourbusiness.local
ODOO_PASSWORD=YourSecurePassword123
ODOO_API_KEY=

MCP_ODOO_PORT=8082
MCP_ODOO_HOST=localhost
```

### Step 3: Start MCP Odoo Server

```bash
# Load environment variables
export $(cat .env | xargs)

# Start MCP server
python mcp_odoo_server.py
```

**Expected Output:**
```
============================================================
MCP Odoo Server - Accounting Integration
============================================================

Odoo URL: http://localhost:8069
Odoo Database: my_business_db
Username: mcp@yourbusiness.local

Available Tools:
  POST /tools/create_invoice  - Create draft customer invoice
  POST /tools/search_partners - Search customers/vendors
  POST /tools/post_invoice    - Post/confirm a draft invoice
  GET  /tools/read_balance    - Get account balances
  GET  /tools/get_invoice     - Get invoice details
  GET  /tools/list_invoices   - List invoices with filters
  GET  /health                - Health check

Starting server on http://localhost:8082
============================================================
```

### Step 4: Test MCP Server Health

```bash
# In a new terminal
curl http://localhost:8082/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "service": "mcp-odoo-server",
  "odoo_url": "http://localhost:8069",
  "odoo_db": "my_business_db",
  "authenticated": true,
  "timestamp": "2026-02-23T10:00:00.000000"
}
```

### Step 5: Run Full Test

```bash
# Run test with real Odoo connection
python test_odoo_mcp.py --real
```

---

## Manual API Testing

### Test 1: Search Partners

```bash
curl -X POST http://localhost:8082/tools/search_partners \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test",
    "partner_type": "customer",
    "limit": 5
  }'
```

### Test 2: Create Invoice

```bash
curl -X POST http://localhost:8082/tools/create_invoice \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "Test Customer ABC Corp",
    "amount": 2500.00,
    "description": "Website Development Services",
    "reference": "TEST-001",
    "due_date": "2026-03-25"
  }'
```

### Test 3: Read Balance

```bash
curl http://localhost:8082/tools/read_balance
```

### Test 4: Get Invoice Details

```bash
curl "http://localhost:8082/tools/get_invoice?invoice_id=1"
```

### Test 5: List Invoices

```bash
curl "http://localhost:8082/tools/list_invoices?state=draft&limit=10"
```

### Test 6: Post Invoice

```bash
curl -X POST http://localhost:8082/tools/post_invoice \
  -H "Content-Type: application/json" \
  -d '{"invoice_id": 1}'
```

---

## Integration Test: Full Workflow

### Scenario: Client Requests Invoice via Email

**1. Email arrives and is saved to /Needs_Action:**

```markdown
# Email from client@abccorp.com

**Subject:** Invoice Request - Project Phase 1

Please send invoice for:
- Customer: ABC Corporation
- Amount: $5,000
- Service: Website Design - Phase 1
- Due: 30 days
```

**2. Run odoo_accounting skill:**

```bash
python reasoning_loop.py --skill=odoo_accounting
```

**3. Check created files:**

```bash
# Check approval file
cat Pending_Approval/INVOICE_*.md

# Check audit log
cat Audit_Log.md | tail -20
```

**4. Approve invoice (manual step):**

```bash
# Move approval file to Approved
move Pending_Approval\INVOICE_1001.md Approved\
```

**5. System posts invoice and sends email:**

```bash
# This happens automatically after approval
# Check Completed folder
dir Completed\
```

---

## Troubleshooting

### Error: "Cannot connect to MCP server"

```bash
# Check if server is running
netstat -an | findstr 8082

# Start MCP server
python mcp_odoo_server.py
```

### Error: "Authentication failed"

```bash
# Verify Odoo credentials
# 1. Check .env file
type .env

# 2. Test Odoo login manually
# Go to: http://localhost:8069
# Login with mcp@yourbusiness.local
```

### Error: "Customer not found"

```bash
# Create customer in Odoo first
# 1. Go to: http://localhost:8069
# 2. Apps → Contacts → Create
# 3. Fill in customer details
# 4. Mark as Customer
# 5. Save
```

### Error: "Database does not exist"

```bash
# Create database in Odoo
# 1. Go to: http://localhost:8069/web/database/manager
# 2. Click "Create Database"
# 3. Name: my_business_db
# 4. Install Invoicing/Accounting modules
```

---

## Verify Installation

### Check Directories

```bash
# Should exist after test
dir Needs_Action\
dir Pending_Approval\
dir Completed\
```

### Check Files Created

```
Needs_Action/
└── email_Invoice_Request_ABC_Corp_20260223_*.md

Pending_Approval/
└── INVOICE_*.md

Completed/
└── POSTED_INVOICE_*.md
```

### Check Odoo (if real connection)

```
1. Login to Odoo: http://localhost:8069
2. Go to: Invoicing → Customers → Invoices
3. Find your test invoice (INV/2026/...)
4. Verify state: Draft → Posted
```

---

## Configuration for Claude Code MCP

Add to `~/.config/claude-code/mcp.json`:

```json
{
  "mcpServers": {
    "odoo-mcp": {
      "command": "python",
      "args": ["D:/Fahad Project/AI-Driven/Personal-AI-Employee-Hackathon-0/Gold/mcp_odoo_server.py"],
      "env": {
        "ODOO_URL": "http://localhost:8069",
        "ODOO_DB": "my_business_db",
        "ODOO_USERNAME": "mcp@yourbusiness.local",
        "ODOO_PASSWORD": "YourSecurePassword123"
      }
    }
  }
}
```

---

## Test Checklist

- [ ] Mock mode test passes (`python test_odoo_mcp.py --mock`)
- [ ] MCP server starts without errors
- [ ] Health endpoint returns status "healthy"
- [ ] Partner search returns results
- [ ] Invoice creation returns success with invoice_id
- [ ] Approval file created in `/Pending_Approval/`
- [ ] Invoice posting changes state to "posted"
- [ ] Balance endpoint returns financial data
- [ ] (Real Odoo) Invoice visible in Odoo UI
- [ ] (Real Odoo) Customer/vendor records accessible

---

## Next Steps After Testing

1. **Configure production Odoo instance**
   - Set up chart of accounts
   - Configure taxes for your country
   - Add real customers and vendors
   - Set up bank accounts

2. **Customize invoice templates**
   - Go to: Invoicing → Configuration → Settings
   - Enable "Custom Invoice Layout"
   - Upload company logo

3. **Set up email for invoice delivery**
   - Configure outgoing mail server in Odoo
   - Test email delivery

4. **Enable automated workflows**
   - Payment reminders
   - Recurring invoices
   - Auto-reconciliation

---

*Testing Guide for Odoo MCP Integration v1.0*
