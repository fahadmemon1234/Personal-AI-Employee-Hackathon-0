# Odoo Setup Guide

## Problem

Your Odoo connection is failing with error:
```
database "FahadMemon" does not exist
```

This means your Odoo database has been deleted, expired, or never existed with that name.

---

## Solutions

### Option 1: Check Odoo Database Status

1. **Login to Odoo.com Portal**
   - Go to https://www.odoo.com/my/databases
   - Login with: fahadmemon131@gmail.com
   - Check if database "FahadMemon" exists

2. **If Database Exists:**
   - Note the EXACT database name (case-sensitive)
   - Update `.env` file:
     ```env
     ODOO_DB=exact_database_name_from_portal
     ```

3. **If Database Doesn't Exist:**
   - Your Odoo subscription may have expired
   - Free trial databases are deleted after expiry
   - You need to either:
     - Renew subscription
     - Create new database
     - Use local Odoo installation

---

### Option 2: Create New Odoo Database

1. **Create New Database:**
   - Go to https://www.odoo.com
   - Click "Start Now"
   - Create new database with email: fahadmemon131@gmail.com

2. **Get Database Name:**
   - After creation, note the database name
   - Usually it's your email or a random string

3. **Update .env:**
   ```env
   ODOO_URL=https://your-new-db.odoo.com
   ODOO_DB=your_new_database_name
   ODOO_USERNAME=fahadmemon131@gmail.com
   ODOO_PASSWORD=your_password
   ```

---

### Option 3: Use Local Odoo (Recommended for Development)

Install Odoo Community locally:

1. **Download Odoo:**
   ```bash
   # Windows
   Download from: https://www.odoo.com/page/download
   ```

2. **Install Odoo 19:**
   - Run installer
   - Set master password
   - Create database

3. **Update .env:**
   ```env
   ODOO_URL=http://localhost:8069
   ODOO_DB=your_local_db
   ODOO_USERNAME=admin
   ODOO_PASSWORD=admin
   ```

---

### Option 4: Continue Without Odoo (Fallback Mode)

The system now works WITHOUT Odoo using fallback mode:

**What Works Without Odoo:**
- ✅ Gmail Watcher
- ✅ WhatsApp Watcher
- ✅ LinkedIn Poster
- ✅ Twitter Integration
- ✅ Reasoning Loop
- ✅ Agent Interface
- ✅ CEO Briefing (with bank transactions only)

**What Doesn't Work:**
- ❌ Accounting integration
- ❌ Invoice sync
- ❌ Financial data from Odoo

**To Use Fallback Mode:**
Just run the system as-is. The CEO Briefing will generate using bank transactions only.

---

## Test Connection

After updating `.env`, test with:

```bash
python -c "from odoo_integration.odoo_connector import get_odoo_connection; conn = get_odoo_connection(); print('CONNECTED!' if conn else 'FAILED')"
```

---

## Current Status

| Component | Status |
|-----------|--------|
| Odoo Connection | ❌ Database doesn't exist |
| CEO Briefing | ✅ Works (fallback mode) |
| Other Components | ✅ All working |

---

## Quick Fix Steps

1. **Check if you need Odoo:**
   - If YES → Follow Option 1, 2, or 3
   - If NO → Continue using fallback mode (Option 4)

2. **If you need Odoo:**
   ```
   a. Login to odoo.com
   b. Check database status
   c. Get correct database name
   d. Update .env file
   e. Test connection
   ```

3. **If you don't need Odoo:**
   - System works fine without it
   - CEO Briefing uses bank transactions
   - All other features work normally

---

**Last Updated:** 2026-02-21  
**Status:** System operational with fallback mode
