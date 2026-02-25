#!/usr/bin/env python3
"""
cloud_orchestrator.py - Platinum Tier Cloud Agent Orchestrator

24/7 Always-On Cloud Agent for Oracle Cloud Free Tier VM.
Capabilities: Email triage, draft replies, social media drafts, Odoo drafts.
RESTRICTIONS: Draft-only mode. Cannot send emails, publish posts, or execute actions.
All drafts written to /Pending_Approval/<domain>/ for Local approval.

Run via supervisor/systemd for 24/7 operation.
"""

import os
import sys
import time
import json
import logging
import signal
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List
from dotenv import load_dotenv

# Import claim task utility
from claim_task import TaskClaimer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('cloud_orchestrator.log')
    ]
)
logger = logging.getLogger('cloud_orchestrator')


class CloudOrchestrator:
    """
    Cloud Agent Orchestrator for Platinum Tier.
    
    Responsibilities:
    1. Monitor /Needs_Action/<domain>/ for new tasks
    2. Claim tasks atomically (claim-by-move rule)
    3. Process tasks in draft-only mode
    4. Write drafts to /Pending_Approval/<domain>/
    5. Write status updates to /Updates/
    6. Signal Local agent when approval needed
    """
    
    def __init__(self, vault_path: str = None, config_path: str = None):
        """
        Initialize Cloud Orchestrator.
        
        Args:
            vault_path: Base path to vault (default: VAULT_PATH env or cwd)
            config_path: Path to claude-cloud-config.json
        """
        # Load environment variables
        load_dotenv('.env.cloud')
        
        # Determine vault path
        if vault_path:
            self.vault_path = Path(vault_path)
        elif os.getenv('VAULT_PATH'):
            self.vault_path = Path(os.getenv('VAULT_PATH'))
        else:
            self.vault_path = Path.cwd()
            
        logger.info(f"Cloud Orchestrator initialized with vault: {self.vault_path}")
        
        # Load configuration
        if config_path:
            self.config_path = Path(config_path)
        else:
            self.config_path = self.vault_path / "claude-cloud-config.json"
            
        self.config = self._load_config()
        
        # Initialize task claimer
        self.claimer = TaskClaimer(str(self.vault_path))
        
        # Domains this cloud agent handles
        self.cloud_domains = ['email', 'social', 'accounting']
        
        # Running flag for graceful shutdown
        self.running = True
        
        # Setup signal handlers
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
        
        # Ensure directories exist
        self._ensure_directories()
        
    def _load_config(self) -> Dict:
        """Load cloud agent configuration."""
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            logger.warning(f"Config not found: {self.config_path}. Using defaults.")
            return {
                "agent_type": "cloud",
                "draft_only_mode": True,
                "sync_interval_minutes": 5
            }
    
    def _ensure_directories(self):
        """Ensure all required directories exist."""
        dirs = [
            self.vault_path / "Needs_Action" / "email",
            self.vault_path / "Needs_Action" / "social",
            self.vault_path / "Needs_Action" / "accounting",
            self.vault_path / "In_Progress" / "cloud",
            self.vault_path / "Pending_Approval" / "email",
            self.vault_path / "Pending_Approval" / "social",
            self.vault_path / "Pending_Approval" / "accounting",
            self.vault_path / "Updates",
            self.vault_path / "Signals",
            self.vault_path / "Logs"
        ]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        logger.info(f"Received signal {signum}. Shutting down gracefully...")
        self.running = False
    
    def _generate_task_id(self, content: str) -> str:
        """Generate unique task ID from content."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        hash_suffix = hashlib.md5(content.encode()).hexdigest()[:8]
        return f"TASK_{timestamp}_{hash_suffix}"
    
    def _scan_needs_action(self) -> Dict[str, List[str]]:
        """
        Scan /Needs_Action/ for unclaimed tasks by domain.
        
        Returns:
            Dict mapping domain to list of unclaimed task files
        """
        tasks = {}
        
        for domain in self.cloud_domains:
            domain_path = self.vault_path / "Needs_Action" / domain
            if not domain_path.exists():
                tasks[domain] = []
                continue
                
            domain_tasks = []
            for file_path in domain_path.rglob("*.md"):
                rel_path = str(file_path.relative_to(self.vault_path / "Needs_Action"))
                is_claimed, claimed_by = self.claimer.is_claimed(rel_path)
                if not is_claimed:
                    domain_tasks.append(rel_path)
                    
            tasks[domain] = domain_tasks
            
        return tasks
    
    def _process_email_task(self, task_file: str) -> bool:
        """
        Process an email task: triage and draft reply.
        
        Args:
            task_file: Relative path to task file
            
        Returns:
            True if processed successfully
        """
        logger.info(f"Processing email task: {task_file}")
        
        # Read task content
        task_path = self.vault_path / "Needs_Action" / task_file
        with open(task_path, 'r', encoding='utf-8') as f:
            task_content = f.read()
            
        # Generate task ID
        task_id = self._generate_task_id(task_content)
        
        # Write status update
        self.claimer.write_status_update(
            task_id,
            "processing",
            f"Cloud Agent triaging email: {task_file}"
        )
        
        # TODO: Integrate with Claude Code or LLM for draft generation
        # For now, create a simple draft template
        draft_content = self._create_email_draft(task_content, task_id, task_file)
        
        # Write draft to Pending_Approval
        draft_path = self.vault_path / "Pending_Approval" / "email" / f"{task_id}.md"
        with open(draft_path, 'w', encoding='utf-8') as f:
            f.write(draft_content)
            
        logger.info(f"Email draft created: {draft_path}")
        
        # Update status
        self.claimer.write_status_update(
            task_id,
            "draft_created",
            f"Draft reply created and waiting for Local approval: {draft_path}"
        )
        
        # Signal Local agent
        self.claimer.write_signal(
            "approval_needed",
            f"Email draft ready for approval: {task_id}",
            "normal"
        )
        
        return True
    
    def _create_email_draft(self, task_content: str, task_id: str, task_file: str) -> str:
        """
        Create email draft reply.
        
        Args:
            task_content: Original email content
            task_id: Generated task ID
            task_file: Original task file path
            
        Returns:
            Markdown-formatted draft with approval checkbox
        """
        timestamp = datetime.now().isoformat()
        
        # Extract subject if possible (simple parsing)
        subject = "Email Reply"
        for line in task_content.split('\n'):
            if line.lower().startswith('subject:'):
                subject = line.split(':', 1)[1].strip()
                break
                
        return f"""---
