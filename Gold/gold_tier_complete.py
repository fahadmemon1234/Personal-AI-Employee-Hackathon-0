"""
Gold Tier Complete - Master Skill

Orchestrates all Gold Tier skills and provides unified interface.
This is the main entry point for Gold Tier functionality.

Gold Tier Features:
1. MCP Servers (5 servers)
2. Weekly CEO Briefing
3. Ralph Wiggum Autonomous Loop
4. Error Recovery with Exponential Backoff
5. Audit Logging
6. Cross-Domain Workflows
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# Add Gold directory to path
GOLD_DIR = Path(__file__).parent
sys.path.insert(0, str(GOLD_DIR))

# Import Gold Tier modules
try:
    from audit_logger import audit_logger, log_action, get_daily_summary
    AUDIT_AVAILABLE = True
except ImportError:
    AUDIT_AVAILABLE = False
    print("Warning: audit_logger not available")

try:
    from error_recovery import (
        retry_with_backoff,
        resilient_api_call,
        get_recovery_status,
        circuit_breakers,
        offline_queues
    )
    ERROR_RECOVERY_AVAILABLE = True
except ImportError:
    ERROR_RECOVERY_AVAILABLE = False
    print("Warning: error_recovery not available")

try:
    from ralph_orchestrator import RalphWiggumLoop
    RALPH_AVAILABLE = True
except ImportError:
    RALPH_AVAILABLE = False
    print("Warning: ralph_orchestrator not available")

try:
    from Skills.weekly_ceo_briefing import WeeklyCEOBriefing
    BRIEFING_AVAILABLE = True
except ImportError as e:
    BRIEFING_AVAILABLE = False
    print(f"Warning: weekly_ceo_briefing not available - {e}")


class GoldTierComplete:
    """
    Gold Tier Complete - Master Skill Orchestrator
    
    Provides unified interface to all Gold Tier features:
    - MCP Server management
    - Weekly CEO Briefings
    - Ralph Wiggum Autonomous Loop
    - Error Recovery
    - Audit Logging
    """
    
    def __init__(self):
        self.status = {
            'tier': 'Gold',
            'version': '1.0',
            'initialized_at': datetime.now().isoformat(),
            'features': {}
        }
        
        # Check feature availability
        self.status['features']['audit_logging'] = AUDIT_AVAILABLE
        self.status['features']['error_recovery'] = ERROR_RECOVERY_AVAILABLE
        self.status['features']['ralph_wiggum'] = RALPH_AVAILABLE
        self.status['features']['ceo_briefing'] = BRIEFING_AVAILABLE
        
        # MCP Servers
        self.mcp_servers = {
            'email': {'port': 8080, 'status': 'unknown'},
            'browser': {'port': 8081, 'status': 'unknown'},
            'odoo': {'port': 8082, 'status': 'unknown'},
            'social': {'port': 8083, 'status': 'unknown'},
            'x': {'port': 8084, 'status': 'unknown'}
        }
        
        print("="*70)
        print("Gold Tier Complete - Master Skill")
        print("="*70)
        print(f"Initialized: {self.status['initialized_at']}")
        print(f"Features Available: {sum(self.status['features'].values())}/4")
        print("="*70)
    
    def log_action(self, action: str, actor: str = 'system', **kwargs):
        """Log action with audit trail"""
        if AUDIT_AVAILABLE:
            log_action(action=action, actor=actor, **kwargs)
    
    def get_mcp_status(self) -> Dict[str, Any]:
        """Get status of all MCP servers"""
        import requests
        
        for name, config in self.mcp_servers.items():
            try:
                response = requests.get(f"http://localhost:{config['port']}/health", timeout=5)
                if response.status_code == 200:
                    config['status'] = 'healthy'
                else:
                    config['status'] = 'unhealthy'
            except:
                config['status'] = 'offline'
        
        return self.mcp_servers
    
    def run_ceo_briefing(self) -> str:
        """Generate weekly CEO briefing"""
        if not BRIEFING_AVAILABLE:
            return "Error: Weekly CEO Briefing not available"
        
        briefing = WeeklyCEOBriefing()
        briefing_path = briefing.generate()
        
        self.log_action(
            action='ceo_briefing_generated',
            actor='gold_tier',
            details={'briefing_path': str(briefing_path)}
        )
        
        return briefing_path
    
    def run_ralph_loop(self, task: str, max_iterations: int = 20) -> Dict[str, Any]:
        """Run Ralph Wiggum autonomous loop"""
        if not RALPH_AVAILABLE:
            return {'error': 'Ralph Wiggum Loop not available'}
        
        loop = RalphWiggumLoop(task=task, max_iterations=max_iterations)
        final_state = loop.run()
        
        self.log_action(
            action='ralph_loop_completed',
            actor='gold_tier',
            details={
                'task': task,
                'status': final_state.get('status'),
                'iterations': final_state.get('iterations')
            }
        )
        
        return final_state
    
    def get_recovery_status(self) -> Dict[str, Any]:
        """Get error recovery system status"""
        if not ERROR_RECOVERY_AVAILABLE:
            return {'error': 'Error recovery not available'}
        
        return get_recovery_status()
    
    def get_audit_summary(self, date: str = None) -> Dict[str, Any]:
        """Get audit log summary"""
        if not AUDIT_AVAILABLE:
            return {'error': 'Audit logging not available'}
        
        return get_daily_summary(date)
    
    def get_full_status(self) -> Dict[str, Any]:
        """Get complete Gold Tier status"""
        status = {
            'tier_status': self.status,
            'mcp_servers': self.get_mcp_status(),
            'timestamp': datetime.now().isoformat()
        }
        
        if AUDIT_AVAILABLE:
            status['audit_summary'] = self.get_audit_summary()
        
        if ERROR_RECOVERY_AVAILABLE:
            status['recovery_status'] = self.get_recovery_status()
        
        return status
    
    def print_status(self):
        """Print formatted status report"""
        status = self.get_full_status()
        
        print("\n" + "="*70)
        print("Gold Tier Complete - Status Report")
        print("="*70)
        
        # MCP Servers
        print("\nMCP Servers:")
        for name, config in status['mcp_servers'].items():
            icon = "✅" if config['status'] == 'healthy' else "❌"
            print(f"  {icon} {name.upper()}: Port {config['port']} - {config['status']}")
        
        # Features
        print("\nFeatures:")
        for feature, available in self.status['features'].items():
            icon = "✅" if available else "❌"
            print(f"  {icon} {feature.replace('_', ' ').title()}: {'Available' if available else 'Not Available'}")
        
        # Audit Summary
        if 'audit_summary' in status:
            summary = status['audit_summary']
            print(f"\nAudit Log (Today):")
            print(f"  Total Entries: {summary.get('total_entries', 0)}")
            print(f"  By Result: {summary.get('by_result', {})}")
        
        # Recovery Status
        if 'recovery_status' in status:
            recovery = status['recovery_status']
            print(f"\nError Recovery:")
            for name, cb_status in recovery.get('circuit_breakers', {}).items():
                state = cb_status.get('state', 'unknown')
                icon = "🟢" if state == 'CLOSED' else "🔴" if state == 'OPEN' else "🟡"
                print(f"  {icon} {name}: {state}")
        
        print("\n" + "="*70)


def main():
    """Main entry point for Gold Tier Complete"""
    import argparse
    
    # Fix Windows console encoding
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8')
    
    parser = argparse.ArgumentParser(description='Gold Tier Complete - Master Skill')
    parser.add_argument('--status', action='store_true', help='Show full status')
    parser.add_argument('--ceo-briefing', action='store_true', help='Generate CEO briefing')
    parser.add_argument('--ralph-task', type=str, help='Run Ralph Wiggum loop with task')
    parser.add_argument('--audit', action='store_true', help='Show audit summary')
    parser.add_argument('--recovery', action='store_true', help='Show recovery status')
    
    args = parser.parse_args()
    
    gold = GoldTierComplete()
    
    if args.status:
        gold.print_status()
    
    if args.ceo_briefing:
        print("\nGenerating Weekly CEO Briefing...")
        path = gold.run_ceo_briefing()
        print(f"Briefing generated: {path}")
    
    if args.ralph_task:
        print(f"\nRunning Ralph Wiggum Loop: {args.ralph_task}")
        result = gold.run_ralph_loop(args.ralph_task)
        print(f"Result: {result}")
    
    if args.audit:
        print("\nAudit Summary:")
        summary = gold.get_audit_summary()
        print(f"Total Entries: {summary.get('total_entries', 0)}")
    
    if args.recovery:
        print("\nRecovery Status:")
        status = gold.get_recovery_status()
        print(status)
    
    if not any([args.status, args.ceo_briefing, args.ralph_task, args.audit, args.recovery]):
        gold.print_status()
        print("\nUsage:")
        print("  python gold_tier_complete.py --status")
        print("  python gold_tier_complete.py --ceo-briefing")
        print("  python gold_tier_complete.py --ralph-task \"Your task here\"")
        print("  python gold_tier_complete.py --audit")
        print("  python gold_tier_complete.py --recovery")


if __name__ == "__main__":
    main()
