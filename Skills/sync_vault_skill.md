# Skill: Vault Synchronization (Git-Based)

**Domain:** Infrastructure
**Agent Type:** Both Cloud and Local
**Capability:** Git-based vault synchronization
**Execution:** Both agents

---

## Overview

This skill enables Cloud and Local agents to:
1. Sync vault contents via Git
2. Pull updates from remote repository
3. Push local changes to remote
4. Handle merge conflicts
5. Maintain audit trail via commits

**CRITICAL:** Secrets (.env, credentials, sessions) are gitignored and NEVER synced.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     CLOUD VM (Oracle Cloud)                     │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  Cloud Agent                                              │ │
│  │  - Processes email/social/accounting drafts              │ │
│  │  - Writes to /Updates/                                    │ │
│  │  - Git push every 5 minutes                               │ │
│  └───────────────────────────────────────────────────────────┘ │
│                              ↕ (Git Remote)                    │
│                    GitHub/GitLab Private Repo                  │
│                              ↕ (Git Remote)                    │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  Local Machine (User Present)                             │ │
│  │  - Local Agent                                            │ │
│  │  - Processes approvals                                    │ │
│  │  - Executes final actions                                 │ │
│  │  - Merges /Updates/ → Dashboard.md                        │ │
│  │  - Git pull/push every 5 minutes                          │ │
│  └───────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## Usage

### Sync Script

```bash
# Pull updates from remote
python sync_vault.py --mode pull

# Push local changes to remote
python sync_vault.py --mode push

# Full sync (pull + push)
python sync_vault.py --mode sync

# Check sync status
python sync_vault.py --mode status
```

### In Cloud Orchestrator

```python
from sync_vault import VaultSync

# Initialize
sync = VaultSync(vault_path='/opt/platinum-vault')

# In orchestrator loop
def run_once(self):
    # Pull latest changes
    success, message = sync.pull()
    
    # Process tasks...
    
    # Push changes
    success, message = sync.push()
```

### In Local Orchestrator

```python
from sync_vault import VaultSync

# Initialize
sync = VaultSync(vault_path='/path/to/vault')

# In orchestrator loop
def run_once(self):
    # Pull Cloud updates
    success, message = sync.pull()
    
    # Merge /Updates/ → Dashboard.md
    merge_updates_to_dashboard()
    
    # Process approvals...
    
    # Push Local changes
    success, message = sync.push()
```

---

## Git Configuration

### .gitignore (Critical Security)

```gitignore
# Environment variables (ALL types)
.env
.env.local
.env.cloud
.env.production

# Token and credentials files
token.pickle
credentials.json
*.pem
*.key
*.crt

# WhatsApp session data
whatsapp_data/
sessions/

# Banking and payment credentials
banking/
creds/
tokens/

# Local configuration
config.local.json

# Database dumps
odoo_backups/
*.dump
*.sql

# Logs with sensitive data
Posts_Log.json
watcher_log.txt
```

### Cron Job (Cloud VM)

```bash
# Edit crontab
crontab -e

# Add sync job (every 5 minutes)
*/5 * * * * cd /opt/platinum-vault && /usr/bin/python3 sync_vault.py --mode sync >> /var/log/vault_sync.log 2>&1
```

### Startup Script (Local)

```bash
# Start local orchestrator on boot (Windows Task Scheduler or Linux systemd)

# Linux systemd service
sudo systemctl edit --force local-orchestrator

[Unit]
Description=Local Agent Orchestrator
After=network.target

[Service]
Type=simple
User=localuser
WorkingDirectory=/path/to/vault
ExecStart=/usr/bin/python3 local_orchestrator.py
Restart=always

[Install]
WantedBy=multi-user.target
```

---

## Conflict Resolution

### Automatic Resolution

```python
from sync_vault import VaultSync

sync = VaultSync()

# Check for conflicts
conflicts = sync.check_conflicts()

if conflicts:
    print(f"Found {len(conflicts)} conflicts:")
    for c in conflicts:
        print(f"  - {c}")
    
    # Resolve with 'ours' strategy (keep local changes)
    success, message = sync.resolve_conflicts(strategy='ours')
    
    # Or 'theirs' strategy (keep remote changes)
    # success, message = sync.resolve_conflicts(strategy='theirs')
```

### Manual Resolution

```bash
# Check status
git status

# See conflicts
git diff

# Resolve manually (edit files)
# ...

# Mark resolved
git add <file>

# Commit
git commit -m "Resolve merge conflicts"
```

---

## Sync Rules

**Cloud Agent:**
- ✅ Sync markdown files (.md)
- ✅ Sync scripts (.py)
- ✅ Sync configuration (.json, .yaml)
- ✅ Sync status updates (/Updates/)
- ❌ NEVER sync .env files
- ❌ NEVER sync credentials
- ❌ NEVER sync WhatsApp sessions

**Local Agent:**
- ✅ Sync all safe files
- ✅ Merge /Updates/ into Dashboard.md
- ✅ Sync completed tasks (/Done/)
- ❌ NEVER sync .env.local
- ❌ NEVER sync credentials
- ❌ NEVER sync WhatsApp sessions

---

## Best Practices

### Commit Messages

```bash
# Good commit messages
"Cloud Agent auto-sync"
"Local Agent auto-sync"
"Add email draft TASK_20260225_abc123"
"Complete social post TASK_20260225_xyz789"

# Avoid
"update"
"changes"
"fix"
```

### Sync Frequency

| Scenario | Recommended Interval |
|----------|---------------------|
| Cloud Agent | 5 minutes |
| Local Agent | 5 minutes |
| High-frequency trading | 1 minute |
| Low-activity system | 10 minutes |

### Branch Strategy

```
main (production)
  └── Cloud and Local both sync to main
  
feature-xyz (optional, for testing)
  └── Test new features before merging to main
```

---

## Monitoring

### Check Sync Status

```bash
# Check last commit
git log -1 --format="%h %s (%ci)"

# Check remote status
git fetch origin
git status

# Check for unpushed commits
git log origin/main..main
```

### Sync Health

```python
def check_sync_health():
    """Check if sync is working properly."""
    sync = VaultSync()
    
    # Get last commit time
    result = subprocess.run(
        ['git', 'log', '-1', '--format=%ct'],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        last_commit_time = int(result.stdout.strip())
        current_time = time.time()
        age_minutes = (current_time - last_commit_time) / 60
        
        if age_minutes > 15:
            print(f"WARNING: Last sync was {age_minutes:.1f} minutes ago")
            return False
            
    return True
```

---

## Troubleshooting

### Sync Fails

```bash
# Check git configuration
git config --list

# Check remote
git remote -v

# Test connection
git fetch origin

# Check for large files
git count-objects -vH
```

### Conflicts

```bash
# List conflicts
git diff --name-only --diff-filter=U

# Abort merge if needed
git merge --abort

# Retry sync
python sync_vault.py --mode sync
```

---

## Related Skills

- [[email_draft_skill]] - Cloud Agent skill for email drafts
- [[approval_handler]] - Local Agent skill for handling approvals
- [[health_monitor_skill]] - Health monitoring skill

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-25 | Initial implementation |