task_id: {task_id}
task_type: email_reply
source: {task_file}
created: {timestamp}
agent: cloud
status: pending_approval
domain: email
---

# Email Draft Reply

**Task ID:** {task_id}
**Source:** {task_file}
**Created:** {timestamp}
**Agent:** Cloud Agent (Draft Only)

---

## Original Email

```
{task_content}
```

---

## Draft Reply

**Subject:** Re: {subject}

> [!NOTE] CLOUD AGENT DRAFT - REQUIRES LOCAL APPROVAL
> This is a DRAFT reply generated by the Cloud Agent.
> Local Agent MUST review and approve before sending.

[ ] **APPROVED** - Check this box to approve sending this email

---

## Suggested Reply Content

[AI-generated reply would go here]

---

## Approval Workflow

1. **Cloud Agent:** Created draft (this file)
2. **Local Agent:** [ ] Review and approve (check box above)
3. **Local Agent:** Execute send via local MCP
4. **Local Agent:** Move to /Done/ and log action

---

**Security:** This draft was created by Cloud Agent with ZERO access to secrets.
Final send will be executed by Local Agent with full credentials.
"""
    
    def _process_social_task(self, task_file: str) -> bool:
        """
        Process a social media task: create draft post.
        
        Args:
            task_file: Relative path to task file
            
        Returns:
            True if processed successfully
        """
        logger.info(f"Processing social media task: {task_file}")
        
        # Read task content
        task_path = self.vault_path / "Needs_Action" / task_file
        with open(task_path, 'r', encoding='utf-8') as f:
            task_content = f.read()
            
        # Generate task ID
        task_id = self._generate_task_id(task_content)
        
        # Write status update
        self.claimer.write_status_update(
            task_id,
            "processing",
            f"Cloud Agent creating social media draft: {task_file}"
        )
        
        # Create draft post
        draft_content = self._create_social_draft(task_content, task_id, task_file)
        
        # Write draft to Pending_Approval
        draft_path = self.vault_path / "Pending_Approval" / "social" / f"{task_id}.md"
        with open(draft_path, 'w', encoding='utf-8') as f:
            f.write(draft_content)
            
        logger.info(f"Social media draft created: {draft_path}")
        
        # Update status
        self.claimer.write_status_update(
            task_id,
            "draft_created",
            f"Social media draft created and waiting for Local approval: {draft_path}"
        )
        
        # Signal Local agent
        self.claimer.write_signal(
            "approval_needed",
            f"Social media draft ready for approval: {task_id}",
            "normal"
        )
        
        return True
    
    def _create_social_draft(self, task_content: str, task_id: str, task_file: str) -> str:
        """Create social media draft post."""
        timestamp = datetime.now().isoformat()
        
        return f"""---
