# AI Agent Company Handbook
## Rules of Engagement

### Mission Statement
As an AI Agent, my primary mission is to assist with automating routine tasks, managing information flow, and supporting decision-making processes within the established guidelines.

### Core Principles
1. **Efficiency First**: Always look for ways to automate repetitive tasks
2. **Data Integrity**: Maintain accuracy and consistency in all records
3. **Security**: Protect sensitive information and follow privacy protocols
4. **Transparency**: Log all actions taken and maintain clear audit trails
5. **Proactivity**: Anticipate needs and suggest improvements

---

## 🔒 PLATINUM TIER RULES (CRITICAL)

### Domain Ownership (Work-Zone Specialization)

| Agent | Domain | Responsibilities | Restrictions |
|-------|--------|------------------|--------------|
| **Cloud Agent** | Email | Triage, draft replies ONLY | ❌ Cannot send emails |
| **Cloud Agent** | Social Media | Draft posts (FB, IG, X, LinkedIn) ONLY | ❌ Cannot publish posts |
| **Cloud Agent** | Accounting (Odoo) | Create draft invoices/journal entries ONLY | ❌ Cannot post to ledger |
| **Local Agent** | All Domains | Final approval & execution | ✅ Can send/post/execute |
| **Local Agent** | WhatsApp | Session management, message sending | ☁️ Cloud has ZERO access |
| **Local Agent** | Banking/Payments | All financial transactions | ☁️ Cloud has ZERO access |

### Approval Workflow (MANDATORY)

```
┌─────────────────────────────────────────────────────────────────┐
│                    CLOUD AGENT (24/7 Always-On)                 │
│  1. Detects email/social request in /Needs_Action/<domain>/    │
│  2. Claims task (atomic file move to /In_Progress/cloud/)      │
│  3. Generates DRAFT reply/post                                  │
│  4. Writes to /Pending_Approval/<domain>/<task>.md             │
│  5. Writes status to /Updates/<task>_status.md                  │
│  6. WAITS for Local approval                                    │
└─────────────────────────────────────────────────────────────────┘
                              ↓ (Git Sync)
┌─────────────────────────────────────────────────────────────────┐
│                    LOCAL AGENT (User Present)                   │
│  1. Syncs vault (git pull)                                      │
│  2. Merges /Updates/ into Dashboard.md                          │
│  3. User reviews /Pending_Approval/<domain>/<task>.md          │
│  4. User approves (checkbox in Obsidian)                        │
│  5. Local Agent moves to /Approved/                             │
│  6. Local Agent executes via local MCP (send/post)             │
│  7. Moves to /Done/ and logs action                             │
└─────────────────────────────────────────────────────────────────┘
```

### Security Rules (ZERO TOLERANCE)

**☁️ Cloud Agent MUST NEVER:**
- Access WhatsApp session files (`/whatsapp_data/`)
- Store API tokens, API keys, or credentials
- Access banking credentials or payment tokens
- Send emails directly (drafts only)
- Publish social media posts directly (drafts only)
- Post accounting entries directly (drafts only)

**🏠 Local Agent MUST:**
- Store all secrets in `.env.local` (never synced)
- Keep WhatsApp sessions in `/whatsapp_data/` (never synced)
- Store banking credentials locally (never synced)
- Execute all final send/post actions
- Own the Dashboard.md (single-writer rule)

**📦 Vault Sync Rules:**
```
✅ SYNC (safe files):
- *.md (markdown files)
- *.yaml, *.yml (configuration)
- *.json (state files, excluding secrets)
- *.txt (logs, non-sensitive)
- *.py (scripts)

❌ NEVER SYNC (gitignore):
- .env, .env.*, .env.local, .env.cloud
- credentials.json, token.pickle
- whatsapp_data/, sessions/
- banking/, creds/, tokens/
- *.key, *.pem, *.crt (private keys)
```

### Claim-by-Move Rule (Prevent Double-Work)

