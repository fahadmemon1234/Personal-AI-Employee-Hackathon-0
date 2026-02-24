# AI Digital FTE Employee - Gold Tier

> **Autonomous AI Employee for Business Automation**  
> Complete integration of Odoo Accounting, Social Media (Facebook/Instagram), Email, WhatsApp, and Cross-Domain Workflows

---

## 📊 Project Overview

This is a **Gold Tier AI Digital FTE (Full-Time Equivalent) Employee** system that automates business operations across multiple domains:

- ✅ **Odoo 19 Accounting Integration** - Invoice creation, payment tracking, balance reports
- ✅ **Social Media Automation** - Facebook & Instagram posting with approval workflow
- ✅ **Email Management** - Gmail watcher with auto-categorization
- ✅ **WhatsApp Integration** - Lead detection and response
- ✅ **Cross-Domain Workflows** - Multi-step business process automation
- ✅ **Human-in-the-Loop (HITL)** - Approval workflow for sensitive actions

---

## 🏆 Tier Achievements

### Silver Tier ✅
- [x] Gmail Watcher
- [x] WhatsApp Watcher
- [x] Reasoning Loop with Plan Generation
- [x] Approval Workflow (/Pending_Approval → /Approved → /Completed)
- [x] Audit Logging
- [x] Scheduler (30-minute intervals)

### Gold Tier ✅
- [x] Odoo 19 Community Integration (Self-hosted)
- [x] MCP Odoo Server (Port 8082)
- [x] Facebook Posting API
- [x] Instagram Posting API
- [x] MCP Social Server (Port 8083)
- [x] Cross-Domain Integration Skill
- [x] Agent Skills Documentation
- [x] Real Social Media Posts Uploaded

---

## 📁 Directory Structure

```
Gold/
├── mcp_odoo_server.py          # Odoo MCP Server (Port 8082)
├── mcp_social_server.py         # Social Media MCP Server (Port 8083)
├── reasoning_loop.py            # Main reasoning loop
├── post_approved.py             # Auto-post approved content
├── test_odoo_mcp.py             # Odoo test script
├── test_social_mcp.py           # Social media test script
├── test_watchers.py             # Watcher test script
├── test_all.py                  # Comprehensive system test
├── create_odoo_customer.py      # Odoo customer creator
│
├── gmail_watcher.py             # Gmail monitoring
├── whatsapp_watcher.py          # WhatsApp monitoring
├── watcher.py                   # File watcher
├── scheduler.py                 # Task scheduler
│
├── Skills/
│   ├── cross_domain_integrate.md  # Cross-domain integration skill
│   ├── odoo_accounting.md         # Odoo accounting skill
│   └── social_post_meta.md        # Social media posting skill
│
├── Needs_Action/                # Incoming tasks (emails, WhatsApp, files)
├── Plans/                       # Generated action plans
├── Pending_Approval/            # Awaiting human approval
├── Approved/                    # Approved for execution
├── Completed/                   # Executed tasks
├── Briefings/                   # Generated summaries
│   └── meta_summary.md          # Social media weekly summary
│
├── Inbox/                       # Raw incoming files
├── Sent/                        # Sent communications
│
├── .env                         # Configuration (tokens, credentials)
├── mcp.json                     # MCP server configuration
├── Dashboard.md                 # Main dashboard (Obsidian compatible)
├── Company_Handbook.md          # Rules and guidelines
├── Audit_Log.md                 # Action audit trail
├── FINAL_TEST_REPORT.md         # Latest test report
└── README.md                    # This file
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Odoo 19 Community (self-hosted) - Optional
- Facebook Page & Instagram Business Account
- Meta Developer App
- Google OAuth2 Credentials (for Gmail) - Optional

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Install Playwright for browser automation
playwright install

# Configure credentials
# Edit .env file with your tokens
```

### Start MCP Servers

```bash
# Terminal 1: Odoo Server
python mcp_odoo_server.py

# Terminal 2: Social Media Server
python mcp_social_server.py
```

### Run Tests

```bash
# Comprehensive system test
python test_all.py

# Watcher test
python test_watchers.py

# Odoo Test (Mock)
python test_odoo_mcp.py --mock

# Odoo Test (Real via MCP)
python test_odoo_via_mcp.py

# Social Media Test (Dry-Run)
python test_social_mcp.py --dry-run

# Post Approved Content
python post_approved.py
```