task_id: {task_id}
task_type: social_media_post
source: {task_file}
created: {timestamp}
agent: cloud
status: pending_approval
domain: social
platforms: [facebook, instagram, x]
---

# Social Media Draft Post

**Task ID:** {task_id}
**Source:** {task_file}
**Created:** {timestamp}
**Agent:** Cloud Agent (Draft Only)

---

## Request

```
{task_content}
```

---

## Draft Post Content

> [!NOTE] CLOUD AGENT DRAFT - REQUIRES LOCAL APPROVAL
> This is a DRAFT post generated by the Cloud Agent.
> Local Agent MUST review and approve before publishing.

[ ] **APPROVED** - Check this box to publish this post

### Post Text

[AI-generated post content would go here]

### Suggested Platforms

- [ ] Facebook
- [ ] Instagram
- [ ] X (Twitter)
- [ ] LinkedIn

---

## Approval Workflow

1. **Cloud Agent:** Created draft (this file)
2. **Local Agent:** [ ] Review and approve (check box above)
3. **Local Agent:** Execute publish via local MCP
4. **Local Agent:** Move to /Done/ and log action

---

**Security:** This draft was created by Cloud Agent with ZERO access to social media credentials.
Final publish will be executed by Local Agent with full API access.
"""
    
    def _process_accounting_task(self, task_file: str) -> bool:
        """
        Process an accounting task: create draft Odoo invoice/journal entry.
        
        Args:
            task_file: Relative path to task file
            
        Returns:
            True if processed successfully
        """
        logger.info(f"Processing accounting task: {task_file}")
        
        # Read task content
        task_path = self.vault_path / "Needs_Action" / task_file
        with open(task_path, 'r', encoding='utf-8') as f:
            task_content = f.read()
            
        # Generate task ID
        task_id = self._generate_task_id(task_content)
        
        # Write status update
        self.claimer.write_status_update(
            task_id,
            "processing",
            f"Cloud Agent creating Odoo draft: {task_file}"
        )
        
        # Create draft invoice/entry
        draft_content = self._create_odoo_draft(task_content, task_id, task_file)
        
        # Write draft to Pending_Approval
        draft_path = self.vault_path / "Pending_Approval" / "accounting" / f"{task_id}.md"
        with open(draft_path, 'w', encoding='utf-8') as f:
            f.write(draft_content)
            
        logger.info(f"Odoo draft created: {draft_path}")
        
        # Update status
        self.claimer.write_status_update(
            task_id,
            "draft_created",
            f"Odoo draft created and waiting for Local approval: {draft_path}"
        )
        
        return True
    
    def _create_odoo_draft(self, task_content: str, task_id: str, task_file: str) -> str:
        """Create Odoo draft invoice/journal entry."""
        timestamp = datetime.now().isoformat()
        
        return f"""---
task_id: {task_id}
task_type: odoo_draft
source: {task_file}
created: {timestamp}
agent: cloud
status: pending_approval
domain: accounting
---

# Odoo Draft Entry

**Task ID:** {task_id}
**Source:** {task_file}
**Created:** {timestamp}
**Agent:** Cloud Agent (Draft Only)

---

## Request

```
{task_content}
```

---

## Draft Entry Details

> [!NOTE] CLOUD AGENT DRAFT - REQUIRES LOCAL APPROVAL
> This is a DRAFT entry generated by the Cloud Agent.
> Local Agent MUST review and approve before posting to Odoo.

[ ] **APPROVED** - Check this box to post this entry to Odoo

### Entry Type

- [ ] Customer Invoice
- [ ] Vendor Bill
- [ ] Journal Entry

