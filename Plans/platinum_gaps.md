# Platinum Tier Gap Analysis

**Document Created:** 2026-02-25
**Current Status:** Gold Tier 100% Complete
**Target:** Platinum Tier 100% Complete

---

## Executive Summary

The system is currently at **Gold Tier** with all core functionality working:
- ✅ 5 MCP servers operational
- ✅ Ralph Wiggum autonomous loop
- ✅ Weekly CEO briefings
- ✅ Audit logging & error recovery
- ✅ Social media posting (Facebook, Instagram, X)
- ✅ Odoo integration
- ✅ WhatsApp watcher active

**Platinum Tier requires significant architectural changes** to achieve:
1. 24/7 Cloud deployment (Oracle Cloud Free Tier)
2. Cloud/Local Agent separation with domain ownership
3. File-based delegation via synced vault
4. Security rules (no secrets on Cloud)
5. Odoo 24/7 hosting on Cloud VM
6. Health monitoring & always-on operations

---

## Gap Analysis by Requirement

### 1. Cloud Deployment (24/7 Always-On)

**Requirement:** Deploy AI Employee on Oracle Cloud Free Tier VM (Ampere A1 Flex: 4 OCPU, 24GB RAM, Ubuntu 24.04)

**Current State:**
- ❌ No cloud deployment
- ❌ No Oracle Cloud VM configured
- ❌ No supervisor/systemd services for 24/7 operation
- ❌ No remote SSH access configured
- ❌ No Ubuntu server environment