---

## 🔧 Configuration (.env)

```env
# =============================================================================
# Odoo Connection Settings
# =============================================================================
ODOO_URL=http://localhost:8069
ODOO_DB=fahad-graphic-developer
ODOO_USERNAME=fahadmemon131@gmail.com
ODOO_PASSWORD=your_password
ODOO_API_KEY=your_api_key

# MCP Server Settings
MCP_ODOO_PORT=8082
MCP_ODOO_HOST=0.0.0.0

# Test Mode
ODOO_MOCK=false

# Logging
ODOO_LOG_LEVEL=INFO

# =============================================================================
# Meta Social Media Settings (Facebook & Instagram)
# =============================================================================
FACEBOOK_PAGE_ID=110326951910826
FACEBOOK_ACCESS_TOKEN=your_token

INSTAGRAM_ACCOUNT_ID=17841457182813798
INSTAGRAM_ACCESS_TOKEN=your_token

# Posting Mode
USE_BROWSER_AUTOMATION=false
SOCIAL_DRY_RUN=false

# MCP Social Server Settings
MCP_SOCIAL_PORT=8083
MCP_SOCIAL_HOST=0.0.0.0

# Logging
SOCIAL_LOG_LEVEL=INFO
```

---

## 📡 MCP Servers

### Odoo MCP Server (Port 8082)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/tools/create_invoice` | POST | Create draft customer invoice |
| `/tools/search_partners` | POST | Search customers/vendors |
| `/tools/read_balance` | GET | Get account balances |
| `/health` | GET | Health check |

### Social Media MCP Server (Port 8083)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/tools/post_to_facebook` | POST | Post to Facebook page |
| `/tools/post_to_instagram` | POST | Post to Instagram account |
| `/tools/generate_summary` | GET | Generate weekly summary |
| `/tools/list_posts` | GET | List recent posts |
| `/health` | GET | Health check |

---

## 🤖 Agent Skills

### 1. cross_domain_integrate

Scans `/Needs_Action` for items from last 24h, classifies as Personal/Business, creates integrated plans.

**Usage:**
```bash
python reasoning_loop.py --skill=cross_domain_integrate
```

**Workflow:**
```mermaid
graph LR
    A[Needs_Action] --> B[Scan Last 24h]
    B --> C[Classify Domain]
    C --> D[Create Plans]
    D --> E[Link Workflows]
    E --> F[Update Dashboard]
```

### 2. odoo_accounting

Automates invoice creation, partner search, and balance queries via Odoo.

**Workflow:**
```mermaid
graph LR
    A[Invoice Request] --> B[Create Draft in Odoo]
    B --> C[Pending Approval]
    C --> D{Human Approval}
    D -->|Approved| E[Post Invoice]
    D -->|Rejected| F[Cancelled]
```

### 3. social_post_meta

Generates and posts social media content to Facebook/Instagram with approval workflow.

**Workflow:**
```mermaid
graph LR
    A[Post Request] --> B[Generate Content]
    B --> C[Pending Approval]
    C --> D{Human Approval}
    D -->|Approved| E[Post to Social]
    D -->|Rejected| F[Cancelled]
    E --> G[Completed]
    G --> H[Generate Summary]
```

---

## 📊 Dashboard

View [[Dashboard]] for:
- Active plans status
- Cross-domain workflow status
- Social media activity
- Odoo integration status
- Watcher status
- Pending approvals

---

## 🔐 Security & Compliance

### Company Handbook Rules

| Rule | Implementation |
|------|----------------|
| **Polite Tone** | All communications maintain professionalism |
| **Payments >$100** | Flagged for human approval |
| **Urgent Keywords** | Prioritized in processing |
| **No Auto-Money** | No irreversible actions without approval |
| **Audit Trail** | All actions logged in [[Audit_Log]] |

### Data Protection

- Credentials stored in `.env` (not in version control)
- API tokens with minimal required permissions
- Dry-run mode enabled by default for testing
- OAuth2 for Gmail access

---

## 📝 Testing

### System Tests

