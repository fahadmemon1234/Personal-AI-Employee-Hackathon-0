#!/usr/bin/env python3
"""
claim_task.py - Atomic Claim-by-Move Operation

Platinum Tier: Prevents double-work by ensuring only one agent can claim a task.
First agent to atomically move file from /Needs_Action/ to /In_Progress/<agent>/ owns it.
Others MUST ignore files already claimed.

Usage:
    python claim_task.py <task_file> <agent_type>
    
Example:
    python claim_task.py email/incoming_001.md cloud
    python claim_task.py whatsapp/message_001.md local
"""

import os
import sys
import shutil
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('claim_task')


class TaskClaimError(Exception):
    """Custom exception for task claiming errors."""
    pass


class TaskClaimer:
    """Handles atomic task claiming via file move operations."""
    
    def __init__(self, vault_path: str = None):
        """
        Initialize the TaskClaimer.
        
        Args:
            vault_path: Base path to the vault. Uses current dir if None.
        """
        if vault_path:
            self.vault_path = Path(vault_path)
        else:
            self.vault_path = Path.cwd()
            
        # Validate vault structure
        self.needs_action_path = self.vault_path / "Needs_Action"
        self.in_progress_cloud_path = self.vault_path / "In_Progress" / "cloud"
        self.in_progress_local_path = self.vault_path / "In_Progress" / "local"
        
        # Ensure directories exist
        self._ensure_directories()
        
    def _ensure_directories(self):
        """Ensure all required directories exist."""
        for path in [
            self.needs_action_path,
            self.in_progress_cloud_path,
            self.in_progress_local_path,
            self.vault_path / "Pending_Approval" / "email",
            self.vault_path / "Pending_Approval" / "social",
            self.vault_path / "Pending_Approval" / "accounting",
            self.vault_path / "Updates",
            self.vault_path / "Signals"
        ]:
            path.mkdir(parents=True, exist_ok=True)
            
    def _get_destination_path(self, agent_type: str) -> Path:
        """
        Get the destination In_Progress path for the agent type.
        
        Args:
            agent_type: Either 'cloud' or 'local'
            
        Returns:
            Path to the appropriate In_Progress directory
        """
        if agent_type.lower() == 'cloud':
            return self.in_progress_cloud_path
        elif agent_type.lower() == 'local':
            return self.in_progress_local_path
        else:
            raise TaskClaimError(f"Invalid agent type: {agent_type}. Must be 'cloud' or 'local'")
    
    def claim(self, task_file: str, agent_type: str) -> Tuple[bool, Optional[str]]:
        """
        Atomically claim a task by moving it from Needs_Action to In_Progress.
        
        Args:
            task_file: Relative path within Needs_Action (e.g., 'email/incoming_001.md')
            agent_type: Either 'cloud' or 'local'
            
        Returns:
            Tuple of (success: bool, message: str or None)
            - (True, None) if claim successful
            - (False, error_message) if claim failed
        """
        source = self.needs_action_path / task_file
        dest_dir = self._get_destination_path(agent_type)
        
        # Preserve subdirectory structure in In_Progress
        task_path = Path(task_file)
        if len(task_path.parts) > 1:
            dest_subdir = dest_dir / task_path.parent
            dest_subdir.mkdir(parents=True, exist_ok=True)
            dest = dest_dir / task_file
        else:
            dest = dest_dir / task_file
            
        try:
            # Check if source exists
            if not source.exists():
                return False, f"Source file does not exist: {source}"
                
            # Check if already claimed (file already in In_Progress)
            if dest.exists():
                return False, f"Task already claimed: {dest}"
                
            # Atomic move (rename on POSIX, fallback to copy+delete on Windows)
            try:
                # Try atomic rename first (works on same filesystem)
                os.rename(source, dest)
                logger.info(f"Task claimed: {task_file} → {agent_type}/{task_file}")
                return True, None
            except OSError:
                # Fallback for cross-filesystem or Windows
                shutil.copy2(source, dest)
                os.remove(source)
                logger.info(f"Task claimed (fallback): {task_file} → {agent_type}/{task_file}")
                return True, None
                
        except PermissionError as e:
            logger.error(f"Permission denied claiming task {task_file}: {e}")
            return False, f"Permission denied: {e}"
        except Exception as e:
            logger.error(f"Error claiming task {task_file}: {e}")
            return False, f"Unexpected error: {e}"
    
    def is_claimed(self, task_file: str) -> Tuple[bool, Optional[str]]:
        """
        Check if a task has already been claimed.
        
        Args:
            task_file: Relative path within Needs_Action
            
        Returns:
            Tuple of (is_claimed: bool, claimed_by: str or None)
        """
        # Check cloud In_Progress
        cloud_dest = self.in_progress_cloud_path / task_file
        if cloud_dest.exists():
            return True, 'cloud'
            
        # Check local In_Progress
        local_dest = self.in_progress_local_path / task_file
        if local_dest.exists():
            return True, 'local'
            
        return False, None
    
    def release(self, task_file: str, agent_type: str, destination: str = "Done") -> Tuple[bool, Optional[str]]:
        """
        Release a claimed task by moving it to final destination.
        
        Args:
            task_file: Relative path within In_Progress
            agent_type: Either 'cloud' or 'local'
            destination: Final destination folder (Done, Completed, Cancelled)
            
        Returns:
            Tuple of (success: bool, message: str or None)
        """
        source_dir = self._get_destination_path(agent_type)
        source = source_dir / task_file
        
        dest_dir = self.vault_path / destination
        dest_dir.mkdir(parents=True, exist_ok=True)
        
        # Preserve subdirectory structure
        task_path = Path(task_file)
        if len(task_path.parts) > 1:
            dest_subdir = dest_dir / task_path.parent
            dest_subdir.mkdir(parents=True, exist_ok=True)
            dest = dest_dir / task_file
        else:
            dest = dest_dir / task_file
            
        try:
            if not source.exists():
                return False, f"Task not found in In_Progress: {source}"
                
            os.rename(source, dest)
            logger.info(f"Task released: {task_file} → {destination}/{task_file}")
            return True, None
            
        except Exception as e:
            logger.error(f"Error releasing task {task_file}: {e}")
            return False, f"Error: {e}"
    
    def list_available_tasks(self, domain: str = None) -> list:
        """
        List all unclaimed tasks in Needs_Action.
        
        Args:
            domain: Optional domain filter (email, social, accounting, etc.)
            
        Returns:
            List of relative file paths available for claiming
        """
        available = []
        
        if domain:
            domain_path = self.needs_action_path / domain
            if domain_path.exists():
                for file_path in domain_path.rglob("*.md"):
                    rel_path = file_path.relative_to(self.needs_action_path)
                    is_claimed, _ = self.is_claimed(str(rel_path))
                    if not is_claimed:
                        available.append(str(rel_path))
        else:
            for file_path in self.needs_action_path.rglob("*.md"):
                rel_path = file_path.relative_to(self.needs_action_path)
                is_claimed, _ = self.is_claimed(str(rel_path))
                if not is_claimed:
                    available.append(str(rel_path))
                    
        return available
    
    def write_status_update(self, task_id: str, status: str, details: str = ""):
        """
        Write a status update to /Updates/ directory.
        Cloud agents use this to communicate progress to Local.
        
        Args:
            task_id: Unique task identifier
            status: Status string (processing, draft_created, waiting_approval, etc.)
            details: Optional additional details
        """
        updates_path = self.vault_path / "Updates"
        updates_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().isoformat()
        update_file = updates_path / f"{task_id}_status.md"
        
        content = f"""---
task_id: {task_id}
status: {status}
timestamp: {timestamp}
agent_type: cloud
---

# Status Update: {task_id}

**Status:** {status}
**Timestamp:** {timestamp}
**Agent:** Cloud Agent

## Details

{details}
"""
        with open(update_file, 'w', encoding='utf-8') as f:
            f.write(content)
            
        logger.info(f"Status update written: {update_file}")
        
    def write_signal(self, signal_type: str, content: str, priority: str = "normal"):
        """
        Write a signal to /Signals/ directory for urgent Cloud→Local communication.
        
        Args:
            signal_type: Type of signal (approval_needed, error, alert, etc.)
            content: Signal content
            priority: Priority level (low, normal, high, urgent)
        """
        signals_path = self.vault_path / "Signals"
        signals_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().isoformat()
        signal_file = signals_path / f"{priority}_{signal_type}_{timestamp.replace(':', '-')}.md"
        
        md_content = f"""---
signal_type: {signal_type}
priority: {priority}
timestamp: {timestamp}
agent_type: cloud
---

# Signal: {signal_type}

**Priority:** {priority}
**Timestamp:** {timestamp}

## Message

{content}
"""
        with open(signal_file, 'w', encoding='utf-8') as f:
            f.write(md_content)
            
        logger.info(f"Signal written: {signal_file}")


def main():
    """CLI entry point for claim_task.py"""
    if len(sys.argv) < 3:
        print("Usage: python claim_task.py <task_file> <agent_type>")
        print("Example: python claim_task.py email/incoming_001.md cloud")
        sys.exit(1)
        
    task_file = sys.argv[1]
    agent_type = sys.argv[2]
    
    claimer = TaskClaimer()
    success, message = claimer.claim(task_file, agent_type)
    
    if success:
        print(f"✓ Task claimed successfully: {task_file} → {agent_type}")
        sys.exit(0)
    else:
        print(f"✗ Failed to claim task: {message}")
        sys.exit(1)


if __name__ == "__main__":
    main()
