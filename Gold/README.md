# AI Agent Silver Tier Implementation

Congratulations! You've reached the Silver Tier of your AI Agent system. This implementation includes enhanced automation with email monitoring, WhatsApp integration, social media automation, agent skills, scheduling, and MCP servers.

## Silver Tier Milestones Achieved

✅ **Agent Skills Conversion**: All automation logic (Gmail, WhatsApp) converted into official 'Agent Skills'
✅ **Basic Scheduling**: Python-based scheduler runs reasoning_loop.py every 30 minutes
✅ **HITL Validation**: Verified that no email is sent without approval from /Pending_Approval to /Approved
✅ **Multi-Watcher Support**: Comprehensive monitoring of Gmail, WhatsApp, and Inbox with unified processing
✅ **Enhanced Automation**: Automated email processing and social media engagement
✅ **Plan Generation**: Automatically creates action plans in `Plans/` directory for all requests

## Quick Start

**Prerequisites**: Python 3.10+ (tested on Python 3.13)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
playwright install
```

### 2. Create Required Directories
```bash
mkdir Inbox Needs_Action Approved Completed Plans Pending_Approval Sent
```

### 3. Start MCP Servers
```bash
python start_mcp_servers.py
```

### 4. Start the Scheduler (runs every 30 mins)
```bash
python scheduler.py
```

---

## Components

### 1. Dashboard (Dashboard.md)
- Shows bank balances and tasks
- Provides quick access to important functions
- Tracks system status and activity

### 2. Company Handbook (Company_Handbook.md)
- Contains "Rules of Engagement"
- Outlines operational guidelines
- Defines decision matrix and emergency procedures

### 3. Inbox Watcher Script (watcher.py)
- Monitors the `/Inbox` folder for new files
- Automatically moves new files to `/Needs_Action` folder
- Logs all actions for audit trail
- Built using the BaseWatcher pattern

### 4. Gmail Watcher Script (gmail_watcher.py)
- Monitors Gmail for important unread emails
- Saves emails as .md files in `/Needs_Action` folder
- Requires Google API credentials for authentication
- Runs continuously to check for new emails

### 5. WhatsApp Watcher Script (whatsapp_watcher.py)
- Monitors WhatsApp Web for specific keywords ('urgent', 'payment', 'help', etc.)
- Saves detected messages as .md files in `/Needs_Action` folder
- Uses Playwright for browser automation
- Maintains persistent session to avoid repeated QR scans
- Implements agent skill to notify when new leads arrive

### 6. Reasoning Loop (reasoning_loop.py)
- Detects requests in `/Needs_Action` folder
- Creates `Plan.md` with proposed actions
- Includes checkboxes for identifying sender, drafting reply, and requesting approval for sensitive actions
- Implements Human-in-the-loop pattern for outgoing messages
- Waits for approval before executing actions
- Implements a complete reasoning cycle

### 7. Email Approval Workflow (email_approval_workflow.py)
- Prevents email sending without explicit approval
- Requires approval file in `/Approved` directory
- Only sends emails after approval is granted
- Moves processed requests to `/Completed` folder

### 8. Agent Skills Framework
- **Gmail Skill** (`.qwen/skills/gmail_skill/`): Monitors Gmail for new emails and processes them
- **WhatsApp Skill** (`.qwen/skills/whatsapp_skill/`): Monitors WhatsApp for new messages and processes them

### 9. Scheduler (scheduler.py)
- Python-based scheduler that runs reasoning_loop.py every 30 minutes
- Ensures continuous monitoring and processing of requests
- Handles timeouts and error recovery

### 10. Agent Interface (agent_interface.py)
- Coordinates all agent skills
- Enforces HITL validation
- Validates that no actions are taken without proper approval
- Monitors for approved items and executes them

### 11. MCP Configuration (mcp.json)
- Configures email-mcp and browser-mcp servers
- Defines server capabilities and settings
- Sets up workflow parameters
- Centralizes configuration for all services

## Configuration

### Environment Variables (`.env` file)
```bash
GOOGLE_CLIENT_ID=your_client_id_here
GOOGLE_CLIENT_SECRET=your_client_secret_here
GMAIL_CREDENTIALS_FILE=credentials.json
GMAIL_TOKEN_FILE=token.pickle
```

### Required Credentials

1. **Google API** (for Gmail watcher):
   - Go to https://console.cloud.google.com/apis/credentials
   - Create OAuth 2.0 credentials for Gmail API
   - Download `credentials.json` and place it in the root directory

## Running Individual Components

| Component | Command | Description |
|-----------|---------|-------------|
| MCP Servers | `python start_mcp_servers.py` | Starts Email (8080) + Browser (8081) servers |
| Scheduler | `python scheduler.py` | Runs reasoning loop every 30 minutes |
| Inbox Watcher | `python watcher.py` | Monitors `/Inbox` folder (file watcher) |
| Gmail Watcher | `python gmail_watcher.py` | Monitors Gmail for new emails |
| WhatsApp Watcher | `python whatsapp_watcher.py` | Monitors WhatsApp Web for keywords |
| Reasoning Loop | `python reasoning_loop.py` | Processes requests, creates plans |
| Email Approval | `python email_approval_workflow.py` | Handles email approval workflow |
| Agent Interface | `python agent_interface.py` | Coordinates all agent skills |

## Verification & Testing

Test individual components:
```bash
# Test module imports
python -c "import watcher; print('OK')"
python -c "import reasoning_loop; print('OK')"
python -c "import gmail_watcher; print('OK')"
python -c "import whatsapp_watcher; print('OK')"