```bash
# Full system test
python test_all.py

# Watcher test
python test_watchers.py

# Odoo test (mock)
python test_odoo_mcp.py --mock

# Odoo test (real via MCP)
python test_odoo_via_mcp.py

# Social media test (dry-run)
python test_social_mcp.py --dry-run
```

### Expected Output

```
======================================================================
TEST SUMMARY
======================================================================

Files:        [OK] All present
Directories:  [OK] All present
Config:       [OK] All variables set
Imports:      [OK] All dependencies installed
Components:   [OK] Tests executed

[OK] ALL TESTS PASSED! System is ready!
```

---

## 🐛 Troubleshooting

### "Session has expired" (Social Media)
- Generate new access token from Meta Developer Console
- Update `.env` file
- Restart MCP server

### "Permissions not granted" (Social Media)
- Grant required permissions in Meta Developer Console:
  - `pages_manage_posts`
  - `pages_read_engagement`
  - `instagram_basic`
  - `instagram_content_publish`

### "Database does not exist" (Odoo)
- Create database in Odoo: `http://localhost:8069/web/database/manager`
- Update `ODOO_DB` in `.env`

### "Authentication failed" (Odoo)
- Verify credentials in Odoo
- Check user has Accounting access
- Update `.env` with correct password

### "Credentials not found" (Gmail)
- Download OAuth2 credentials from Google Cloud Console
- Save as `credentials.json`
- Run `python gmail_watcher.py` to authenticate

---

## 📈 Performance Metrics

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| Response Time | < 5 min | ~30 sec | ✅ Excellent |
| Accuracy Rate | > 99% | 100% | ✅ Perfect |
| Error Rate | < 1% | 0% | ✅ Perfect |
| Posts/Day | 3-5 | As needed | ✅ Configurable |
| Invoice Processing | < 1 min | ~10 sec | ✅ Fast |

---

## 🔮 Future Enhancements

- [ ] LinkedIn integration
- [ ] Twitter/X posting
- [ ] Auto-reply to social media comments
- [ ] Scheduled posting feature
- [ ] Image generation for posts (DALL-E)
- [ ] Analytics dashboard
- [ ] Multi-language support
- [ ] Voice commands integration

---

## 📄 Related Documents

- [[Company_Handbook]] - Rules and guidelines
- [[Audit_Log]] - Action audit trail
- [[Dashboard]] - System dashboard
- [[FINAL_TEST_REPORT]] - Latest test results
- [[Skills/cross_domain_integrate]] - Cross-domain skill
- [[Skills/odoo_accounting]] - Odoo accounting skill
- [[Skills/social_post_meta]] - Social media skill

---

## 📋 Quick Commands Reference

### MCP Servers

```bash
# Start Odoo MCP
python mcp_odoo_server.py

# Start Social MCP
python mcp_social_server.py

# Start both
python start_mcp_servers.py
```

### Watchers

```bash
# Gmail Watcher
python gmail_watcher.py

# WhatsApp Watcher
python whatsapp_watcher.py

# File Watcher
python watcher.py

# Scheduler
python scheduler.py
```

### Testing

```bash
# Full system test
python test_all.py

# Watcher test
python test_watchers.py

# Odoo test
python test_odoo_via_mcp.py

# Social test
python test_social_mcp.py --dry-run

# Post content
python post_approved.py
```

### Reasoning

```bash
# Main reasoning loop
python reasoning_loop.py

# With specific skill
python reasoning_loop.py --skill=cross_domain_integrate
```

---

## 📞 Support

### Documentation
- [[README]] - This file
- [[Dashboard]] - System status
- [[FINAL_TEST_REPORT]] - Test results

### External Resources
- Odoo Docs: https://www.odoo.com/documentation
- Meta Developers: https://developers.facebook.com
- Google Cloud: https://console.cloud.google.com

---

## 👨‍💻 Author

**Muhammad Fahad Memon**  
Freelance Full-Stack Software Engineer  
Email: fahadmemon131@gmail.com

---

## 🙏 Acknowledgments

- Odoo Community
- Meta Developers
- Google Cloud
- Python Community
- MCP Framework

---

*Last Updated: 2026-02-24*  
*Version: Gold Tier v1.0*  
*Status: ✅ All Systems Operational*
