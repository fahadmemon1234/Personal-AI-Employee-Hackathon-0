# 🚀 How to Run the Gold Tier Automation System

## Quick Start (3 Steps)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Configure .env File
Edit the `.env` file and add your API credentials:
- Odoo credentials
- Gmail API credentials
- Twitter API credentials
- Facebook/Instagram credentials

### Step 3: Run the System

**Windows:**
```bash
start.bat
```

**Linux/Mac:**
```bash
chmod +x start.sh
./start.sh
```

**Or use the Python menu directly:**
```bash
python main.py
```

---

## Running Individual Components

### Gmail Watcher
Monitors Gmail for important emails and saves them to Needs_Action folder.
```bash
python gmail_watcher.py
```

### WhatsApp Watcher
Monitors WhatsApp Web for keywords and saves messages.
```bash
python whatsapp_watcher.py
```

### Reasoning Loop
Autonomous loop that processes requests in Needs_Action folder.
```bash
python reasoning_loop.py
```

### Agent Interface
Monitors approvals and executes MCP actions.
```bash
python agent_interface.py
```

### LinkedIn Poster
Creates and posts LinkedIn content.
```bash
python linkedin_poster.py
```

### Scheduler
Runs the reasoning loop every 30 minutes.
```bash
python scheduler.py
```

### System Health Check
Checks PM2 process status and updates dashboard.
```bash
python check_system_health.py
```

### CEO Briefing
Generates weekly Monday CEO briefing report.
```bash
python ceo_briefing_skill.py
```

---

## Production Deployment (PM2)

### Install PM2
```bash
npm install -g pm2
```

### Start All Services
```bash
pm2 start ecosystem.config.js
pm2 save
```

### Monitor Services
```bash
pm2 monit
```

### View Logs
```bash
pm2 logs
```

### Stop Services
```bash
pm2 stop all
```

---

## First Time Setup

### 1. Gmail API Setup
1. Go to https://console.cloud.google.com/apis/credentials
2. Create OAuth2 credentials
3. Download as `credentials.json`
4. Place in project root directory

### 2. Twitter API Setup
1. Go to https://developer.twitter.com/
2. Create an app
3. Get API keys
4. Update `.env` file

### 3. Facebook/Instagram Setup
1. Go to https://developers.facebook.com/
2. Create an app
3. Get access token
4. Update `.env` with Page ID and Account ID

### 4. Verify Setup
```bash
python verify_gold_tier.py
```

---

## Common Issues

### "Module not found"
```bash
pip install -r requirements.txt
```

### "Gmail authentication failed"
- Ensure `credentials.json` is in project root
- Delete `token.pickle` and re-run
- Check Gmail API is enabled

### "Odoo connection failed"
- Verify Odoo URL in `.env`
- Check database name and credentials
- Ensure Odoo instance is accessible

### "PM2 not found"
```bash
npm install -g pm2
```

---

## Monitoring & Logs

### Dashboard
Open `Dashboard.md` to see:
- Active plans
- System health
- Recent activities

### Audit Log
Check `Audit_Log.md` for all system actions.

### PM2 Logs
```bash
pm2 logs
```

---

## Need Help?

1. Run verification: `python verify_gold_tier.py`
2. Check audit log: `Audit_Log.md`
3. Review lessons: `LESSONS_LEARNED.md`
