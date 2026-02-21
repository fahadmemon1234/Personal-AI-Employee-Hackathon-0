# Troubleshooting Guide - Gold Tier Automation System

## Issues Identified & Solutions

### 1. Gmail Authentication Error ✅ FIXED

**Problem:**
```
google.auth.exceptions.RefreshError: invalid_grant: Token has been expired or revoked.
```

**Solution:**
- Deleted expired `token.pickle` file
- On next run, Gmail Watcher will prompt for re-authentication
- Browser will open automatically - login with your Google account
- New token will be saved automatically

**To Fix:**
```bash
# Token has been deleted, just run Gmail Watcher again
python gmail_watcher.py
```

---

### 2. Odoo Database Connection Issue ⚠️ NEEDS ATTENTION

**Problem:**
```
psycopg2.OperationalError: database "FahadMemon" does not exist
```

**Root Cause:**
The database name in your Odoo instance doesn't match the configured name.

**Possible Solutions:**

#### Option A: Try lowercase database name (Already applied)
```env
ODOO_DB=fahadmemon
```

#### Option B: Use email as database name
For Odoo.com instances, the database name is often your email address:
```env
ODOO_DB=fahadmemon131@gmail.com
```

#### Option C: Check your actual Odoo database name
1. Login to https://fahadmemon.odoo.com
2. Go to Settings → Database Manager
3. Note the exact database name
4. Update `.env` file with the correct name

**To Test:**
```bash
# After updating .env, test the connection
python -c "from odoo_integration.odoo_connector import get_odoo_connection; conn = get_odoo_connection(); print('Success!' if conn else 'Failed')"
```

---

### 3. Facebook/Instagram Credentials Missing ⚠️ OPTIONAL

**Problem:**
```env
META_ACCESS_TOKEN=your_meta_access_token
FACEBOOK_PAGE_ID=your_facebook_page_id
INSTAGRAM_BUSINESS_ACCOUNT_ID=your_instagram_business_account_id
```

These are placeholder values. Facebook/Instagram features won't work without real credentials.

**Solution (If you need FB/IG integration):**

1. **Get Meta Access Token:**
   - Go to https://developers.facebook.com/
   - Create a new app
   - Get Access Token from Graph API Explorer

2. **Get Facebook Page ID:**
   - Go to your Facebook Page
   - Click "About" section
   - Find Page ID (or use: https://findmyfbid.in/)

3. **Get Instagram Business Account ID:**
   - Your Instagram must be a Business account
   - Connect it to your Facebook Page
   - Get ID from Graph API Explorer

4. **Update .env file:**
   ```env
   META_ACCESS_TOKEN=EAAB... (your actual token)
   FACEBOOK_PAGE_ID=123456789 (your page ID)
   INSTAGRAM_BUSINESS_ACCOUNT_ID=987654321 (your IG account ID)
   ```

**Note:** This is OPTIONAL. The system works without FB/IG integration.

---

## Quick Test Commands

### Test All Components
```bash
python comprehensive_test.py
```

### Test Individual Components

**Gmail:**
```bash
python gmail_watcher.py
```

**WhatsApp:**
```bash
python whatsapp_watcher.py
```

**Reasoning Loop:**
```bash
python reasoning_loop.py
```

**CEO Briefing:**
```bash
python ceo_briefing_skill.py
```

**Verify Gold Tier:**
```bash
python verify_gold_tier.py
```

---

## Current Status Summary

| Component | Status | Notes |
|-----------|--------|-------|
| Gmail Watcher | ✅ Ready | Token deleted, will re-authenticate on first run |
| WhatsApp Watcher | ✅ Ready | No issues detected |
| Reasoning Loop | ✅ Ready | No issues detected |
| Agent Interface | ✅ Ready | No issues detected |
| LinkedIn Poster | ✅ Ready | No issues detected |
| Odoo Integration | ⚠️ Warning | Database name needs correction |
| Twitter Integration | ✅ Ready | API credentials configured |
| Facebook/Instagram | ⚠️ Optional | Placeholder credentials (optional feature) |
| CEO Briefing | ✅ Ready | Works even without Odoo |
| MCP Servers | ✅ Ready | All 5 servers configured |

---

## Next Steps

### Critical (Required)
1. **Re-authenticate Gmail:**
   ```bash
   python gmail_watcher.py
   ```
   Browser will open - login and grant permissions.

2. **Fix Odoo Database Name:**
   - Login to your Odoo instance
   - Find the correct database name
   - Update `.env` file
   - Test connection

### Optional (Nice to have)
3. **Configure Facebook/Instagram** (if needed)
   - Follow the steps above to get credentials
   - Update `.env` file

---

## Production Deployment

Once all issues are resolved, deploy with PM2:

```bash
# Install PM2 (if not installed)
npm install -g pm2

# Start all services
pm2 start ecosystem.config.js

# Save PM2 configuration
pm2 save

# Monitor services
pm2 monit
```

---

## Need Help?

1. **Check Audit Log:**
   ```bash
   type Audit_Log.md
   ```

2. **Run Verification:**
   ```bash
   python verify_gold_tier.py
   ```

3. **Check Error Log:**
   ```bash
   type error_log.txt
   ```

---

**Last Updated:** 2026-02-21  
**System Version:** Gold Tier v1.0
