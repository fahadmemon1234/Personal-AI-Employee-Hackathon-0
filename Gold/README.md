# AI Agent Gold Tier Implementation - Autonomous Employee

🏆 **Gold Tier Achievement Unlocked!**

This is a fully autonomous AI employee system with cross-domain integration, social media automation, accounting integration, and comprehensive audit logging.

## Gold Tier Features Achieved

✅ **All Silver Requirements** - Gmail, WhatsApp, LinkedIn automation with HITL validation
✅ **Full Cross-Domain Integration** - Personal (Gmail/WhatsApp) + Business (Odoo ERP)
✅ **Odoo Accounting Integration** - Self-hosted Odoo Community via JSON-RPC MCP server
✅ **Facebook & Instagram Integration** - Post content and generate performance summaries
✅ **Twitter (X) Integration** - Post tweets/threads and generate analytics summaries
✅ **Multiple MCP Servers** - 5 specialized servers (Email, Browser, Odoo, Twitter, Facebook/Instagram)
✅ **Weekly CEO Briefing** - Automated business and accounting audit reports
✅ **Error Recovery & Graceful Degradation** - Comprehensive exception handling
✅ **Comprehensive Audit Logging** - All actions logged to Audit_Log.md
✅ **Ralph Wiggum Loop** - Autonomous multi-step task completion (up to 5 iterations)
✅ **Architecture Documentation** - Complete ARCHITECTURE.md and LESSONS_LEARNED.md
✅ **Agent Skills Framework** - All AI functionality implemented as modular skills

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

### 8. LinkedIn Poster (linkedin_poster.py)
- Generates daily LinkedIn updates about AI services
- Creates draft posts in `/Pending_Approval` before posting
- Executes posts when moved to `/Approved` directory
- Logs all LinkedIn activity in `Dashboard.md`

### 9. Agent Skills Framework
- **Gmail Skill** (`.qwen/skills/gmail_skill/`): Monitors Gmail for new emails and processes them
- **WhatsApp Skill** (`.qwen/skills/whatsapp_skill/`): Monitors WhatsApp for new messages and processes them
- **LinkedIn Skill** (`.qwen/skills/linkedin_skill/`): Generates and posts LinkedIn content for sales
- **Facebook/Instagram Skill** (`.qwen/skills/facebook_instagram_skill/`): Posts to Facebook/Instagram and generates summaries
- **Twitter Skill** (`.qwen/skills/twitter_skill/`): Posts tweets/threads and generates Twitter analytics
- **CEO Briefing Skill** (`ceo_briefing_skill.py`): Generates weekly business audit reports

### 10. Scheduler (scheduler.py)
- Python-based scheduler that runs reasoning_loop.py every 30 minutes
- Ensures continuous monitoring and processing of requests
- Handles timeouts and error recovery

### 11. Agent Interface (agent_interface.py)
- Coordinates all agent skills
- Enforces HITL validation
- Validates that no actions are taken without proper approval
- Monitors for approved items and executes them

### 12. MCP Configuration (mcp.json)
- Configures all MCP servers (Email, Browser, Odoo, Twitter, Facebook/Instagram)
- Defines server capabilities and settings
- Centralizes configuration for all services

### 13. Social Media Integration (`social_media_integration/`)
- **facebook_instagram_connector.py**: Meta Graph API connector
- **facebook_instagram_mcp_server.py**: Facebook/Instagram MCP server (Port 8084)
- **twitter_connector.py**: Twitter API v2 connector
- **twitter_mcp_server.py**: Twitter MCP server (Port 8083)

### 14. Documentation
- **ARCHITECTURE.md**: Comprehensive system architecture documentation
- **LESSONS_LEARNED.md**: Implementation learnings and best practices
- **Company_Handbook.md**: Rules of engagement and operational guidelines

## Setup Instructions

### Prerequisites

1. **Install Python 3.10+**

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Playwright browsers:**
   ```bash
   playwright install chromium
   ```

### Configure Credentials

#### Google/Gmail
- Go to https://console.cloud.google.com/apis/credentials
- Create credentials for Gmail API
- Download `credentials.json` and place it in the root directory

#### Meta (Facebook/Instagram)
- Go to https://developers.facebook.com/
- Create an app and get Access Token
- Set environment variables:
  ```bash
  set META_ACCESS_TOKEN=your_token
  set FACEBOOK_PAGE_ID=your_page_id
  set INSTAGRAM_BUSINESS_ACCOUNT_ID=your_ig_account_id
  ```