**Gaps:**
| Gap | Priority | Effort |
|-----|----------|--------|
| Oracle Cloud account setup | High | Medium |
| VM instance creation (Ampere A1) | High | Low |
| Ubuntu 24.04 configuration | High | Low |
| Python 3.13+, Node.js v24+, Git installation | High | Low |
| Supervisor/systemd service configuration | High | Medium |
| SSH key management | High | Low |
| Domain & HTTPS setup (Let's Encrypt) | High | Medium |

**Action Items:**
- [ ] Create Oracle Cloud Free Tier account
- [ ] Provision Ampere A1 Flex instance
- [ ] Configure SSH access
- [ ] Install all dependencies
- [ ] Set up supervisor services for orchestrators
- [ ] Configure domain DNS to VM public IP
- [ ] Install Certbot for HTTPS

---

### 2. Work-Zone Specialization (Domain Ownership)

**Requirement:**
- **Cloud Agent owns:** Email triage + draft replies + social media drafts (LinkedIn, FB, IG, X) → writes to `/Pending_Approval/<domain>/`
- **Local Agent owns:** Final approvals, WhatsApp session, payments/banking, final send/post executions

**Current State:**
- ⚠️ Partial implementation
- ✅ Email watcher exists (needs OAuth)
- ✅ Social MCP servers exist
- ❌ No Cloud/Local separation
- ❌ WhatsApp watcher currently not Local-only
- ❌ No domain ownership rules enforced
- ❌ No approval workflow separation

**Gaps:**
| Gap | Priority | Priority | Effort |
|-----|----------|----------|--------|
| Define Cloud Agent scope | High | High | Low |
| Define Local Agent scope | High | High | Low |
| Move WhatsApp watcher to Local-only | High | High | Medium |
| Move banking/payment watchers to Local-only | High | High | Medium |
| Create Cloud-only MCP config | High | High | Low |
| Create Local-only MCP config | High | High | Low |
| Enforce draft-only on Cloud | High | High | Medium |

**Action Items:**
- [ ] Update Company_Handbook.md with domain ownership rules
- [ ] Create `claude-cloud-config.json` (email triage, social drafts, Odoo drafts only)
- [ ] Create `claude-local-config.json` (approvals, WhatsApp, banking, final executes)
- [ ] Modify WhatsApp watcher to run Local-only
- [ ] Create email_draft_skill.md for Cloud
- [ ] Create social_draft_skill.md for Cloud
- [ ] Create approval_handler.md for Local

---

### 3. Delegation via Synced Vault (Phase 1)

**Requirement:**
- Agents communicate ONLY via files:
  - `/Needs_Action/<domain>/`
  - `/Plans/<domain>/`
  - `/Pending_Approval/<domain>/`
- Claim-by-move rule (atomic file move)
- Single-writer rule (Local writes Dashboard.md only)
- Git-based sync (cron every 5-10 min)

**Current State:**
- ⚠️ Partial folder structure exists
- ✅ `/Needs_Action/` exists (108 files)
- ✅ `/Plans/` exists (812+ files)
- ✅ `/Pending_Approval/` exists (empty)
- ❌ No `/In_Progress/cloud/` or `/In_Progress/local/`
- ❌ No claim-by-move mechanism
- ❌ No Git sync automation
- ❌ No cron jobs configured
- ❌ Dashboard.md writable by all

**Gaps:**
| Gap | Priority | Effort |
|-----|----------|--------|
| Create `/In_Progress/cloud/` folder | High | Low |
| Create `/In_Progress/local/` folder | High | Low |
| Create domain subfolders (email/, social/, accounting/) | High | Low |
| Implement claim-by-move atomic operations | High | Medium |
| Create sync_vault.py script | High | Medium |
| Configure Git cron jobs (5-10 min) | High | Low |
| Enforce single-writer rule for Dashboard.md | High | Medium |
| Create merge script for /Updates/ → Dashboard.md | High | Medium |

**Action Items:**
- [ ] Create folder structure: `/Needs_Action/email/`, `/Needs_Action/social/`, `/Needs_Action/accounting/`
- [ ] Create `/In_Progress/cloud/` and `/In_Progress/local/`
- [ ] Create `/Pending_Approval/email/`, `/Pending_Approval/social/`, `/Pending_Approval/accounting/`
- [ ] Create `/Updates/` folder for Cloud status updates
- [ ] Create `/Signals/` folder for Cloud→Local signals
- [ ] Implement `claim_task.py` with atomic file move
- [ ] Create `sync_vault.py` for Git pull/push automation
- [ ] Create `merge_updates.py` for Dashboard.md sync
- [ ] Set up cron: `*/5 * * * * cd /vault && git pull && process && git add/commit/push`

---

### 4. Security Rules (Critical)

**Requirement:**
- Vault sync includes ONLY markdown/state files (.md, .yaml)
- NEVER sync: .env, API tokens, WhatsApp sessions, banking creds
- Cloud has ZERO access to WhatsApp sessions, banking creds, payment tokens

**Current State:**
- ⚠️ Partial .gitignore exists
- ✅ `.env` excluded
- ✅ `token.pickle` excluded
- ✅ `credentials.json` excluded
- ❌ WhatsApp session folder not excluded
- ❌ Banking creds not explicitly excluded
- ❌ No security enforcement mechanism
- ❌ No secret scanning

**Gaps:**
| Gap | Priority | Effort |
|-----|----------|--------|
| Update .gitignore for all secrets | Critical | Low |
| Exclude whatsapp_data/ from sync | Critical | Low |
| Exclude banking/creds folders | Critical | Low |
| Create .env.cloud.example (no secrets) | High | Low |
| Create .env.local.example (all secrets) | High | Low |
| Implement secret scanning pre-commit hook | High | Medium |
| Document security rules in Company_Handbook | High | Low |

**Action Items:**
- [ ] Update `.gitignore` with all secret patterns
- [ ] Create `.env.cloud.example` (safe for Cloud)
- [ ] Create `.env.local.example` (Local-only secrets)
- [ ] Add `whatsapp_data/`, `sessions/`, `creds/`, `tokens/` to .gitignore
- [ ] Create pre-commit hook to scan for secrets
- [ ] Add CRITICAL security warning to Company_Handbook.md

---

### 5. Odoo 24/7 on Cloud VM

**Requirement:**
- Install Odoo Community Edition 19+ on SAME Cloud VM
- Configure PostgreSQL, odoo.conf
- Enable HTTPS with Let's Encrypt
- Set up daily backups (pg_dump + rsync)
- Health monitoring endpoint
- Integrate Cloud Agent via MCP (draft-only actions)
- Local approves → executes final post

**Current State:**
- ✅ Odoo MCP server exists (Port 8082)
- ✅ Odoo integration tested
- ❌ Odoo not installed on Cloud VM
- ❌ No PostgreSQL configuration for Cloud
- ❌ No HTTPS/Let's Encrypt configured
- ❌ No daily backup system
- ❌ No health monitoring endpoint
- ❌ Odoo MCP not draft-only (can execute directly)

**Gaps:**
| Gap | Priority | Effort |
|-----|----------|--------|
| Odoo 19 CE installation on Ubuntu | High | Medium |
| PostgreSQL configuration | High | Medium |
| odoo.conf configuration | High | Low |
| Let's Encrypt HTTPS setup | High | Medium |
| Daily backup script (pg_dump) | High | Low |
| Health monitoring endpoint (/health) | High | Low |
| Modify Odoo MCP for draft-only on Cloud | High | Medium |
| Create odoo_draft_invoice.md skill | High | Low |

**Action Items:**
- [ ] Create Odoo installation script for Ubuntu
- [ ] Configure PostgreSQL for Odoo
- [ ] Set up odoo.conf with proper settings
- [ ] Install Certbot and configure HTTPS
- [ ] Create daily backup cron job
- [ ] Add `/health` endpoint to Odoo MCP
- [ ] Create `odoo_draft_skill.md` (Cloud: draft-only)
- [ ] Modify Odoo MCP to check agent type (Cloud vs Local)

---

### 6. Phase 2 A2A Upgrade (Optional)

**Requirement:** Replace some file-based handoffs with direct agent-to-agent messages (WebSockets/MQTT) while keeping vault as source of truth

**Current State:**
- ❌ No WebSocket implementation
- ❌ No MQTT implementation
- ❌ No direct agent communication

**Gaps:**
| Gap | Priority | Effort |
|-----|----------|--------|
| WebSocket server (Socket.io) | Low | High |
| MQTT broker setup | Low | Medium |
| A2A message protocol | Low | Medium |
| Fallback to vault sync | Low | Medium |

**Note:** Phase 2 is OPTIONAL. Prioritize file-based (Phase 1) first.

---

### 7. Platinum Demo Requirement

**Requirement:**
1. Send test email → Local offline
2. Cloud Watcher detects → triages → drafts reply → writes to `/Pending_Approval/email/`
3. Local comes online → User approves in Obsidian
4. Local Agent executes send → logs → moves to `/Done/`
5. Verify: no secrets leaked, zones respected, sync worked

**Current State:**
- ❌ No Cloud/Local separation
- ❌ No sync mechanism
- ❌ No demo test script

**Gaps:**
| Gap | Priority | Effort |
|-----|----------|--------|
| Create demo test script | High | Medium |
| Simulate Local offline scenario | High | Low |
| Verify Cloud draft creation | High | Low |
| Verify Local approval workflow | High | Low |
| Verify no secret leakage | High | Low |

**Action Items:**
- [ ] Create `platinum_demo_test.py`
- [ ] Create test email scenario
- [ ] Create approval simulation
- [ ] Create verification checklist
- [ ] Document demo results

---

### 8. Health Monitoring

**Requirement:** Flask endpoint on Cloud + cron ping/email alert if down

**Current State:**
- ❌ No health monitoring endpoint
- ❌ No uptime monitoring
- ❌ No alert system

**Gaps:**
| Gap | Priority | Effort |
|-----|----------|--------|
| Create health_monitor.py (Flask) | High | Low |
| Create /health endpoint | High | Low |
| Create uptime monitor cron | High | Low |
| Create email alert on downtime | High | Low |

**Action Items:**
- [ ] Create `health_monitor.py` with Flask `/health` endpoint
- [ ] Create external monitor script (pings /health)
- [ ] Set up cron for monitoring
- [ ] Configure email alerts on failure

---

### 9. Orchestrator Implementation

**Requirement:**
- `cloud_orchestrator.py`: Runs Watchers (email/social), claims tasks, runs Claude Code loop, writes to `/Updates/`
- `local_orchestrator.py`: Merges `/Updates/` → Dashboard.md, handles approvals, runs local Watchers (WhatsApp/finance), executes final actions

**Current State:**
- ✅ `ralph_orchestrator.py` exists
- ✅ `reasoning_loop.py` exists
- ✅ `scheduler.py` exists
- ❌ No Cloud-specific orchestrator
- ❌ No Local-specific orchestrator
- ❌ No merge logic for Dashboard.md

**Gaps:**
| Gap | Priority | Effort |
|-----|----------|--------|
| Create cloud_orchestrator.py | Critical | High |
| Create local_orchestrator.py | Critical | High |
| Implement /Updates/ merge logic | High | Medium |
| Configure supervisor for cloud_orchestrator | High | Low |
| Configure local startup for local_orchestrator | High | Low |

**Action Items:**
- [ ] Create `cloud_orchestrator.py` (email/social watchers, draft generation, /Updates/ writes)
- [ ] Create `local_orchestrator.py` (approval handling, WhatsApp/finance watchers, final executes, Dashboard.md merge)
- [ ] Create `merge_dashboard.py` utility
- [ ] Create supervisor config for cloud_orchestrator
- [ ] Create startup script for local_orchestrator

---

### 10. Agent Skills (Platinum-Specific)

**Requirement:** All AI functionality as Agent Skills (SKILL.md files)

**Current State:**
- ✅ 4 existing skills in `/Skills/`
- ✅ 2 skills in `/.qwen/skills/`
- ❌ No email_draft_skill.md
- ❌ No social_draft_skill.md
- ❌ No approval_handler.md
- ❌ No odoo_draft_skill.md
- ❌ No sync_vault_skill.md
- ❌ No health_monitor_skill.md

**Gaps:**
| Gap | Priority | Effort |
|-----|----------|--------|
| Create email_draft_skill.md | High | Low |
| Create social_draft_skill.md | High | Low |
| Create approval_handler.md | High | Low |
| create odoo_draft_skill.md | High | Low |
| Create sync_vault_skill.md | Medium | Low |
| Create health_monitor_skill.md | Medium | Low |
| Create cloud_orchestrator_skill.md | Medium | Low |
| Create local_orchestrator_skill.md | Medium | Low |

---

## Summary: Critical Path to Platinum

### Phase 1: Foundation (Week 1)
1. ✅ Gap analysis (this document)
2. ⏳ Reorganize folder structure
3. ⏳ Update Company_Handbook.md with Platinum rules
4. ⏳ Create Cloud/Local Agent configs
5. ⏳ Implement cloud_orchestrator.py
6. ⏳ Implement local_orchestrator.py
7. ⏳ Create sync_vault.py
8. ⏳ Update .gitignore for security

### Phase 2: Cloud Deployment (Week 2)
9. ⏳ Set up Oracle Cloud VM
10. ⏳ Deploy cloud_orchestrator to VM
11. ⏳ Install Odoo 19 on VM
12. ⏳ Configure HTTPS (Let's Encrypt)
13. ⏳ Set up health monitoring
14. ⏳ Configure supervisor services

### Phase 3: Integration & Testing (Week 3)
15. ⏳ Test Cloud/Local sync
16. ⏳ Test domain ownership rules
17. ⏳ Test security (no secret leakage)
18. ⏳ Run Platinum demo simulation
19. ⏳ Document results

### Phase 4: Completion (Week 4)
20. ⏳ Fix any issues
21. ⏳ Write PLATINUM_COMPLETE.md
22. ⏳ Update Dashboard.md
23. ⏳ Mark Platinum Tier 100% COMPLETE

---

## File Creation Checklist

### Configuration Files
- [ ] `claude-cloud-config.json`
- [ ] `claude-local-config.json`
- [ ] `.env.cloud.example`
- [ ] `.env.local.example`
- [ ] `supervisor_cloud.conf`
- [ ] `supervisor_local.conf`

### Python Scripts
- [ ] `cloud_orchestrator.py`
- [ ] `local_orchestrator.py`
- [ ] `sync_vault.py`
- [ ] `merge_dashboard.py`
- [ ] `claim_task.py`
- [ ] `health_monitor.py`
- [ ] `platinum_demo_test.py`
- [ ] `odoo_install_ubuntu.sh`
- [ ] `backup_odoo_db.py`

### Skills (SKILL.md)
- [ ] `Skills/email_draft_skill.md`
- [ ] `Skills/social_draft_skill.md`
- [ ] `Skills/approval_handler.md`
- [ ] `Skills/odoo_draft_skill.md`
- [ ] `Skills/sync_vault_skill.md`
- [ ] `Skills/health_monitor_skill.md`

### Documentation
- [ ] `Plans/platinum_gaps.md` (this file)
- [ ] `Plans/platinum_progress.md`
- [ ] `DEPLOYMENT.md` (Oracle Cloud guide)
- [ ] `PLATINUM_COMPLETE.md`
- [ ] Update `Company_Handbook.md`
- [ ] Update `Dashboard.md`

### Folder Structure
- [ ] `/Needs_Action/email/`
- [ ] `/Needs_Action/social/`
- [ ] `/Needs_Action/accounting/`
- [ ] `/Needs_Action/whatsapp/` (Local-only)
- [ ] `/Needs_Action/finance/` (Local-only)
- [ ] `/In_Progress/cloud/`
- [ ] `/In_Progress/local/`
- [ ] `/Pending_Approval/email/`
- [ ] `/Pending_Approval/social/`
- [ ] `/Pending_Approval/accounting/`
- [ ] `/Updates/`
- [ ] `/Signals/`

---

**Next Step:** Begin Phase 1 - Foundation by reorganizing folder structure and updating Company_Handbook.md with Platinum rules.
