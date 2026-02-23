# Odoo 19 Installation Guide for Windows

## Quick Install (Recommended for Windows)

### Step 1: Download Odoo Windows Installer

**Official Download Link:**
https://nightly.odoo.com/19.0/nightly/win/

**Latest Version (as of Feb 2026):**
- Odoo 19.0 Nightly Build (64-bit)
- File: `odoo_19.0.latest.exe`
- Size: ~300MB

### Step 2: Run Installer

1. **Download** the `.exe` file
2. **Double-click** to run installer
3. **Accept** License Agreement
4. **Choose Installation Folder:**
   ```
   C:\Program Files\Odoo 19.0
   ```
5. **Select Components:**
   - ✅ Odoo Server
   - ✅ PostgreSQL Database
   - ✅ Python 3.10+
   - ✅ Required Libraries

6. **Set Installation Options:**
   - **Install for:** All Users
   - **Start Menu Folder:** Odoo 19.0

7. **Click Install** and wait (~5-10 minutes)

8. **Finish** installation

---

## Step 3: Configure Odoo

### Create odoo.conf File

Location: `C:\Program Files\Odoo 19.0\server\odoo.conf`

```ini
[options]
; Admin password for database management
admin_passwd = master_admin_123

; Database connection
db_host = localhost
db_port = 5432
db_user = odoo
db_password = odoo
db_name = my_business_db

; Server configuration
http_port = 8069
http_interface = 0.0.0.0

; Logging
logfile = C:\Program Files\Odoo 19.0\server\odoo.log
log_level = info

; Data directory
data_dir = C:\Program Files\Odoo 19.0\data

; Addons paths
addons_path = C:\Program Files\Odoo 19.0\server\odoo\addons
```

---

## Step 4: Start Odoo Service

### Option A: Windows Service (Auto-start)

```powershell
# Open PowerShell as Administrator

# Check if Odoo service exists
Get-Service -Name "odoo_server_19"

# Start Odoo service
Start-Service odoo_server_19

# Set to auto-start
Set-Service -Name "odoo_server_19" -StartupType Automatic
```

### Option B: Manual Start

```powershell
# Navigate to Odoo folder
cd "C:\Program Files\Odoo 19.0\server"

# Run Odoo manually
python odoo-bin.py --config=odoo.conf
```

---

## Step 5: Create Database

1. **Open Browser:** http://localhost:8069

2. **Click "Create Database"**

3. **Fill in details:**
   ```
   Database Name: my_business_db
   Email: admin@yourbusiness.com
   Password: AdminPassword123
   Language: English (US)
   Country: Pakistan
   ```

4. **Click "Create Database"**

5. **Wait 2-3 minutes** for database creation

---

## Step 6: Install Accounting Modules

1. **Login to Odoo:**
   - URL: http://localhost:8069
   - Email: admin@yourbusiness.com
   - Password: AdminPassword123

2. **Go to Apps:**
   - Click **Apps** from main menu

3. **Remove "Apps" filter:**
   - Click the filter icon (funnel)
   - Uncheck "Apps"

4. **Search and Install:**
   - Search: `Invoicing`
   - Click **Install** on "Invoicing" app
   
5. **Optional - Full Accounting:**
   - Search: `account_accountant`
   - Click **Install** (requires Odoo Studio subscription for Community)

6. **Complete Configuration Wizard:**
   - Company Info
   - Chart of Accounts
   - Tax Configuration

---

## Step 7: Create MCP User

1. **Go to Settings** → **Users & Companies** → **Users**

2. **Click Create**

3. **Fill in:**
   ```
   Name: MCP Integration User
   Email: mcp@yourbusiness.local
   ```

4. **Set Access Rights:**
   - Invoicing / Accounting: **Administrator**
   - Settings: **Internal User**

5. **Set Password:**
   - Click "Send Password Reset Email" OR
   - Manually set password: `McpPassword123`

6. **Save**

---

## Step 8: Verify Installation

### Check Odoo is Running

```powershell
# Check if port 8069 is listening
netstat -an | findstr 8069

# Check Odoo service status
Get-Service odoo_server_19

# View Odoo logs
Get-Content "C:\Program Files\Odoo 19.0\server\odoo.log" -Tail 50
```

### Test Web Access

```
http://localhost:8069
```

Should show Odoo login page.

---

## Step 9: Configure .env for MCP

Create `.env` file in Gold directory:

**Location:** `D:\Fahad Project\AI-Driven\Personal-AI-Employee-Hackathon-0\Gold\.env`

```env
ODOO_URL=http://localhost:8069
ODOO_DB=my_business_db
ODOO_USERNAME=mcp@yourbusiness.local
ODOO_PASSWORD=McpPassword123
MCP_ODOO_PORT=8082
MCP_ODOO_HOST=0.0.0.0
ODOO_MOCK=false
```

---

## Step 10: Test MCP Connection

```bash
# Restart MCP server (if already running, stop and restart)
python mcp_odoo_server.py

# In new terminal, test health
curl http://localhost:8082/health

# Test with real Odoo
python test_odoo_mcp.py --real
```

---

## Troubleshooting

### Port 8069 Already in Use

```powershell
# Find process using port 8069
netstat -ano | findstr 8069

# Kill the process (replace PID with actual number)
taskkill /PID <PID> /F
```

### PostgreSQL Error

```powershell
# Restart PostgreSQL service
Restart-Service postgresql-x64-15

# Or check Windows Services
services.msc
# Find: postgresql-x64-15
# Right-click → Restart
```

### Cannot Access Odoo

```powershell
# Check Windows Firewall
# Allow port 8069

netsh advfirewall firewall add rule name="Odoo" dir=in action=allow protocol=TCP localport=8069
```

### Database Creation Fails

```
# Try manual database creation
# Open PowerShell as Administrator

cd "C:\Program Files\Odoo 19.0\server"

# Create database
python odoo-bin.py -d my_business_db --without-demo=all --stop-after-init
```

---

## Alternative: WSL2 (Windows Subsystem for Linux)

Agar EXE installer se issues hon, to WSL2 use karein:

```powershell
# Enable WSL
wsl --install

# Install Ubuntu
wsl --install -d Ubuntu-22.04

# Then follow ODOO_INSTALLATION.md (Linux instructions)
```

---

## Download Links

| Component | Link |
|-----------|------|
| Odoo 19 Windows | https://nightly.odoo.com/19.0/nightly/win/ |
| Odoo 18 Stable | https://www.odoo.com/page/download |
| PostgreSQL (standalone) | https://www.postgresql.org/download/windows/ |

---

## System Requirements

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| RAM | 4GB | 8GB+ |
| Storage | 10GB | 20GB+ |
| Python | 3.10+ | 3.11+ |
| PostgreSQL | 12+ | 15+ |

---

*Windows Installation Guide for Odoo 19 Community*