#### Twitter (X)
- Go to https://developer.twitter.com/
- Apply for developer account and create an app
- Set environment variables:
  ```bash
  set TWITTER_API_KEY=your_key
  set TWITTER_API_SECRET=your_secret
  set TWITTER_ACCESS_TOKEN=your_token
  set TWITTER_ACCESS_TOKEN_SECRET=your_secret
  ```

#### Odoo
- Configure your Odoo instance
- Set environment variables:
  ```bash
  set ODOO_URL=http://your-odoo-url.com
  set ODOO_DB=your_database
  set ODOO_USERNAME=your_email
  set ODOO_PASSWORD=your_password
  ```

### Run the System

#### Option 1: Run Complete System (Recommended)
```bash
# Run the scheduler to process requests every 30 minutes
python scheduler.py
```

#### Option 2: Run Individual Components
```bash
python watcher.py              # Monitor Inbox folder
python gmail_watcher.py        # Monitor Gmail
python whatsapp_watcher.py     # Monitor WhatsApp
python reasoning_loop.py       # Process requests with reasoning
python linkedin_poster.py      # Generate and post LinkedIn content
python email_approval_workflow.py  # Handle email sending with approval
python agent_interface.py      # Coordinate all agent skills
```

#### Option 3: Run MCP Servers
```bash
# Odoo MCP Server (Port 8082)
python odoo_integration/mcp_server.py

# Twitter MCP Server (Port 8083)
python social_media_integration/twitter_mcp_server.py

# Facebook/Instagram MCP Server (Port 8084)
python social_media_integration/facebook_instagram_mcp_server.py
```

#### Option 4: Run with PM2 (Production)
```bash
# Install PM2
npm install -g pm2

# Start all services
pm2 start ecosystem.config.js

# Or start individual services
pm2 start ecosystem.config.js --only odoo-mcp-server
pm2 start ecosystem.config.js --only twitter-mcp-server
pm2 start ecosystem.config.js --only facebook-instagram-mcp-server
```

#### Option 5: Use Agent Skills
```bash
# Generate CEO Briefing
python ceo_briefing_skill.py

# Post to Twitter
python .qwen/skills/twitter_skill/twitter_skill.py --action post-tweet --text "Hello Twitter!"

# Post to Facebook
python .qwen/skills/facebook_instagram_skill/facebook_instagram_skill.py --action post-facebook --message "Hello Facebook!"

# Generate social media summary
python .qwen/skills/twitter_skill/twitter_skill.py --action summary --days 7
python .qwen/skills/facebook_instagram_skill/facebook_instagram_skill.py --action summary --days 7
```

## Directory Structure
```
├── Dashboard.md              # Main dashboard showing status and tasks
├── Company_Handbook.md       # Rules of engagement and operational guidelines
├── ARCHITECTURE.md           # System architecture documentation
├── LESSONS_LEARNED.md        # Implementation learnings and best practices
├── README.md                 # This file
├── watcher.py                # Python script that monitors Inbox folder
├── gmail_watcher.py          # Python script that monitors Gmail
├── whatsapp_watcher.py       # Python script that monitors WhatsApp Web
├── reasoning_loop.py         # Implements reasoning loop (Ralph Wiggum pattern)
├── linkedin_poster.py        # Generates and posts LinkedIn content
├── email_approval_workflow.py # Handles email sending with approval
├── scheduler.py              # Runs reasoning_loop.py every 30 minutes
├── agent_interface.py        # Coordinates all agent skills
├── ceo_briefing_skill.py     # Generates weekly CEO briefings
├── mcp.json                  # Configuration for MCP servers
├── ecosystem.config.js       # PM2 configuration
├── requirements.txt          # Python dependencies
├── .qwen/
│   └── skills/               # Agent skills directory
│       ├── gmail_skill/
│       ├── whatsapp_skill/
│       ├── linkedin_skill/
│       ├── facebook_instagram_skill/
│       ├── twitter_skill/
│       └── (ceo_briefing_skill.py)
├── social_media_integration/ # Social media connectors and MCP servers
│   ├── facebook_instagram_connector.py
│   ├── facebook_instagram_mcp_server.py
│   ├── twitter_connector.py
│   └── twitter_mcp_server.py
├── odoo_integration/         # Odoo integration
│   ├── odoo_connector.py
│   ├── mcp_server.py
│   ├── sync_invoices.py
│   └── update_dashboard_with_odoo.py
├── Inbox/                    # Folder monitored by the watcher
├── Needs_Action/             # Destination for files moved by watcher
├── Pending_Approval/         # Directory for items awaiting approval
├── Approved/                 # Directory for approved items
├── Completed/                # Directory for completed requests
├── Social_Media_Summaries/   # Social media performance reports
├── Briefings/                # CEO briefing reports
├── Bank_Transactions/        # Financial transaction data
└── Audit_Log.md              # Comprehensive audit log
```

