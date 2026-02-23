# Odoo 19 Installation - Quick Guide

## Download Failed - Use This Link Instead

Nightly build link change ho sakta hai. Stable version use karein:

---

## Option 1: Official Odoo Website (Recommended)

### Step 1: Download

**Visit:** https://www.odoo.com/page/download

**Select:**
- Odoo 19 (Community Edition)
- Windows (64-bit)

**Direct Download Link:**
```
https://download.odoo.com/community/odoo_19.0.latest.exe
```

### Step 2: Install

1. Downloaded file par **double-click** karein
2. **Next** → **Next** → **Install**
3. Wait 5-10 minutes
4. **Finish**

### Step 3: Start Odoo

```
Start Menu → Odoo 19.0 → Odoo Server
```

Ya browser mein:
```
http://localhost:8069
```

---

## Option 2: GitHub Release

### Download from GitHub

```
https://github.com/odoo/odoo/releases
```

Latest 19.x release download karein.

---

## Option 3: Manual Download + Script

### Step 1: Download Manually

Browser mein ye link try karein:

1. **Primary:** https://download.odoo.com/community/odoo_19.0.latest.exe
2. **Mirror:** https://github.com/odoo/odoo/releases/download/19.0/odoo_19.0.exe

### Step 2: Save To

```
D:\Downloads\odoo_19_installer.exe
```

### Step 3: Run Script Again

```powershell
# Downloaded file ko temp mein copy karein
Copy-Item "D:\Downloads\odoo_19_installer.exe" "$env:TEMP\odoo_19_installer.exe"

# Phir script run karein
powershell -ExecutionPolicy Bypass -File install_odoo_windows.ps1
```

---

## Quick Install Steps (Manual)

### 1. Download & Install

```powershell
# Direct download try karein
Start-BitsTransfer -Source "https://download.odoo.com/community/odoo_19.0.latest.exe" -Destination "$env:TEMP\odoo_installer.exe"

# Install
Start-Process "$env:TEMP\odoo_installer.exe" -Wait
```

### 2. Configure

```powershell
# Odoo config file
$odooConf = "C:\Program Files\Odoo 19.0\server\odoo.conf"

# Edit karein (Notepad as Admin)
notepad $odooConf
```

Add/Update:
```ini
[options]
admin_passwd = master_admin_123
http_port = 8069
```

### 3. Start Service

```powershell
# Services open karein
services.msc

# Find: odoo_server_19
# Right-click → Start
```

### 4. Create Database

Browser mein:
```
http://localhost:8069
```

Click: **Create Database**

Fill:
```
Database: my_business_db
Email: admin@yourbusiness.com
Password: AdminPassword123
```

---

## Alternative: Odoo 18 (Stable)

Agar Odoo 19 stable nahi hai, to Odoo 18 use karein:

**Download:** https://www.odoo.com/page/download

Ya direct:
```
https://download.odoo.com/community/odoo_18.0.latest.exe
```

---

## After Installation

### .env File Update

Already created at:
```
D:\Fahad Project\AI-Driven\Personal-AI-Employee-Hackathon-0\Gold\.env
```

Verify:
```
ODOO_URL=http://localhost:8069
ODOO_DB=my_business_db
ODOO_USERNAME=mcp@yourbusiness.local
ODOO_PASSWORD=McpPassword123
```

### MCP Server Restart

```powershell
# Purana server band karein (CTRL+C)
cd "D:\Fahad Project\AI-Driven\Personal-AI-Employee-Hackathon-0\Gold"
python mcp_odoo_server.py
```

### Test Connection

```powershell
# Health check
Invoke-RestMethod http://localhost:8082/health

# Test with mock (if Odoo not ready)
python test_odoo_mcp.py --mock
```

---

## Troubleshooting

### Download Still Fails

```powershell
# Check internet connection
Test-NetConnection download.odoo.com -Port 443

# Try alternative method
Invoke-WebRequest -Uri "https://download.odoo.com/community/odoo_19.0.latest.exe" -OutFile "$env:TEMP\odoo.exe"
```

### Port 8069 Already In Use

```powershell
# Check kya use kar raha hai
netstat -ano | findstr 8069

# Kill process (replace PID)
taskkill /PID <PID> /F
```

### Service Not Found

```powershell
# Manual start
cd "C:\Program Files\Odoo 19.0\server"
python odoo-bin.py --config=odoo.conf
```

---

## Contact/Support

- Odoo Community: https://www.odoo.com/forum/help-1
- GitHub Issues: https://github.com/odoo/odoo/issues

---

*Quick Install Guide - Updated for Download Issues*
