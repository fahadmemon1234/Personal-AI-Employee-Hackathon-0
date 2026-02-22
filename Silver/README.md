# AI Agent Silver Tier Implementation

Congratulations! You've reached the Silver Tier of your AI Agent system. This implementation includes enhanced automation with email monitoring, WhatsApp integration, social media automation, agent skills, scheduling, and MCP servers.

## Silver Tier Milestones Achieved

✅ **Agent Skills Conversion**: All automation logic (Gmail, WhatsApp, LinkedIn) converted into official 'Agent Skills'  
✅ **LinkedIn Sales Automation**: Skill to 'Generate and Post LinkedIn Content' analyzes business goals and drafts sales-generating posts  
✅ **Basic Scheduling**: Python-based scheduler runs reasoning_loop.py every 30 minutes  
✅ **HITL Validation**: Verified that no email or social post is sent without approval from /Pending_Approval to /Approved  
✅ **Multi-Watcher Support**: Comprehensive monitoring of Gmail, WhatsApp, and Inbox with unified processing  
✅ **Enhanced Automation**: Automated LinkedIn posting, email processing, and social media engagement  

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
- Configures email-mcp and browser-mcp servers
- Defines server capabilities and settings
- Sets up workflow parameters
- Centralizes configuration for all services

### 13. Auto LinkedIn Poster (auto_linkedin_poster.py) ⭐ NEW
- **Automatically monitors** `Approved/` folder for approval
- **Posts via LinkedIn API** - no browser window opens
- **Auto re-authenticates** when token expires
- **Posts all pending posts** sequentially
- **Zero manual intervention** after approval

### 14. Start Monitor (start_monitor.py) ⭐ NEW
- Simple wrapper to start the auto-poster monitor
- Shows current status (token, pending posts, approval)
- Runs continuously in background

## Quick Start - Auto LinkedIn Posting

**Jab approval mile, automatically posts honge!**

1. **Start the monitor** (background mein):
   ```bash
   python start_monitor.py
   ```

2. **Jab approval mile**, bas `Approved/` folder mein koi file create karein:
   ```bash
   echo approved > Approved/approve.txt
   ```

3. **Automatic process**:
   - ✅ Monitor approval detect karega
   - ✅ Token expire ho to auto re-authenticate hoga
   - ✅ Saare pending posts LinkedIn par honge
   - ✅ Koi browser window nahi khulega
   - ✅ Dashboard update ho jayega

**Commands:**
```bash
python auto_linkedin_poster.py --status     # Check current status
python auto_linkedin_poster.py --once       # Check once for approval
python auto_linkedin_poster.py --post-now   # Post immediately (bypass approval)
python start_monitor.py                     # Start continuous monitoring
```

## Setup Instructions

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install schedule
   pip install python-dotenv
   ```

2. Install Playwright browsers:
   ```bash
   playwright install chromium
   ```

3. Set up environment variables:
   - Copy the `.env` file in the root directory
   - Update the following variables:
     ```bash
     GOOGLE_CLIENT_ID=your_client_id_here
     GOOGLE_CLIENT_SECRET=your_client_secret_here
     GMAIL_CREDENTIALS_FILE=credentials.json
     GMAIL_TOKEN_FILE=token.pickle
     LINKEDIN_API_KEY=your_linkedin_api_key_here
     LINKEDIN_API_SECRET=your_linkedin_api_secret_here
     ```

4. Set up Google API credentials (for Gmail watcher):
   - Go to https://console.cloud.google.com/apis/credentials
   - Create credentials for Gmail API
   - Download the credentials.json file and place it in the root directory

5. Run the complete system:
   ```bash
   # Run the scheduler to process requests every 30 minutes
   python scheduler.py
   
   # Or run individual components:
   python watcher.py              # Monitor Inbox folder
   python gmail_watcher.py        # Monitor Gmail
   python whatsapp_watcher.py     # Monitor WhatsApp for keywords
   python reasoning_loop.py       # Process requests with reasoning
   python linkedin_poster.py      # Generate and post LinkedIn content
   python email_approval_workflow.py  # Handle email sending with approval
   python agent_interface.py      # Coordinate all agent skills
   ```

5. Place files in the `Inbox` folder or receive emails/WhatsApp messages to be automatically processed

## Directory Structure
```
├── Dashboard.md              # Main dashboard showing status and tasks
├── Company_Handbook.md       # Rules of engagement and operational guidelines
├── watcher.py               # Python script that monitors Inbox folder
├── gmail_watcher.py         # Python script that monitors Gmail
├── whatsapp_watcher.py      # Python script that monitors WhatsApp Web
├── reasoning_loop.py        # Implements reasoning loop for requests
├── linkedin_poster.py       # Generates and posts LinkedIn content
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
│       ├── whatsapp_skill/
│       │   ├── SKILL.md     # WhatsApp skill documentation
│       │   └── whatsapp_skill.py # WhatsApp skill implementation
│       └── linkedin_skill/
│           ├── SKILL.md     # LinkedIn skill documentation
│           └── linkedin_skill.py # LinkedIn skill implementation
├── Inbox/                  # Folder monitored by the watcher
├── Needs_Action/           # Destination for files moved by watcher
├── Pending_Approval/       # Directory for items awaiting approval
├── Approved/               # Directory for approved items
├── Posted/                 # Directory for executed LinkedIn posts
├── Sent/                   # Directory for sent emails
├── Plans/                  # Directory for generated action plans
├── Completed/              # Directory for completed requests
└── watcher_log.txt         # Log of all file movements
```

## Usage

1. **Basic Operation**: Place any files you want processed in the `Inbox` folder
2. **Email Monitoring**: Configure Gmail credentials to monitor emails automatically
3. **WhatsApp Monitoring**: Log in to WhatsApp Web once, then monitor for keywords
4. **Request Processing**: The reasoning loop will create plans for requests in `Needs_Action`
5. **Approval Workflow**: Move files from `Pending_Approval` to `Approved` directory to approve actions
6. **LinkedIn Posts**: Drafts are created in `Pending_Approval`, move to `Approved` to post
7. **Check logs**: Review `watcher_log.txt` and `Dashboard.md` for records of all actions
8. **Update dashboard**: Update `Dashboard.md` with current information as needed

## MCP Servers

### Email-MCP Server
- Port: 8080
- Capabilities: send-email, receive-email, process-email, gmail-watch, email-approval
- Handles all email-related operations with approval workflow

### Browser-MCP Server
- Port: 8081
- Capabilities: browse-web, scrape-content, automate-browser, social-media-post, web-interaction, whatsapp-monitor
- Manages web browsing, social media automation, and WhatsApp monitoring tasks

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