## Usage

### Basic Operation
1. **Place files in `/Inbox`** to be automatically processed
2. **Configure email credentials** to monitor Gmail automatically
3. **Log in to WhatsApp Web** once for persistent session
4. **Review plans** created in `/Needs_Action` folder
5. **Approve actions** by moving files from `/Pending_Approval` to `/Approved`
6. **Check logs** in `Audit_Log.md` and `Dashboard.md`

### MCP Servers

| Server | Port | Purpose |
|--------|------|---------|
| Email-MCP | 8080 | Email operations and Gmail integration |
| Browser-MCP | 8081 | Web browsing and automation |
| Odoo-MCP | 8082 | Accounting and ERP integration |
| Twitter-MCP | 8083 | Twitter posting and analytics |
| Facebook/Instagram-MCP | 8084 | Meta platforms integration |

### Agent Skills

All AI functionality is implemented as modular Agent Skills:

| Skill | Location | Purpose |
|-------|----------|---------|
| Gmail | `.qwen/skills/gmail_skill/` | Monitor and process Gmail |
| WhatsApp | `.qwen/skills/whatsapp_skill/` | Monitor and process WhatsApp |
| LinkedIn | `.qwen/skills/linkedin_skill/` | Generate and post LinkedIn content |
| Facebook/Instagram | `.qwen/skills/facebook_instagram_skill/` | Post and analyze Meta platforms |
| Twitter | `.qwen/skills/twitter_skill/` | Post tweets and generate analytics |
| CEO Briefing | `ceo_briefing_skill.py` | Generate weekly business audits |

### Weekly CEO Briefing

Generate comprehensive business reports every Monday:

```bash
python ceo_briefing_skill.py
```

The briefing includes:
- Financial Summary (Income vs Expense)
- Odoo Financial Data (Revenue, Outstanding Invoices)
- Bottleneck Analysis (Tasks over 48 hours)
- Proactive Business Suggestions
- Action Items

### Social Media Management

#### Post to Social Media
```bash
# Twitter
python .qwen/skills/twitter_skill/twitter_skill.py --action post-tweet --text "Your tweet here"

# Facebook
python .qwen/skills/facebook_instagram_skill/facebook_instagram_skill.py --action post-facebook --message "Your message"

# Instagram
python .qwen/skills/facebook_instagram_skill/facebook_instagram_skill.py --action post-instagram --caption "Caption" --image-url "https://example.com/image.jpg"
```

#### Generate Performance Summaries
```bash
# Twitter Summary
python .qwen/skills/twitter_skill/twitter_skill.py --action summary --days 7

# Facebook/Instagram Summary
python .qwen/skills/facebook_instagram_skill/facebook_instagram_skill.py --action summary --days 7
```

Summaries are saved to `Social_Media_Summaries/` folder.

### Audit Trail

All actions are logged to `Audit_Log.md` with:
- Timestamp
- Action type
- Success/Failure status
- Component name

Review the audit log regularly for system monitoring.

## Agent Skill Implementation

The system is designed to proactively read from and write to your vault (the current directory):

- **Reading**: The watchers monitor Inbox, Gmail, and WhatsApp continuously
- **Writing**: Files are moved between folders, logs are written, and dashboards can be updated
- **Automation**: Multiple systems operate independently once started
- **Reasoning**: The reasoning loop creates plans and waits for approval before acting
- **Safety**: All email sending and social posts require explicit approval to prevent unauthorized actions
- **Social Media**: WhatsApp messages with important keywords trigger notifications to the agent
- **Scheduling**: The scheduler ensures continuous processing every 30 minutes
- **Skills**: Agent skills provide modular, reusable functionality for different platforms