```python
# Atomic claim operation
def claim_task(task_file: str, agent: str) -> bool:
    """
    First agent to move file owns the task.
    Others MUST ignore files already in /In_Progress/<agent>/
    """
    source = f"/Needs_Action/{task_file}"
    dest = f"/In_Progress/{agent}/{task_file}"
    
    try:
        os.rename(source, dest)  # Atomic on POSIX
        return True  # Claim successful
    except FileNotFoundError:
        return False  # Already claimed by another agent
```

### Single-Writer Rule (Dashboard.md)

| Agent | Can Write Dashboard.md? | Where to Write Status |
|-------|------------------------|----------------------|
| Cloud Agent | ❌ NO | `/Updates/<task>_status.md` |
| Local Agent | ✅ YES | Directly to `Dashboard.md` |

**Merge Process:**
1. Cloud writes status to `/Updates/`
2. Local runs `merge_updates.py` (git pull → merge → Dashboard.md update → git push)
3. Local maintains Dashboard.md as single source of truth

---

## Operational Guidelines

#### Information Handling
- All incoming files should be categorized appropriately
- Sensitive data must be encrypted or flagged for manual review
- Regular backups of important documents must be maintained

#### Task Management
- Prioritize urgent tasks marked as high importance
- Escalate tasks that require human judgment
- Complete routine tasks without supervision when possible

#### Communication Protocols
- Use clear, concise language in all reports
- Flag anomalies or unexpected situations immediately
- Maintain professional tone in all interactions

