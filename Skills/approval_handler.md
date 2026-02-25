# Skill: Approval Handler (Local Agent)

**Domain:** All Domains
**Agent Type:** Local
**Capability:** Handle user approvals for Cloud Agent drafts
**Execution:** Local Agent only

---

## Overview

This skill enables the Local Agent to:
1. Monitor `/Pending_Approval/<domain>/` for draft tasks
2. Check for user approval (checkbox in Obsidian)
3. Execute approved actions via local MCP servers
4. Move completed tasks to `/Done/`
5. Update Dashboard.md with execution status

**CRITICAL:** Only Local Agent can execute final actions. Cloud Agent has ZERO execution capability.

---

## Usage

### As Local Agent

```python
import re
from pathlib import Path
from claim_task import TaskClaimer

# Initialize
claimer = TaskClaimer(vault_path='/path/to/vault')
pending_path = Path(vault_path) / 'Pending_Approval'

def check_approval(task_file: Path) -> bool:
    """Check if task has been approved by user."""
    content = task_file.read_text()
    
    # Look for checked checkbox
    approval_patterns = [
        r'\[x\]\s*\*\*APPROVED\*\*',
        r'\[x\]\s*APPROVED',
        r'-\s*\[x\]\s*Review and approve'
    ]
    
    return any(re.search(pattern, content, re.IGNORECASE) for pattern in approval_patterns)

def execute_approved_tasks():
    """Check and execute all approved tasks."""
    
    # Check all domains
    for domain in ['email', 'social', 'accounting']:
        domain_path = pending_path / domain
        if not domain_path.exists():
            continue
            
        for task_file in domain_path.glob('*.md'):
            # Check if approved
            if check_approval(task_file):
                print(f"Approved task found: {task_file}")
                
                # Claim for local execution
                rel_path = f"{domain}/{task_file.name}"
                claimer.claim(rel_path, 'local')
                
                # Execute based on domain
                if domain == 'email':
                    execute_email(task_file)
                elif domain == 'social':
                    execute_social(task_file)
                elif domain == 'accounting':
                    execute_odoo(task_file)
                    
                # Move to Done
                done_path = Path(vault_path) / 'Done' / domain
                done_path.mkdir(parents=True, exist_ok=True)
                task_file.rename(done_path / task_file.name)
```

### Execute Email

```python
def execute_email(task_file: Path):
    """Send approved email via local MCP."""
    import requests
    
    # Read task content
    content = task_file.read_text()
    
    # Extract reply content (parse markdown)
    reply_content = extract_reply_content(content)
    
    # Call local email MCP server
    response = requests.post('http://localhost:8080/tools/send_email', json={
        'to': extract_recipient(content),
        'subject': extract_subject(content),
        'body': reply_content
    })
    
    if response.status_code == 200:
        print(f"Email sent successfully")
    else:
        print(f"Failed to send email: {response.text}")
```

### Execute Social Post

```python
def execute_social(task_file: Path):
    """Publish approved social post via local MCP."""
    import requests
    
    # Read task content
    content = task_file.read_text()
    
    # Extract post content and platforms
    post_text = extract_post_text(content)
    platforms = extract_platforms(content)
    
    # Publish to each selected platform
    for platform in platforms:
        if platform == 'facebook':
            response = requests.post('http://localhost:8083/tools/post_facebook', json={
                'text': post_text,
                'page_id': get_facebook_page_id()
            })
        elif platform == 'instagram':
            response = requests.post('http://localhost:8083/tools/post_instagram', json={
                'text': post_text,
                'account_id': get_instagram_account_id()
            })
        elif platform == 'x':
            response = requests.post('http://localhost:8084/tools/post_tweet', json={
                'text': post_text
            })
```

### Execute Odoo Entry

```python
def execute_odoo(task_file: Path):
    """Post approved Odoo entry via local MCP."""
    import requests
    
    # Read task content
    content = task_file.read_text()
    
    # Extract entry details
    entry_type = extract_entry_type(content)
    entry_data = extract_entry_data(content)
    
    # Post to Odoo via local MCP
    if entry_type == 'invoice':
        response = requests.post('http://localhost:8082/tools/create_invoice', json=entry_data)
    elif entry_type == 'journal_entry':
        response = requests.post('http://localhost:8082/tools/post_journal_entry', json=entry_data)
```

---