# Test reasoning loop (creates plans for all files in Needs_Action)
python reasoning_loop.py

# Check created plans
dir Plans
```

## Directory Structure
```
├── Dashboard.md              # Main dashboard showing status and tasks
├── Company_Handbook.md       # Rules of engagement and operational guidelines
├── watcher.py               # Python script that monitors Inbox folder
├── gmail_watcher.py         # Python script that monitors Gmail
├── whatsapp_watcher.py      # Python script that monitors WhatsApp Web
├── reasoning_loop.py        # Implements reasoning loop for requests
├── email_approval_workflow.py # Handles email sending with approval workflow
├── scheduler.py             # Runs reasoning_loop.py every 30 minutes
├── agent_interface.py       # Coordinates all agent skills
├── mcp.json                 # Configuration for MCP servers
├── requirements.txt         # Dependencies
├── .qwen/
│   └── skills/              # Agent skills directory
│       ├── gmail_skill/
│       │   ├── SKILL.md     # Gmail skill documentation
│       │   └── gmail_skill.py # Gmail skill implementation
│       └── whatsapp_skill/
│           ├── SKILL.md     # WhatsApp skill documentation
│           └── whatsapp_skill.py # WhatsApp skill implementation
├── Inbox/                  # Folder monitored by the watcher
├── Needs_Action/           # Destination for files moved by watcher
├── Pending_Approval/       # Directory for items awaiting approval
├── Approved/               # Directory for approved items
├── Sent/                   # Directory for sent emails
├── Plans/                  # Directory for generated action plans
├── Completed/              # Directory for completed requests
└── watcher_log.txt         # Log of all file movements
```

## Usage

### Basic Workflow

1. **Place files in `Inbox/`** - Files are automatically moved to `Needs_Action/` by watcher
2. **Reasoning Loop processes** - Creates action plans in `Plans/` for each request
3. **Review plans** - Check generated plans in `Plans/` directory
4. **Approve actions** - Move approval files to `Approved/` to execute actions
5. **Check results** - Completed items moved to `Completed/`

### Email Monitoring Setup

1. Create Google Cloud project and enable Gmail API
2. Download OAuth 2.0 credentials as `credentials.json`
3. Place `credentials.json` in project root
4. Run `python gmail_watcher.py` to authenticate
5. Token saved as `token.pickle` for future use

### WhatsApp Monitoring Setup

1. Run `python whatsapp_watcher.py`
2. Scan QR code if prompted (one-time only)
3. Session saved in `whatsapp_data/` for future use
4. Monitors for keywords: urgent, payment, help, emergency, asap, important

### Approval Workflow

1. Sensitive actions create drafts in `Pending_Approval/`
2. Review and move approval file to `Approved/`
3. Agent interface executes the approved action
4. Completed items moved to `Completed/`

## Logs & Monitoring

- **watcher_log.txt** - File movement logs
- **Audit_Log.md** - System activity audit trail
- **Dashboard.md** - Current status and active plans
- **Plans/** - Generated action plans

## MCP Servers

### Email-MCP Server
- **Port**: 8080
- **Capabilities**: send-email, receive-email, process-email, gmail-watch, email-approval
- Handles all email-related operations with approval workflow

### Browser-MCP Server
- **Port**: 8081
- **Capabilities**: browse-web, scrape-content, automate-browser, social-media-post, web-interaction, whatsapp-monitor
- Manages web browsing, social media automation, and WhatsApp monitoring tasks

## Agent Skill Implementation

The system proactively reads from and writes to your vault (current directory):

- **Reading**: Watchers monitor Inbox, Gmail, and WhatsApp continuously
- **Writing**: Files moved between folders, logs written, dashboards updated
- **Automation**: Multiple systems operate independently once started
- **Reasoning**: Creates plans and waits for approval before acting
- **Safety**: All email sending and social posts require explicit approval
- **Social Media**: WhatsApp messages with keywords trigger agent notifications
- **Scheduling**: Scheduler ensures processing every 30 minutes
- **Skills**: Modular, reusable functionality for different platforms

## Testing & Verification

### Run Comprehensive Tests
```bash
# Run all component tests
python test_all_components.py

# Run social media specific tests
python test_social_mcp.py --dry-run

