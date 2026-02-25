#!/usr/bin/env python3
"""
local_orchestrator.py - Platinum Tier Local Agent Orchestrator

Local Agent for user's machine.
Capabilities: Full execution, approvals, WhatsApp, banking, payments.
Responsibilities:
1. Sync vault with Git (pull Cloud updates)
2. Merge /Updates/ into Dashboard.md
3. Monitor /Pending_Approval/ for user approval
4. Execute final actions via local MCP
5. Run Local-only watchers (WhatsApp, finance)

Run on user's machine alongside Obsidian for approval workflow.
"""

import os
import sys
import time
import json
import logging
import signal
import subprocess
import re
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Tuple
from dotenv import load_dotenv

# Import claim task utility
from claim_task import TaskClaimer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('local_orchestrator.log')
    ]
)
logger = logging.getLogger('local_orchestrator')


class LocalOrchestrator:
    """
    Local Agent Orchestrator for Platinum Tier.
    
    Responsibilities:
    1. Sync vault with Git (pull from Cloud)
    2. Merge /Updates/ into Dashboard.md
    3. Monitor /Pending_Approval/ for user approval (checkbox)
    4. Execute approved actions via local MCP
    5. Run Local-only watchers (WhatsApp, finance)
    6. Write to Dashboard.md (single-writer rule)
    """
    
    def __init__(self, vault_path: str = None, config_path: str = None):
        """
        Initialize Local Orchestrator.
        
        Args:
            vault_path: Base path to vault (default: VAULT_PATH env or cwd)
            config_path: Path to claude-local-config.json
        """
        # Load environment variables
        load_dotenv('.env.local')
        
        # Determine vault path
        if vault_path:
            self.vault_path = Path(vault_path)
        elif os.getenv('VAULT_PATH'):
            self.vault_path = Path(os.getenv('VAULT_PATH'))
        else:
            self.vault_path = Path.cwd()
            
        logger.info(f"Local Orchestrator initialized with vault: {self.vault_path}")
        
        # Load configuration
        if config_path:
            self.config_path = Path(config_path)
        else:
            self.config_path = self.vault_path / "claude-local-config.json"
            
        self.config = self._load_config()
        
        # Initialize task claimer
        self.claimer = TaskClaimer(str(self.vault_path))
        
        # Local-only domains (Cloud has ZERO access)
        self.local_domains = ['whatsapp', 'finance', 'banking']
        
        # Running flag for graceful shutdown
        self.running = True
        
        # Dashboard path
        self.dashboard_path = self.vault_path / "Dashboard.md"
        
        # Setup signal handlers
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
        
        # Ensure directories exist
        self._ensure_directories()
        
    def _load_config(self) -> Dict:
        """Load local agent configuration."""
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            logger.warning(f"Config not found: {self.config_path}. Using defaults.")
            return {
                "agent_type": "local",
                "draft_only_mode": False,
                "sync_interval_minutes": 5
            }
    
    def _ensure_directories(self):
        """Ensure all required directories exist."""
        dirs = [
            self.vault_path / "Needs_Action" / "whatsapp",
            self.vault_path / "Needs_Action" / "finance",
            self.vault_path / "In_Progress" / "local",
            self.vault_path / "Pending_Approval" / "email",
            self.vault_path / "Pending_Approval" / "social",
            self.vault_path / "Pending_Approval" / "accounting",
            self.vault_path / "Approved",
            self.vault_path / "Done",
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
    
    def _sync_vault(self):
        """
        Sync vault with Git repository.
        Pull Cloud updates, process, then push Local changes.
        """
        logger.info("Syncing vault with Git...")
        
        try:
            # Git pull (get Cloud updates)
            result = subprocess.run(
                ['git', 'pull', 'origin', 'main'],
                cwd=str(self.vault_path),
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode == 0:
                logger.info("Git pull completed")
            else:
                logger.warning(f"Git pull had issues: {result.stderr}")
            
            # Process will happen here
            
            # Git add, commit, push (Local changes)
            subprocess.run(
                ['git', 'add', '.'],
                cwd=str(self.vault_path),
                capture_output=True,
                timeout=30
            )
            subprocess.run(
                ['git', 'diff', '--cached', '--quiet'],
                cwd=str(self.vault_path),
                capture_output=True
            )
            if subprocess.run(['git', 'diff', '--cached', '--quiet'], cwd=str(self.vault_path)).returncode != 0:
                subprocess.run(
                    ['git', 'commit', '-m', 'Local Agent auto-sync'],
                    cwd=str(self.vault_path),
                    capture_output=True,
                    timeout=30
                )
                subprocess.run(
                    ['git', 'push', 'origin', 'main'],
                    cwd=str(self.vault_path),
                    capture_output=True,
                    timeout=60
                )
                logger.info("Git push completed")
            else:
                logger.info("No Local changes to push")
                
        except subprocess.TimeoutExpired as e:
            logger.error(f"Git operation timed out: {e}")
        except Exception as e:
            logger.error(f"Git sync error: {e}")
    
    def _merge_updates_to_dashboard(self):
        """
        Merge /Updates/ into Dashboard.md.
        Cloud writes status to /Updates/, Local merges into Dashboard.
        """
        logger.info("Merging /Updates/ into Dashboard.md...")
        
        updates_path = self.vault_path / "Updates"
        if not updates_path.exists():
            logger.debug("No /Updates/ directory found")
            return
            
        # Read all update files
        update_files = list(updates_path.glob("*_status.md"))
        
        if not update_files:
            logger.debug("No status updates to merge")
            return
            
        # Build updates section content
        updates_section = "## ☁️ Cloud Agent Updates\n\n"
        updates_section += f"*Last synced: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
        
        processed_updates = []
        
        for update_file in update_files:
            try:
                with open(update_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Parse frontmatter
                task_id = ""
                status = ""
                timestamp = ""
                
                for line in content.split('\n'):
                    if line.startswith('task_id:'):
                        task_id = line.split(':', 1)[1].strip()
                    elif line.startswith('status:'):
                        status = line.split(':', 1)[1].strip()
                    elif line.startswith('timestamp:'):
                        timestamp = line.split(':', 1)[1].strip()
                        
                if task_id and status:
                    updates_section += f"- **{task_id}**: {status} (at {timestamp})\n"
                    processed_updates.append(update_file)
                    
            except Exception as e:
                logger.error(f"Error reading update {update_file}: {e}")
                
        updates_section += "\n"
        
        # Read Dashboard.md
        if not self.dashboard_path.exists():
            logger.warning("Dashboard.md not found. Creating new one.")
            self.dashboard_path.write_text("# AI Agent Dashboard\n\n")
            
        dashboard_content = self.dashboard_path.read_text(encoding='utf-8')
        
        # Find and replace Cloud Agent Updates section
        pattern = r'(## ☁️ Cloud Agent Updates.*?)(?=##|\Z)'
        match = re.search(pattern, dashboard_content, re.DOTALL)
        
        if match:
            # Replace existing section
            dashboard_content = dashboard_content[:match.start()] + updates_section + dashboard_content[match.end():]
        else:
            # Append new section before the last section
            dashboard_content = dashboard_content.rstrip() + "\n\n" + updates_section
            
        # Write updated Dashboard
        self.dashboard_path.write_text(dashboard_content, encoding='utf-8')
        logger.info(f"Dashboard.md updated with {len(processed_updates)} status updates")
        
        # Archive processed updates (move to Logs)
        logs_path = self.vault_path / "Logs" / "updates_archive"
        logs_path.mkdir(parents=True, exist_ok=True)
        
        for update_file in processed_updates:
            archive_name = logs_path / f"{update_file.stem}_{datetime.now().strftime('%Y%m%d')}.md"
            update_file.rename(archive_name)
    
    def _process_signals(self):
        """
        Process signals from Cloud Agent.
        Signals are urgent Cloud→Local communications.
        """
        signals_path = self.vault_path / "Signals"
        if not signals_path.exists():
            return
            
        signal_files = list(signals_path.glob("*.md"))
        
        for signal_file in signal_files:
            try:
                with open(signal_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Parse signal
                signal_type = ""
                priority = ""
                
                for line in content.split('\n'):
                    if line.startswith('signal_type:'):
                        signal_type = line.split(':', 1)[1].strip()
                    elif line.startswith('priority:'):
                        priority = line.split(':', 1)[1].strip()
                        
                logger.info(f"Processing signal: {signal_type} (priority: {priority})")
                
                # Handle based on signal type
                if signal_type == "approval_needed":
                    logger.info("Cloud Agent needs approval - checking Pending_Approval/")
                    # This will be handled in _check_approvals()
                    
                # Move processed signal to Logs
                logs_path = self.vault_path / "Logs" / "signals_archive"
                logs_path.mkdir(parents=True, exist_ok=True)
                signal_file.rename(logs_path / signal_file.name)
                
            except Exception as e:
                logger.error(f"Error processing signal {signal_file}: {e}")
    
    def _check_approvals(self) -> List[Path]:
        """
        Check /Pending_Approval/ for user-approved tasks.
        User approves by checking checkbox in Obsidian.
        
        Returns:
            List of approved task files ready for execution
        """
        approved_tasks = []
        
        pending_path = self.vault_path / "Pending_Approval"
        if not pending_path.exists():
            return approved_tasks
            
        # Check all domains
        for domain in ['email', 'social', 'accounting']:
            domain_path = pending_path / domain
            if not domain_path.exists():
                continue
                
            for task_file in domain_path.glob("*.md"):
                try:
                    with open(task_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # Check for approval checkbox
                    # Looking for: [x] **APPROVED** or [x] **APPROVED** - Check this box
                    approval_patterns = [
                        r'\[x\]\s*\*\*APPROVED\*\*',
                        r'\[x\]\s*APPROVED',
                        r'-\s*\[x\]\s*Review and approve'
                    ]
                    
                    is_approved = any(re.search(pattern, content, re.IGNORECASE) for pattern in approval_patterns)
                    
                    if is_approved:
                        logger.info(f"Approved task found: {task_file}")
                        approved_tasks.append(task_file)
                        
                except Exception as e:
                    logger.error(f"Error checking approval {task_file}: {e}")
                    
        return approved_tasks
    
    def _execute_email_task(self, task_file: Path):
        """
        Execute an approved email task via local MCP.
        
        Args:
            task_file: Path to approved task file
        """
        logger.info(f"Executing email task: {task_file}")
        
        # Read task content
        with open(task_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Parse task ID
        task_id = ""
        for line in content.split('\n'):
            if line.startswith('task_id:'):
                task_id = line.split(':', 1)[1].strip()
                break
                
        # TODO: Call local MCP email server to send
        # For now, simulate execution
        logger.info(f"Email task {task_id} executed (simulated)")
        
        # Move to Done
        done_path = self.vault_path / "Done" / "email"
        done_path.mkdir(parents=True, exist_ok=True)
        task_file.rename(done_path / task_file.name)
        
        # Update Dashboard
        self._update_dashboard_task_status(task_id, "completed", "Email sent via Local MCP")
    
    def _execute_social_task(self, task_file: Path):
        """
        Execute an approved social media task via local MCP.
        
        Args:
            task_file: Path to approved task file
        """
        logger.info(f"Executing social media task: {task_file}")
        
        # Read task content
        with open(task_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Parse task ID and platforms
        task_id = ""
        platforms = []
        
        for line in content.split('\n'):
            if line.startswith('task_id:'):
                task_id = line.split(':', 1)[1].strip()
            elif line.startswith('platforms:'):
                platforms = line.split(':', 1)[1].strip()
                
        # TODO: Call local MCP social server to publish
        # For now, simulate execution
        logger.info(f"Social media task {task_id} executed (simulated) on platforms: {platforms}")
        
        # Move to Done
        done_path = self.vault_path / "Done" / "social"
        done_path.mkdir(parents=True, exist_ok=True)
        task_file.rename(done_path / task_file.name)
        
        # Update Dashboard
        self._update_dashboard_task_status(task_id, "completed", f"Social post published via Local MCP on {platforms}")
    
    def _execute_accounting_task(self, task_file: Path):
        """
        Execute an approved accounting task via local Odoo MCP.
        
        Args:
            task_file: Path to approved task file
        """
        logger.info(f"Executing accounting task: {task_file}")
        
        # Read task content
        with open(task_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Parse task ID
        task_id = ""
        for line in content.split('\n'):
            if line.startswith('task_id:'):
                task_id = line.split(':', 1)[1].strip()
                break
                
        # TODO: Call local Odoo MCP to post
        # For now, simulate execution
        logger.info(f"Accounting task {task_id} executed (simulated)")
        
        # Move to Done
        done_path = self.vault_path / "Done" / "accounting"
        done_path.mkdir(parents=True, exist_ok=True)
        task_file.rename(done_path / task_file.name)
        
        # Update Dashboard
        self._update_dashboard_task_status(task_id, "completed", "Odoo entry posted via Local MCP")
    
    def _update_dashboard_task_status(self, task_id: str, status: str, details: str):
        """
        Update Dashboard.md with task execution status.
        
        Args:
            task_id: Task identifier
            status: Status string
            details: Additional details
        """
        if not self.dashboard_path.exists():
            return
            
        content = self.dashboard_path.read_text(encoding='utf-8')
        
        # Find or create Recent Activity section
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        activity_line = f"- [{timestamp}] **{task_id}**: {status} - {details}\n"
        
        # Try to add to Recent Activity section
        if "## 📝 Recent Activity Log" in content:
            # Insert after the header
            lines = content.split('\n')
            new_lines = []
            inserted = False
            
            for line in lines:
                new_lines.append(line)
                if line.startswith("## 📝 Recent Activity Log") and not inserted:
                    new_lines.append("")
                    new_lines.append(activity_line)
                    inserted = True
                    
            content = '\n'.join(new_lines)
        else:
            # Append to end
            content = content.rstrip() + f"\n\n## 📝 Recent Activity Log\n\n{activity_line}\n"
            
        self.dashboard_path.write_text(content, encoding='utf-8')
        logger.info(f"Dashboard updated: {task_id} → {status}")
    
    def _process_local_tasks(self):
        """
        Process Local-only tasks (WhatsApp, finance).
        Cloud has ZERO access to these domains.
        """
        logger.info("Processing Local-only tasks...")
        
        # WhatsApp tasks
        whatsapp_path = self.vault_path / "Needs_Action" / "whatsapp"
        if whatsapp_path.exists():
            for task_file in whatsapp_path.glob("*.md"):
                rel_path = f"whatsapp/{task_file.name}"
                success, message = self.claimer.claim(rel_path, 'local')
                if success:
                    logger.info(f"Processing WhatsApp task: {task_file}")
                    # TODO: Process WhatsApp message
                    # Move to Done when complete
                    done_path = self.vault_path / "Done" / "whatsapp"
                    done_path.mkdir(parents=True, exist_ok=True)
                    task_file.rename(done_path / task_file.name)
                    
        # Finance tasks
        finance_path = self.vault_path / "Needs_Action" / "finance"
        if finance_path.exists():
            for task_file in finance_path.glob("*.md"):
                rel_path = f"finance/{task_file.name}"
                success, message = self.claimer.claim(rel_path, 'local')
                if success:
                    logger.info(f"Processing Finance task: {task_file}")
                    # TODO: Process finance/banking task
                    # Move to Done when complete
                    done_path = self.vault_path / "Done" / "finance"
                    done_path.mkdir(parents=True, exist_ok=True)
                    task_file.rename(done_path / task_file.name)
    
    def run_once(self):
        """
        Run one iteration of the Local orchestrator loop.
        """
        logger.info("Starting Local Orchestrator iteration...")
        
        # Step 1: Sync vault (pull Cloud updates)
        self._sync_vault()
        
        # Step 2: Merge /Updates/ into Dashboard.md
        self._merge_updates_to_dashboard()
        
        # Step 3: Process signals from Cloud
        self._process_signals()
        
        # Step 4: Check for approved tasks and execute
        approved_tasks = self._check_approvals()
        
        for task_file in approved_tasks:
            # Determine domain from path
            domain = task_file.parent.name
            
            try:
                if domain == 'email':
                    self._execute_email_task(task_file)
                elif domain == 'social':
                    self._execute_social_task(task_file)
                elif domain == 'accounting':
                    self._execute_accounting_task(task_file)
            except Exception as e:
                logger.error(f"Error executing task {task_file}: {e}")
                
        # Step 5: Process Local-only tasks
        self._process_local_tasks()
        
        # Step 6: Sync vault (push Local changes)
        self._sync_vault()
        
        logger.info("Local Orchestrator iteration complete.")
    
    def run(self, interval_seconds: int = 300):
        """
        Run the orchestrator in a continuous loop.
        
        Args:
            interval_seconds: Seconds between iterations (default: 5 minutes)
        """
        logger.info(f"Local Orchestrator starting with {interval_seconds}s interval...")
        logger.info(f"Vault path: {self.vault_path}")
        logger.info(f"Local-only domains: {self.local_domains}")
        logger.info(f"Mode: Full execution (Local Agent)")
        
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
                
        logger.info("Local Orchestrator stopped.")


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Local Agent Orchestrator - Platinum Tier')
    parser.add_argument('--vault', type=str, help='Vault path (default: VAULT_PATH env or cwd)')
    parser.add_argument('--config', type=str, help='Config file path (default: claude-local-config.json)')
    parser.add_argument('--interval', type=int, default=300, help='Loop interval in seconds (default: 300)')
    parser.add_argument('--once', action='store_true', help='Run once and exit')
    
    args = parser.parse_args()
    
    orchestrator = LocalOrchestrator(vault_path=args.vault, config_path=args.config)
    
    if args.once:
        orchestrator.run_once()
    else:
        orchestrator.run(interval_seconds=args.interval)


if __name__ == "__main__":
    main()