## Approval Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                    CLOUD AGENT (Draft Creation)                 │
│  1. Detects task in /Needs_Action/<domain>/                    │
│  2. Claims task atomically                                     │
│  3. Generates draft                                            │
│  4. Writes to /Pending_Approval/<domain>/<task>.md            │
│  5. Writes status to /Updates/                                 │
│  6. Signals Local Agent                                        │
└─────────────────────────────────────────────────────────────────┘
                              ↓ (Git Sync)
┌─────────────────────────────────────────────────────────────────┐
│                    LOCAL AGENT (Approval Check)                 │
│  1. Syncs vault (git pull)                                      │
│  2. Merges /Updates/ → Dashboard.md                             │
│  3. Scans /Pending_Approval/<domain>/                          │
│  4. Checks each task for approval checkbox                      │
│  5. If [ ] unchecked → WAIT for user                            │
│  6. If [x] checked → EXECUTE via local MCP                     │
│  7. Move to /Done/ and update Dashboard                         │
└─────────────────────────────────────────────────────────────────┘
                              ↓ (User Action)
┌─────────────────────────────────────────────────────────────────┐
│                    USER (Obsidian Review)                       │
│  1. Opens /Pending_Approval/<domain>/<task>.md in Obsidian     │
│  2. Reviews draft content                                       │
│  3. If satisfied → Check [x] **APPROVED** box                  │
│  4. If not → Edit draft or reject                               │
│  5. Save file (Obsidian auto-saves)                             │
└─────────────────────────────────────────────────────────────────┘
```

---

## Approval File Format

```markdown
---
task_id: TASK_20260225_abc123
task_type: email_reply
source: email/incoming_001.md
created: 2026-02-25T10:30:00
agent: cloud
status: pending_approval
domain: email
---

# Email Draft Reply

**Task ID:** TASK_20260225_abc123
**Source:** email/incoming_001.md
**Created:** 2026-02-25T10:30:00
**Agent:** Cloud Agent (Draft Only)

---

## Original Email

```
[Original email content]
```

---

## Draft Reply

> [!NOTE] CLOUD AGENT DRAFT - REQUIRES LOCAL APPROVAL
> This is a DRAFT reply generated by the Cloud Agent.
> Local Agent MUST review and approve before sending.

[ ] **APPROVED** - Check this box to approve sending this email
    ^ User clicks here to approve

---

## Suggested Reply Content

[AI-generated reply]

---

## Approval Workflow

1. **Cloud Agent:** Created draft (this file)
2. **Local Agent:** [ ] Review and approve (check box above)
3. **Local Agent:** Execute send via local MCP
4. **Local Agent:** Move to /Done/ and log action
```

---

## Security Rules

**Local Agent MUST:**
- ✅ Monitor `/Pending_Approval/` for approvals
- ✅ Check for user approval checkbox
- ✅ Execute approved actions via local MCP
- ✅ Move completed tasks to `/Done/`
- ✅ Update Dashboard.md with status
- ✅ Store all secrets in `.env.local` (never synced)
- ✅ Keep WhatsApp sessions local (never synced)

**Local Agent MUST NOT:**
- ❌ Sync secrets to Git
- ❌ Allow Cloud Agent to access credentials
- ❌ Execute unapproved tasks

---

## Integration with Obsidian

User workflow in Obsidian:

1. **Open Obsidian** → Navigate to vault
2. **Browse to** `Pending_Approval/email/` (or social/accounting)
3. **Open task file** → Review draft content
4. **Check checkbox** → `[ ]` becomes `[x]`
5. **Save** → Obsidian auto-saves
6. **Local Agent detects** → Executes on next iteration

---

## Testing

### Test Approval Workflow

```bash
# 1. Create draft manually (simulating Cloud Agent)
cat > Pending_Approval/email/test_approval_001.md << 'EOF'
---
task_id: TASK_TEST_001
domain: email
status: pending_approval
---

# Email Draft Reply

[ ] **APPROVED** - Check this box to approve sending this email

## Suggested Reply

Test email content
EOF

# 2. Manually approve (simulate user action)
sed -i 's/\[ \] \*\*APPROVED\*\*/[x] **APPROVED**/' Pending_Approval/email/test_approval_001.md

# 3. Run local orchestrator
python local_orchestrator.py --once

# 4. Verify task moved to Done
ls Done/email/
```

---

## Related Skills

- [[email_draft_skill]] - Cloud Agent skill for email drafts
- [[social_draft_skill]] - Cloud Agent skill for social drafts
- [[odoo_draft_skill]] - Cloud Agent skill for Odoo drafts
- [[sync_vault_skill]] - Git-based vault synchronization

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-25 | Initial implementation |
