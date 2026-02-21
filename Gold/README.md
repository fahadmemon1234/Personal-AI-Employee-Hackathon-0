# Gold Tier Automation System

A fully autonomous AI employee system with multi-platform integration (Gmail, WhatsApp, LinkedIn, Twitter, Facebook, Instagram, Odoo).

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Edit the `.env` file with your credentials:

```bash
# ODOO (Accounting/ERP)
ODOO_URL=http://fahadmemon.odoo.com
ODOO_DB=FahadMemon
ODOO_USERNAME=your_email@gmail.com
ODOO_PASSWORD=your_password

# GMAIL API
GMAIL_CREDENTIALS_FILE=credentials.json
GMAIL_TOKEN_FILE=token.pickle

# TWITTER/X API
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_token
TWITTER_ACCESS_TOKEN_SECRET=your_token_secret

# FACEBOOK/INSTAGRAM (Meta)
META_ACCESS_TOKEN=your_access_token
FACEBOOK_PAGE_ID=your_page_id
INSTAGRAM_BUSINESS_ACCOUNT_ID=your_account_id
```

### 3. Setup API Credentials

#### Gmail Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Create OAuth2 credentials
3. Download as `credentials.json` and place in project root

#### Twitter/X Setup
1. Go to [Twitter Developer Portal](https://developer.twitter.com/)
2. Create an app and get API keys
3. Update `.env` with your credentials

#### Facebook/Instagram Setup
1. Go to [Meta for Developers](https://developers.facebook.com/)
2. Create an app and get access token
3. Update `.env` with Page ID and Account ID

### 4. Run the System

#### Option A: Run Individual Components

```bash
# Gmail Watcher (monitors emails)
python gmail_watcher.py

# WhatsApp Watcher (monitors WhatsApp Web)
python whatsapp_watcher.py

# Reasoning Loop (processes requests)
python reasoning_loop.py

# Agent Interface (handles approvals)
python agent_interface.py

# LinkedIn Poster (scheduled posts)
python linkedin_poster.py

# Scheduler (runs reasoning loop every 30 min)
python scheduler.py

# System Health Check
python check_system_health.py

# CEO Briefing Generator
python ceo_briefing_skill.py
```

#### Option B: Run with PM2 (Production)

**Windows:**
```bash
pm2_setup.bat
```

**Linux/Mac:**
```bash
chmod +x pm2_setup.sh
./pm2_setup.sh
```

**Manual PM2 Commands:**
```bash
# Install PM2
npm install -g pm2

# Start all services
pm2 start ecosystem.config.js

# Monitor services
pm2 monit

# View logs
pm2 logs

# Stop all services
pm2 stop all
```

### 5. Verify Installation

```bash
python verify_gold_tier.py
```

## 📁 Directory Structure

```
Gold/
├── .env                          # Environment variables (configure this!)
├── requirements.txt              # Python dependencies
├── mcp.json                      # MCP server configuration
├── ecosystem.config.js           # PM2 configuration
├── Dashboard.md                  # Main dashboard
├── Audit_Log.md                  # System audit log
├── Company_Handbook.md           # Company guidelines
│
├── gmail_watcher.py              # Gmail monitoring
├── whatsapp_watcher.py           # WhatsApp monitoring
├── reasoning_loop.py             # Autonomous reasoning loop
├── agent_interface.py            # Human-in-the-loop interface
├── email_approval_workflow.py    # Email approval system
├── linkedin_poster.py            # LinkedIn automation
├── scheduler.py                  # Task scheduler
├── check_system_health.py        # Health monitoring
├── ceo_briefing_skill.py         # Weekly CEO reports
│
├── odoo_integration/             # Odoo ERP integration
│   ├── odoo_connector.py
│   ├── mcp_server.py
│   ├── sync_invoices.py
│   └── update_dashboard_with_odoo.py
│
├── social_media_integration/     # Social media connectors
│   ├── twitter_connector.py
│   ├── twitter_mcp_server.py
│   ├── facebook_instagram_connector.py
│   └── facebook_instagram_mcp_server.py
│
├── .qwen/skills/                 # Agent skills
│   ├── gmail_skill/
│   ├── whatsapp_skill/
│   ├── linkedin_skill/
│   ├── twitter_skill/
│   └── facebook_instagram_skill/
│
└── Directories (auto-created):
    ├── Needs_Action/             # Incoming tasks
    ├── Pending_Approval/         # Awaiting approval
    ├── Approved/                 # Approved actions
    ├── Completed/                # Finished tasks
    ├── Plans/                    # Action plans
    ├── Briefings/                # CEO briefings
    └── Posted/                   # Posted content
```

## 🔄 Workflow

1. **Incoming Requests** → Saved in `Needs_Action/`
2. **Reasoning Loop** → Creates plans in `Plans/`
3. **Approval Required?** → Moves to `Pending_Approval/`
4. **Human Approval** → Move file to `Approved/`
5. **Agent Executes** → Moves to `Completed/`

## 🛠️ Configuration

### Environment Variables Reference

| Variable | Description | Default |
|----------|-------------|---------|
| `ODOO_URL` | Odoo instance URL | `http://fahadmemon.odoo.com` |
| `ODOO_DB` | Odoo database name | `FahadMemon` |
| `ODOO_USERNAME` | Odoo username | - |
| `ODOO_PASSWORD` | Odoo password | - |
| `GMAIL_CREDENTIALS_FILE` | Gmail credentials file | `credentials.json` |
| `GMAIL_TOKEN_FILE` | Gmail token file | `token.pickle` |
| `TWITTER_API_KEY` | Twitter API key | - |
| `TWITTER_API_SECRET` | Twitter API secret | - |
| `TWITTER_ACCESS_TOKEN` | Twitter access token | - |
| `TWITTER_ACCESS_TOKEN_SECRET` | Twitter token secret | - |
| `META_ACCESS_TOKEN` | Meta access token | - |
| `FACEBOOK_PAGE_ID` | Facebook page ID | - |
| `INSTAGRAM_BUSINESS_ACCOUNT_ID` | Instagram business account ID | - |
| `REASONING_LOOP_INTERVAL` | Reasoning loop check interval (sec) | `10` |
| `SCHEDULER_INTERVAL` | Scheduler interval (sec) | `1800` |
| `GMAIL_MONITOR_INTERVAL` | Gmail check interval (sec) | `300` |
| `WHATSAPP_MONITOR_INTERVAL` | WhatsApp check interval (sec) | `10` |
| `MAX_AUTONOMOUS_ITERATIONS` | Max autonomous iterations | `5` |

## 📊 Monitoring

### Dashboard
View `Dashboard.md` for real-time status of:
- Active plans
- System health
- Bank balances
- Recent activities

### Audit Log
Check `Audit_Log.md` for all system actions.

### Health Check
```bash
python check_system_health.py
```

## 🧪 Testing

```bash
# Run comprehensive tests
python final_test.py

# Verify Gold Tier requirements
python verify_gold_tier.py

# Test logging
python test_logging.py
```

## 🔧 Troubleshooting

### Gmail Authentication Failed
- Ensure `credentials.json` is in project root
- Delete `token.pickle` and re-authenticate
- Check Gmail API is enabled in Google Cloud Console

### Odoo Connection Failed
- Verify Odoo URL is correct
- Check database name and credentials
- Ensure Odoo instance is accessible

### WhatsApp Not Working
- Make sure you're logged into WhatsApp Web
- Browser must be visible during first login
- Check `whatsapp_data/` folder for session data

### PM2 Not Starting
- Install Node.js and PM2: `npm install -g pm2`
- Check `ecosystem.config.js` for correct paths
- Run `pm2 startup` to setup PM2 on boot

## 📝 Important Notes

1. **Security**: Never commit `.env` file with real credentials to version control
2. **Backup**: Regularly backup `token.pickle` and `whatsapp_data/` folder
3. **Monitoring**: Use PM2 for production deployments
4. **Updates**: Run `verify_gold_tier.py` after making changes

## 🆘 Support

For issues or questions:
1. Check `Audit_Log.md` for error messages
2. Run `python verify_gold_tier.py` to diagnose issues
3. Review `LESSONS_LEARNED.md` for known solutions