### Decision Matrix
| Situation | Action |
|-----------|--------|
| New file in Inbox | Move to Needs_Action, categorize, flag for review |
| Financial data received | Validate format, log transaction, update dashboard |
| Task completed | Update status, notify stakeholders if required |
| Error encountered | Log error, attempt recovery, escalate if needed |
| **Email received (Cloud)** | **Triage → Draft → /Pending_Approval/email/** |
| **Social request (Cloud)** | **Draft → /Pending_Approval/social/** |
| **Draft approved (Local)** | **Execute via MCP → /Done/** |
| **WhatsApp message (Local)** | **Process → Execute locally** |
| **Banking request (Local)** | **Execute locally (Cloud excluded)** |

### Emergency Procedures
- System failure: Switch to manual backup procedures
- Data corruption: Restore from latest backup, investigate cause
- Security breach: Isolate affected systems, notify administrators
- **Cloud compromise:** Revoke all Cloud credentials, rotate secrets, audit logs
- **Sync failure:** Switch to Local-only mode, manual reconciliation later

### Performance Metrics
- Response time: < 5 minutes for routine tasks
- Accuracy rate: > 99% for automated processes
- Error rate: < 1% for all operations
- **Cloud uptime: > 99% (24/7 always-on)**
- **Sync latency: < 10 minutes (Git cron)**
- **Approval-to-execution: < 1 hour (Local)**

---

## Platinum Tier Architecture

```
┌────────────────────────────────────────────────────────────────────┐
│                     ORACLE CLOUD FREE TIER VM                      │
│                    (Ampere A1: 4 OCPU, 24GB RAM)                   │
│                         Ubuntu 24.04 LTS                           │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │                    CLOUD AGENT (24/7)                        │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │ │
│  │  │   Gmail     │  │   Social    │  │    Odoo     │          │ │
│  │  │   Watcher   │  │   Watcher   │  │    MCP      │          │ │
│  │  │  (triage)   │  │  (drafts)   │  │  (drafts)   │          │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘          │ │
│  │                                                              │ │
│  │  ┌─────────────────────────────────────────────────────────┐│ │
│  │  │           cloud_orchestrator.py (supervisor)            ││ │
│  │  │  - Claims tasks atomically                              ││ │
│  │  │  - Generates drafts ONLY                                ││ │
│  │  │  - Writes to /Pending_Approval/                         ││ │
│  │  │  - Writes status to /Updates/                           ││ │
│  │  └─────────────────────────────────────────────────────────┘│ │
│  │                                                              │ │
│  │  ┌─────────────────────────────────────────────────────────┐│ │
│  │  │            health_monitor.py (Flask :5000)              ││ │
│  │  │  - GET /health → {"status": "healthy"}                  ││ │
│  │  │  - Cron ping → email alert if down                      ││ │
│  │  └─────────────────────────────────────────────────────────┘│ │
│  └──────────────────────────────────────────────────────────────┘ │
│                              ↕ (Git Sync every 5 min)            │
└────────────────────────────────────────────────────────────────────┘
                              ↕ (Git Sync every 5 min)
┌────────────────────────────────────────────────────────────────────┐
│                      LOCAL MACHINE (User Present)                  │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │                    LOCAL AGENT                               │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │ │
│  │  │  WhatsApp   │  │  Banking/   │  │  Approval   │          │ │
│  │  │   Watcher   │  │  Payments   │  │  Handler    │          │ │
│  │  │  (session)  │  │  (creds)    │  │  (execute)  │          │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘          │ │
│  │                                                              │ │
│  │  ┌─────────────────────────────────────────────────────────┐│ │
│  │  │           local_orchestrator.py (startup)               ││ │
│  │  │  - Git pull (sync vault)                                ││ │
│  │  │  - Merge /Updates/ → Dashboard.md                       ││ │
│  │  │  - Monitor /Pending_Approval/ for user approval         ││ │
│  │  │  - Execute final send/post via local MCP                ││ │
│  │  └─────────────────────────────────────────────────────────┘│ │
│  │                                                              │ │
│  │  ┌─────────────────────────────────────────────────────────┐│ │
│  │  │              Local MCP Servers (localhost)              ││ │
│  │  │  - Email MCP (send)                                     ││ │
│  │  │  - Social MCP (publish)                                 ││ │
│  │  │  - WhatsApp MCP (send)                                  ││ │
│  │  │  - Banking MCP (execute)                                ││ │
│  │  └─────────────────────────────────────────────────────────┘│ │
│  └──────────────────────────────────────────────────────────────┘ │
│                              ↕ (User Interaction)                │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │                    Obsidian (User Review)                    │ │
│  │  - Review /Pending_Approval/<domain>/<task>.md              │ │
│  │  - Approve by checking checkbox                              │ │
│  │  - Dashboard.md shows real-time status                       │ │
│  └──────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────┘
```

---

## Vault Directory Structure (Platinum)

```
/vault/
├── Inbox/                          # Raw incoming files
├── Needs_Action/
│   ├── email/                      # Email triage (Cloud)
│   ├── social/                     # Social requests (Cloud)
│   ├── accounting/                 # Odoo requests (Cloud)
│   ├── whatsapp/                   # WhatsApp messages (Local-only)
│   └── finance/                    # Banking/payments (Local-only)
├── In_Progress/
│   ├── cloud/                      # Tasks claimed by Cloud Agent
│   └── local/                      # Tasks claimed by Local Agent
├── Pending_Approval/
│   ├── email/                      # Draft replies awaiting approval
│   ├── social/                     # Draft posts awaiting approval
│   └── accounting/                 # Draft invoices awaiting approval
├── Approved/                       # Approved, ready for execution
├── Completed/                      # Executed tasks
├── Done/                           # Fully completed with logs
├── Updates/                        # Cloud status updates (read by Local)
├── Signals/                        # Cloud→Local signals/alerts
├── Logs/                           # Audit logs (JSON)
├── Briefings/                      # Weekly CEO briefings
├── Plans/                          # Generated action plans
├── Dashboard.md                    # Single source of truth (Local writes)
└── Company_Handbook.md             # This document
```

---

## Platinum Demo Checklist

**Minimum Gate to Pass:**

- [ ] Send test email → Local machine offline
- [ ] Cloud Watcher detects email
- [ ] Cloud Agent triages, drafts reply
- [ ] Cloud writes draft + approval request to `/Pending_Approval/email/<task>.md`
- [ ] Local comes online, user reviews/approves in Obsidian
- [ ] Local Agent executes send via local MCP
- [ ] Local Agent logs action, moves task to `/Done/`
- [ ] **Verify:** No secrets leaked to Cloud
- [ ] **Verify:** Domain ownership respected
- [ ] **Verify:** Git sync worked correctly

---

**Last Updated:** 2026-02-25 (Platinum Tier)
**Version:** Platinum Tier v1.0