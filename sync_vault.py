#!/usr/bin/env python3
"""
sync_vault.py - Platinum Tier Vault Synchronization

Git-based synchronization between Cloud and Local agents.
Runs on both Cloud VM and Local machine via cron/systemd.

Usage:
    python sync_vault.py --mode pull    # Pull from remote
    python sync_vault.py --mode push    # Push to remote
    python sync_vault.py --mode sync    # Pull, process, push
    python sync_vault.py --mode status  # Check sync status
"""

import os
import sys
import subprocess
import logging
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('sync_vault')


class VaultSync:
    """Handles Git-based vault synchronization."""
    
    def __init__(self, vault_path: str = None, remote: str = 'origin', branch: str = 'main'):
        """
        Initialize Vault Sync.
        
        Args:
            vault_path: Base path to vault (default: VAULT_PATH env or cwd)
            remote: Git remote name (default: origin)
            branch: Git branch name (default: main)
        """
        if vault_path:
            self.vault_path = Path(vault_path)
        elif os.getenv('VAULT_PATH'):
            self.vault_path = Path(os.getenv('VAULT_PATH'))
        else:
            self.vault_path = Path.cwd()
            
        self.remote = remote
        self.branch = branch
        
        # Verify vault is a git repository
        git_dir = self.vault_path / ".git"
        if not git_dir.exists():
            logger.warning(f"Not a git repository: {self.vault_path}")
            
    def _run_git(self, *args, timeout: int = 60) -> Tuple[bool, str, str]:
        """
        Run a git command.
        
        Args:
            *args: Git command arguments
            timeout: Command timeout in seconds
            
        Returns:
            Tuple of (success, stdout, stderr)
        """
        try:
            result = subprocess.run(
                ['git'] + list(args),
                cwd=str(self.vault_path),
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Command timed out"
        except Exception as e:
            return False, "", str(e)
    
    def pull(self) -> Tuple[bool, str]:
        """
        Pull changes from remote.
        
        Returns:
            Tuple of (success, message)
        """
        logger.info(f"Pulling from {self.remote}/{self.branch}...")
        
        success, stdout, stderr = self._run_git('pull', self.remote, self.branch)
        
        if success:
            logger.info("Pull completed successfully")
            return True, stdout or "Pull completed"
        else:
            logger.error(f"Pull failed: {stderr}")
            return False, stderr
            
    def push(self) -> Tuple[bool, str]:
        """
        Push changes to remote.
        
        Returns:
            Tuple of (success, message)
        """
        logger.info(f"Pushing to {self.remote}/{self.branch}...")
        
        # First check if there are changes to commit
        success, stdout, stderr = self._run_git('status', '--porcelain')
        
        if not success:
            return False, f"Git status failed: {stderr}"
            
        if not stdout.strip():
            logger.info("No changes to push")
            return True, "No changes"
            
        # Add all changes
        success, stdout, stderr = self._run_git('add', '.')
        if not success:
            return False, f"Git add failed: {stderr}"
            
        # Commit
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        success, stdout, stderr = self._run_git(
            'commit', '-m', f'Auto-sync {timestamp}'
        )
        
        if not success and 'nothing to commit' not in stderr:
            return False, f"Git commit failed: {stderr}"
            
        # Push
        success, stdout, stderr = self._run_git('push', self.remote, self.branch)
        
        if success:
            logger.info("Push completed successfully")
            return True, stdout or "Push completed"
        else:
            logger.error(f"Push failed: {stderr}")
            return False, stderr
            
    def sync(self) -> Tuple[bool, str]:
        """
        Full sync: pull, then push.
        
        Returns:
            Tuple of (success, message)
        """
        logger.info("Starting full sync...")
        
        # Pull first
        success, message = self.pull()
        if not success:
            return False, f"Pull failed: {message}"
            
        # Then push
        success, message = self.push()
        if not success:
            return False, f"Push failed: {message}"
            
        return True, "Full sync completed"
    
    def status(self) -> str:
        """
        Get git status.
        
        Returns:
            Status string
        """
        success, stdout, stderr = self._run_git('status')
        
        if not success:
            return f"Error: {stderr}"
            
        return stdout
        
    def get_last_commit(self) -> str:
        """
        Get last commit info.
        
        Returns:
            Last commit string
        """
        success, stdout, stderr = self._run_git('log', '-1', '--format=%h %s (%ci)')
        
        if not success:
            return f"Error: {stderr}"
            
        return stdout.strip()
    
    def check_conflicts(self) -> list:
        """
        Check for merge conflicts.
        
        Returns:
            List of conflicting files
        """
        conflicts = []
        
        # Check for unmerged files
        success, stdout, stderr = self._run_git('diff', '--name-only', '--diff-filter=U')
        
        if success and stdout.strip():
            conflicts.extend(stdout.strip().split('\n'))
            
        return conflicts
    
    def resolve_conflicts(self, strategy: str = 'ours') -> Tuple[bool, str]:
        """
        Resolve merge conflicts.
        
        Args:
            strategy: 'ours' (keep local) or 'theirs' (keep remote)
            
        Returns:
            Tuple of (success, message)
        """
        logger.info(f"Resolving conflicts with '{strategy}' strategy...")
        
        conflicts = self.check_conflicts()
        
        if not conflicts:
            return True, "No conflicts to resolve"
            
        for file in conflicts:
            if strategy == 'ours':
                self._run_git('checkout', '--ours', file)
            elif strategy == 'theirs':
                self._run_git('checkout', '--theirs', file)
                
        # Add resolved files
        self._run_git('add', '.')
        
        return True, f"Resolved {len(conflicts)} conflicts"


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description='Vault Sync - Platinum Tier')
    parser.add_argument('--vault', type=str, help='Vault path (default: VAULT_PATH env or cwd)')
    parser.add_argument('--remote', type=str, default='origin', help='Git remote (default: origin)')
    parser.add_argument('--branch', type=str, default='main', help='Git branch (default: main)')
    parser.add_argument('--mode', type=str, choices=['pull', 'push', 'sync', 'status'], required=True,
                       help='Sync mode')
    parser.add_argument('--strategy', type=str, choices=['ours', 'theirs'], default='ours',
                       help='Conflict resolution strategy')
    
    args = parser.parse_args()
    
    sync = VaultSync(vault_path=args.vault, remote=args.remote, branch=args.branch)
    
    if args.mode == 'pull':
        success, message = sync.pull()
        print(f"{'✓' if success else '✗'} {message}")
        sys.exit(0 if success else 1)
        
    elif args.mode == 'push':
        success, message = sync.push()
        print(f"{'✓' if success else '✗'} {message}")
        sys.exit(0 if success else 1)
        
    elif args.mode == 'sync':
        success, message = sync.sync()
        print(f"{'✓' if success else '✗'} {message}")
        sys.exit(0 if success else 1)
        
    elif args.mode == 'status':
        status = sync.status()
        last_commit = sync.get_last_commit()
        conflicts = sync.check_conflicts()
        
        print("=== Vault Sync Status ===")
        print(f"Vault: {sync.vault_path}")
        print(f"Remote: {sync.remote}/{sync.branch}")
        print()
        print("=== Git Status ===")
        print(status)
        print()
        print(f"=== Last Commit ===")
        print(last_commit)
        
        if conflicts:
            print()
            print(f"=== CONFLICTS ({len(conflicts)}) ===")
            for c in conflicts:
                print(f"  ! {c}")
        else:
            print()
            print("=== No conflicts ===")
            
        sys.exit(0)


if __name__ == "__main__":
    main()