# Test individual modules
python -c "import watcher; print('OK')"
python -c "import reasoning_loop; print('OK')"
python -c "import mcp_social_server; print('OK')"
```

### Test Results (Latest: 2026-02-23)

| Component | Status | Notes |
|-----------|--------|-------|
| Module Imports | ✅ PASS | All 8 modules import successfully |
| Directory Structure | ✅ PASS | All 8 required directories exist |
| Environment Config | ✅ PASS | .env file configured with social media credentials |
| Social MCP Server | ✅ PASS | Server runs on port 8083, Instagram & Facebook configured |
| Email MCP Server | ⚠️ OPTIONAL | Runs on port 8080 (start when needed) |
| Browser MCP Server | ⚠️ OPTIONAL | Runs on port 8081 (start when needed) |
| Agent Skills | ✅ PASS | 2 skills found (gmail_skill, whatsapp_skill) |
| Documentation | ✅ PASS | All docs exist (Dashboard, Handbook, Audit_Log, README) |
| Reasoning Loop | ✅ PASS | Initialized, 945+ plan files created |
| Agent Interface | ✅ PASS | All approval directories exist |

### Instagram Post Test Results

**Endpoint:** `POST http://localhost:8083/tools/post_to_instagram`

**Test Payload:**
```json
{
  "account_id": "17841436842078450",
  "caption": "Test post from AI Employee System #TestPost #AIEmployee",
  "media_path": "https://via.placeholder.com/600x400.png?text=Test+Image",
  "dry_run": true
}
```

**Dry Run Mode:** ✅ Working
- Response: `{"success": true, "dry_run": true, "message": "[DRY RUN] Would post: ..."}`
- Posts logged to `Posts_Log.json`

**Real Posting Mode:** ⚠️ Requires Public Image URL
- Instagram Graph API requires publicly accessible image URL
- Local file paths must be hosted or use public URL
- API flow: Create Media Container → Publish Media

**Facebook Post Test:** ✅ Working (Dry Run)
- Endpoint: `POST http://localhost:8083/tools/post_to_facebook`
- Supports both text and image posts

### Starting MCP Servers

```bash
# Start all MCP servers
python start_mcp_servers.py

# Or start individually:
python mcp_social_server.py    # Port 8083 - Facebook & Instagram
python mcp_email_server.py     # Port 8080 - Gmail integration
python mcp_browser_server.py   # Port 8081 - Browser automation
python mcp_odoo_server.py      # Port 8082 - Odoo integration
```

### Health Check Endpoints

```bash
# Social Media Server
curl http://localhost:8083/health

# Email Server
curl http://localhost:8080/health

# Browser Server
curl http://localhost:8081/health

# Odoo Server
curl http://localhost:8082/health
```

## Troubleshooting

### Python 3.13 Compatibility
If you encounter `greenlet` build errors, ensure `playwright>=1.42.0` is installed (already in requirements.txt).

### Playwright Browser Issues
```bash
playwright install --force
```

### Gmail Authentication
Delete `token.pickle` and re-run `gmail_watcher.py` to re-authenticate.

### WhatsApp Session Issues
Delete `whatsapp_data/` folder and re-run `whatsapp_watcher.py` to re-authenticate.

### Instagram Post Failing
1. **Check Access Token**: Ensure `INSTAGRAM_ACCESS_TOKEN` is valid (not expired)
2. **Public Image URL**: Instagram requires publicly accessible image URL (not local file path)
3. **Account Type**: Must use Instagram Business or Creator account
4. **Facebook Page Link**: Instagram account must be linked to Facebook Page
5. **Token Permissions**: Access token needs `instagram_basic`, `pages_show_list`, `publish_to_groups`

### Facebook Post Failing
1. **Page Access Token**: Ensure token has `pages_manage_posts` permission
2. **Page ID**: Verify `FACEBOOK_PAGE_ID` is correct
3. **Token Expiry**: Access tokens expire, regenerate from Meta Developer Portal

### No Files in Needs_Action
Ensure `Inbox/` directory exists and watcher.py is running.

### Plans Not Being Created
Run `python reasoning_loop.py` manually to verify it can access `Needs_Action/` directory.

### MCP Server Not Starting
1. Check if port is already in use: `netstat -ano | findstr :8083`
2. Kill existing process or change port in `.env`
3. Ensure all dependencies installed: `pip install -r requirements.txt`

---

**Need Help?** Check `Dashboard.md` for system status and `Audit_Log.md` for activity history.

**Tested On:** Windows 11, Python 3.13, Playwright 1.58.0

**Last Updated:** 2026-02-23

## Quick Reference: Social Media Posting

### Post to Instagram (Dry Run)
```bash
python -c "
import requests
payload = {
    'account_id': 'your_instagram_account_id',
    'caption': 'Your caption here #hashtags',
    'media_path': 'https://example.com/image.jpg',
    'dry_run': True
}
r = requests.post('http://localhost:8083/tools/post_to_instagram', json=payload)
print(r.json())
"
```

### Post to Facebook (Dry Run)
```bash
python -c "
import requests
payload = {
    'page_id': 'your_facebook_page_id',
    'message': 'Your message here',
    'dry_run': True
}
r = requests.post('http://localhost:8083/tools/post_to_facebook', json=payload)
print(r.json())
"
```

### View Posts Log
```bash
# View JSON log of all posts
type Posts_Log.json

# View summary
python -c "
import requests
r = requests.get('http://localhost:8083/tools/generate_summary')
print(r.json())
"
```