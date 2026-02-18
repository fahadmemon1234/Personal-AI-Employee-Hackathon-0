# AI Agent Gold Tier - System Architecture

## Overview

This document describes the architecture of the Gold Tier AI Agent system - an autonomous employee system that integrates personal communication, business accounting, and social media management through a modular MCP (Model Context Protocol) server architecture.

![Architecture Diagram](#architecture-diagram-description-below)

---

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Component Overview](#component-overview)
3. [MCP Servers](#mcp-servers)
4. [Agent Skills Framework](#agent-skills-framework)
5. [Data Flow](#data-flow)
6. [Directory Structure](#directory-structure)
7. [Integration Patterns](#integration-patterns)
8. [Security Architecture](#security-architecture)
9. [Error Handling & Recovery](#error-handling--recovery)
10. [Scalability Considerations](#scalability-considerations)

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         AI AGENT GOLD TIER SYSTEM                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐               │
│  │   Gmail      │    │  WhatsApp    │    │   LinkedIn   │               │
│  │   Watcher    │    │   Watcher    │    │    Poster    │               │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘               │
│         │                   │                   │                        │
│         └───────────────────┼───────────────────┘                        │
│                             │                                            │
│                             ▼                                            │
│                  ┌──────────────────┐                                   │
│                  │  Needs_Action    │                                   │
│                  │     Folder       │                                   │
│                  └────────┬─────────┘                                   │
│                           │                                              │
│                           ▼                                              │
│  ┌──────────────────────────────────────────────────────────┐           │
│  │           REASONING LOOP (Ralph Wiggum Pattern)          │           │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │           │
│  │  │   Analyze   │→ │   Create    │→ │   Execute   │      │           │
│  │  │   Request   │  │   Plan.md   │  │   Actions   │      │           │
│  │  └─────────────┘  └─────────────┘  └─────────────┘      │           │
│  │         ↑                │                  │            │           │
│  │         │                ↓                  │            │           │
│  │         │         ┌─────────────┐          │            │           │
│  │         └──────── │  HITL Check │ ←────────┘            │           │
│  │                   │  (Approval) │                       │           │
│  │                   └─────────────┘                       │           │
│  └──────────────────────────────────────────────────────────┘           │
│                           │                                              │
│                           ▼                                              │
│  ┌──────────────────────────────────────────────────────────┐           │
│  │              AGENT SKILLS ORCHESTRATOR                   │           │
│  └──────────────────────────────────────────────────────────┘           │
│                           │                                              │
│         ┌─────────────────┼─────────────────┐                           │
│         │                 │                 │                           │
│         ▼                 ▼                 ▼                           │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐                   │
│  │   Odoo      │   │  Facebook/  │   │   Twitter   │                   │
│  │     MCP     │   │ Instagram   │   │     MCP     │                   │
│  │  (Port 8082)│   │     MCP     │   │  (Port 8083)│                   │
│  │             │   │  (Port 8084)│   │             │                   │
│  └─────────────┘   └─────────────┘   └─────────────┘                   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Component Overview

### Core Components

| Component | Purpose | Technology |
|-----------|---------|------------|
| **Watcher Scripts** | Monitor external platforms for new content | Python + APIs |
| **Reasoning Loop** | Autonomous decision-making with HITL validation | Python |
| **Agent Skills** | Modular action implementations | Python + MCP |
| **MCP Servers** | Standardized API interfaces | aiohttp + JSON-RPC |
| **Scheduler** | Time-based task execution | schedule library |
| **Audit Logger** | Comprehensive action tracking | Markdown files |

### Communication Platforms

| Platform | Integration Method | Purpose |
|----------|-------------------|---------|
| Gmail | Google API v3 | Email monitoring |
| WhatsApp | Playwright + Web | Message monitoring |
| LinkedIn | Browser automation | Content posting |
| Facebook | Meta Graph API v18 | Social media management |
| Instagram | Meta Graph API v18 | Social media management |
| Twitter (X) | Twitter API v2 | Tweet management |

### Business Systems

| System | Integration Method | Purpose |
|--------|-------------------|---------|
| Odoo | JSON-RPC (XML-RPC) | Accounting & ERP |
| Bank Transactions | File parsing | Financial tracking |

---

## MCP Servers

### What is MCP?

Model Context Protocol (MCP) is a standardized protocol for AI agents to interact with external systems through well-defined APIs.

### Server Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                      MCP SERVER LAYER                         │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │   Email     │  │   Browser   │  │    Odoo     │          │
│  │     MCP     │  │     MCP     │  │     MCP     │          │
│  │  Port 8080  │  │  Port 8081  │  │  Port 8082  │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
│                                                               │
│  ┌─────────────────┐  ┌─────────────────┐                    │
│  │ Facebook/       │  │    Twitter      │                    │
│  │ Instagram MCP   │  │      MCP        │                    │
│  │   Port 8084     │  │   Port 8083     │                    │
│  └─────────────────┘  └─────────────────┘                    │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

### MCP Server Details

#### 1. Email MCP Server (Port 8080)
- **Purpose**: Email operations and Gmail integration
- **Endpoints**:
  - `POST /send-email` - Send emails
  - `GET /receive-email` - Fetch emails
  - `POST /process-email` - Process incoming emails
  - `GET /gmail-watch` - Monitor Gmail
- **Authentication**: Google OAuth 2.0

#### 2. Browser MCP Server (Port 8081)
- **Purpose**: Web automation and scraping
- **Endpoints**:
  - `POST /browse-web` - Navigate to URLs
  - `GET /scrape-content` - Extract web content
  - `POST /automate-browser` - Execute browser automation
  - `POST /social-media-post` - Post to social platforms
- **Technology**: Playwright (Chromium)

#### 3. Odoo MCP Server (Port 8082)
- **Purpose**: Accounting and ERP integration
- **Endpoints**:
  - `GET /financial/records` - Get financial data
  - `POST /invoices/sync` - Sync invoices to Odoo
  - `GET /financial/outstanding` - Get outstanding invoices
  - `GET /financial/monthly-revenue` - Get monthly revenue
- **Protocol**: Odoo JSON-RPC API v19+

#### 4. Twitter MCP Server (Port 8083)
- **Purpose**: Twitter (X) integration
- **Endpoints**:
  - `POST /post/tweet` - Post a tweet
  - `POST /post/thread` - Post a thread
  - `GET /metrics/user` - Get user metrics
  - `GET /metrics/tweet` - Get tweet metrics
  - `GET /summary` - Generate performance summary
- **Authentication**: Twitter OAuth 2.0

#### 5. Facebook/Instagram MCP Server (Port 8084)
- **Purpose**: Meta platforms integration
- **Endpoints**:
  - `POST /post/facebook` - Post to Facebook
  - `POST /post/instagram` - Post to Instagram
  - `GET /insights/facebook` - Get Facebook insights
  - `GET /insights/instagram` - Get Instagram insights
  - `GET /summary` - Generate combined summary
- **Authentication**: Meta Graph API OAuth

---

## Agent Skills Framework

### Skills Architecture

```
.qwen/skills/
├── gmail_skill/
│   ├── SKILL.md           # Documentation
│   └── gmail_skill.py     # Implementation
├── whatsapp_skill/
│   ├── SKILL.md
│   └── whatsapp_skill.py
├── linkedin_skill/
│   ├── SKILL.md
│   └── linkedin_skill.py
├── facebook_instagram_skill/
│   ├── SKILL.md
│   └── facebook_instagram_skill.py
├── twitter_skill/
│   ├── SKILL.md
│   └── twitter_skill.py
└── ceo_briefing_skill/
    └── ceo_briefing_skill.py
```

### Skill Interface

Each skill implements a standard interface:

```python
def skill_action(parameters) -> dict:
    """
    Standard skill action interface
    
    Returns:
        {
            "success": bool,
            "error": str (optional),
            "data": dict (optional),
            "skill": str
        }
    """
```

### Skill Registration

Skills are auto-discovered from the `.qwen/skills/` directory by the agent interface.

---

## Data Flow

### Request Processing Flow

```
1. External Trigger (Email/Message/File)
           │
           ▼
2. Watcher detects and saves to /Needs_Action
           │
           ▼
3. Reasoning Loop reads /Needs_Action
           │
           ▼
4. Creates Plan.md with proposed actions
           │
           ▼
5. Checks if HITL approval required
           │
     ┌─────┴─────┐
     │           │
    Yes         No
     │           │
     ▼           │
6a. Wait    6b. Execute immediately
    for          │
    Approval     │
     │           │
     ▼           │
7. Move to /Approved ◄────┘
           │
           ▼
8. Agent Interface executes approved actions
           │
           ▼
9. Log to Audit_Log.md
           │
           ▼
10. Move to /Completed
```

### Approval Workflow

```
/Needs_Action → [Plan Created] → /Pending_Approval → [User Moves] → /Approved → [Execute] → /Completed
```

---

## Directory Structure

```
Gold/
├── .qwen/
│   └── skills/                    # Agent Skills
│       ├── gmail_skill/
│       ├── whatsapp_skill/
│       ├── linkedin_skill/
│       ├── facebook_instagram_skill/
│       ├── twitter_skill/
│       └── ceo_briefing_skill/
├── social_media_integration/      # Social media connectors
│   ├── facebook_instagram_connector.py
│   ├── facebook_instagram_mcp_server.py
│   ├── twitter_connector.py
│   └── twitter_mcp_server.py
├── odoo_integration/              # Odoo integration
│   ├── odoo_connector.py
│   ├── mcp_server.py
│   ├── sync_invoices.py
│   └── update_dashboard_with_odoo.py
├── Inbox/                         # Input folder
├── Needs_Action/                  # Pending processing
├── Pending_Approval/              # Awaiting approval
├── Approved/                      # Approved actions
├── Completed/                     # Finished actions
├── Social_Media_Summaries/        # Performance reports
├── Briefings/                     # CEO briefings
├── Bank_Transactions/             # Financial data
├── agent_interface.py             # Main orchestrator
├── reasoning_loop.py              # Ralph Wiggum pattern
├── scheduler.py                   # Task scheduler
├── mcp.json                       # MCP configuration
├── requirements.txt               # Dependencies
├── README.md                      # User documentation
├── ARCHITECTURE.md                # This file
└── LESSONS_LEARNED.md             # Implementation learnings
```

---

## Integration Patterns

### 1. Watcher Pattern

```python
class BaseWatcher:
    def __init__(self, source, destination):
        self.source = source
        self.destination = destination
    
    def watch(self):
        while True:
            new_items = self.detect_new_items()
            for item in new_items:
                self.process_item(item)
                self.save_to_destination(item)
```

### 2. Connector Pattern

```python
class BaseConnector:
    def __init__(self, credentials):
        self.credentials = credentials
        self.authenticate()
    
    def authenticate(self):
        # Implement authentication logic
        pass
    
    def request(self, endpoint, method='GET', data=None):
        # Standardized request handling
        pass
```

### 3. MCP Server Pattern

```python
class BaseMCPServer:
    def __init__(self, port):
        self.app = web.Application()
        self.port = port
        self.setup_routes()
    
    def setup_routes(self):
        self.app.router.add_get('/health', self.health_check)
        # Add more routes
    
    async def health_check(self, request):
        return web.json_response({"status": "healthy"})
    
    def run(self):
        web.run_app(self.app, port=self.port)
```

### 4. Skill Pattern

```python
def skill_action(*args, **kwargs) -> dict:
    try:
        # Validate inputs
        # Execute action
        # Log result
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}
```

---

## Security Architecture

### Authentication Methods

| Component | Method | Storage |
|-----------|--------|---------|
| Gmail | OAuth 2.0 | token.pickle |
| Meta (FB/IG) | Access Token | Environment Variable |
| Twitter | OAuth 2.0 | Environment Variables |
| Odoo | JSON-RPC Auth | Environment Variables |

### Security Best Practices

1. **Credential Storage**
   - Never commit credentials to version control
   - Use environment variables for sensitive data
   - Implement secret rotation (90 days)

2. **Access Control**
   - Minimum required permissions for each integration
   - Separate tokens for development and production
   - Regular access audits

3. **Data Protection**
   - Encrypt sensitive data at rest
   - Use HTTPS for all API communications
   - Implement rate limiting to prevent abuse

4. **Audit Trail**
   - All actions logged to `Audit_Log.md`
   - Timestamp, action type, and result recorded
   - Logs retained indefinitely

---

## Error Handling & Recovery

### Error Handling Strategy

```python
try:
    result = perform_action()
except ConnectionError as e:
    # Network issue - retry with exponential backoff
    retry_with_backoff()
except AuthenticationError as e:
    # Auth issue - alert user, don't retry
    alert_user("Authentication failed")
except RateLimitError as e:
    # Rate limited - wait and retry
    wait_and_retry(after_seconds=e.retry_after)
except Exception as e:
    # Unknown error - log and escalate
    log_error(e)
    escalate_to_user()
```

### Graceful Degradation

| Failure Scenario | Degradation Strategy |
|-----------------|---------------------|
| Odoo unavailable | Cache transactions locally, sync later |
| Social media API down | Queue posts, retry in 15 minutes |
| Email service down | Local queue, process when restored |
| Database error | Fallback to file-based storage |

### Ralph Wiggum Loop

The autonomous loop pattern allows up to 5 iterations:

```python
for iteration in range(5):
    if stop_hook_triggered():
        break
    result = execute_step()
    if result.requires_approval():
        wait_for_approval()
    if result.is_complete():
        break
```

---

## Scalability Considerations

### Current Capacity

| Metric | Value |
|--------|-------|
| Email monitoring | 100 emails/hour |
| Social posts | 50 posts/hour |
| Odoo transactions | 200 transactions/hour |
| Concurrent watchers | 5 |

### Scaling Strategies

1. **Horizontal Scaling**
   - Deploy multiple watcher instances
   - Use message queue (Redis/RabbitMQ)
   - Load balance MCP servers

2. **Vertical Scaling**
   - Increase server resources
   - Optimize database queries
   - Implement caching (Redis)

3. **Asynchronous Processing**
   - Convert synchronous operations to async
   - Use Celery for background tasks
   - Implement job queues

4. **Database Migration**
   - Current: File-based (Markdown)
   - Future: SQLite → PostgreSQL
   - Implement proper indexing

---

## Technology Stack

### Backend
- **Language**: Python 3.10+
- **Web Framework**: aiohttp (async)
- **API Protocol**: REST + JSON-RPC
- **Browser Automation**: Playwright

### External APIs
- **Email**: Google Gmail API v3
- **Social**: Meta Graph API v18, Twitter API v2
- **ERP**: Odoo JSON-RPC v19+

### Infrastructure
- **Process Management**: PM2
- **Scheduling**: schedule library
- **Logging**: File-based (Markdown)

---

## Future Enhancements

### Planned Features
1. **Real-time Dashboard**: Web-based monitoring UI
2. **Advanced Analytics**: ML-powered insights
3. **Multi-tenant Support**: Handle multiple businesses
4. **Voice Interface**: Alexa/Google Home integration
5. **Mobile App**: iOS/Android companion app

### Technical Debt
1. Migrate from file-based to database storage
2. Implement proper testing framework (pytest)
3. Add CI/CD pipeline
4. Containerize with Docker
5. Implement distributed tracing

---

## Appendix: API Reference

### MCP Server Health Check

```bash
GET http://localhost:{port}/health

Response:
{
  "status": "healthy",
  "service": "{service_name}"
}
```

### Standard Error Response

```json
{
  "success": false,
  "error": "Error message",
  "error_code": "ERROR_CODE",
  "timestamp": "2026-02-17T10:30:00"
}
```

---

*Document Version: 1.0*
*Last Updated: 2026-02-17*
*Author: AI Agent Development Team*