### Draft Details

[AI-generated Odoo entry details would go here]

---

## Approval Workflow

1. **Cloud Agent:** Created draft (this file)
2. **Local Agent:** [ ] Review and approve (check box above)
3. **Local Agent:** Execute post via local Odoo MCP
4. **Local Agent:** Move to /Done/ and log action

---

**Security:** This draft was created by Cloud Agent with draft-only Odoo access.
Final post will be executed by Local Agent with full posting permissions.
"""
    
    def _sync_vault(self):
        """
        Sync vault with Git repository.
        Pull before processing, push after processing.
        """
        logger.info("Syncing vault with Git...")
        
        try:
            # Git pull
            os.system('git pull origin main')
            logger.info("Git pull completed")
            
            # Process will happen here
            
            # Git add, commit, push
            os.system('git add .')
            os.system('git diff --cached --quiet || git commit -m "Cloud Agent auto-sync"')
            os.system('git push origin main')
            logger.info("Git push completed")
            
        except Exception as e:
            logger.error(f"Git sync error: {e}")
    
    def run_once(self):
        """
        Run one iteration of the orchestrator loop.
        Scan, claim, process, and update.
        """
        logger.info("Starting Cloud Orchestrator iteration...")
        
        # Sync vault first
        self._sync_vault()
        
        # Scan for available tasks
        tasks = self._scan_needs_action()
        
        total_tasks = sum(len(task_list) for task_list in tasks.values())
        logger.info(f"Found {total_tasks} unclaimed tasks across domains: {tasks}")
        
        # Process tasks by domain
        for domain, task_files in tasks.items():
            for task_file in task_files:
                if not self.running:
                    logger.info("Shutdown requested. Stopping processing.")
                    return
                    
                # Claim the task atomically
                success, message = self.claimer.claim(task_file, 'cloud')
                
                if not success:
                    logger.warning(f"Could not claim task {task_file}: {message}")
                    continue
                    
                logger.info(f"Claimed task: {task_file}")
                
                # Process based on domain
                try:
                    if domain.startswith('email'):
                        self._process_email_task(task_file)
                    elif domain.startswith('social'):
                        self._process_social_task(task_file)
                    elif domain.startswith('accounting'):
                        self._process_accounting_task(task_file)
                    else:
                        logger.warning(f"Unknown domain: {domain}")
                        
                except Exception as e:
                    logger.error(f"Error processing task {task_file}: {e}")
                    # Write error to Updates
                    task_id = self._generate_task_id(task_file)
                    self.claimer.write_status_update(
                        task_id,
                        "error",
                        f"Error processing task: {e}"
                    )
        
        # Final sync
        self._sync_vault()
        
        logger.info("Cloud Orchestrator iteration complete.")
    
    def run(self, interval_seconds: int = 300):
        """
        Run the orchestrator in a continuous loop.
        
        Args:
            interval_seconds: Seconds between iterations (default: 5 minutes)
        """
        logger.info(f"Cloud Orchestrator starting with {interval_seconds}s interval...")
        logger.info(f"Vault path: {self.vault_path}")
        logger.info(f"Domains: {self.cloud_domains}")
        logger.info(f"Mode: Draft-only (Cloud Agent)")
        
        while self.running:
            try:
                self.run_once()
            except Exception as e:
                logger.error(f"Error in orchestrator loop: {e}")
                
            # Sleep until next iteration
            for _ in range(interval_seconds):
                if not self.running:
                    break
                time.sleep(1)
                
        logger.info("Cloud Orchestrator stopped.")


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Cloud Agent Orchestrator - Platinum Tier')
    parser.add_argument('--vault', type=str, help='Vault path (default: VAULT_PATH env or cwd)')
    parser.add_argument('--config', type=str, help='Config file path (default: claude-cloud-config.json)')
    parser.add_argument('--interval', type=int, default=300, help='Loop interval in seconds (default: 300)')
    parser.add_argument('--once', action='store_true', help='Run once and exit')
    
    args = parser.parse_args()
    
    orchestrator = CloudOrchestrator(vault_path=args.vault, config_path=args.config)
    
    if args.once:
        orchestrator.run_once()
    else:
        orchestrator.run(interval_seconds=args.interval)


if __name__ == "__main__":
    main()
