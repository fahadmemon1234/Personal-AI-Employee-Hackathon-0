"""
Audit Logging Module

Logs every action to /Logs/YYYY-MM-DD.json with:
- timestamp
- action
- actor (system/user/service)
- result
- metadata

Compliant with audit trail requirements.
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
import threading
import os

# Configuration
LOGS_DIR = Path("Logs")
LOGS_DIR.mkdir(exist_ok=True)

# Setup logging
logger = logging.getLogger('audit_log')


class AuditLogger:
    """
    Audit Logger - Records all system actions
    
    Log Entry Format:
    {
        "timestamp": "2026-02-24T16:30:00.000000",
        "action": "email_sent",
        "actor": "system" | "user" | "service",
        "result": "success" | "failure" | "pending",
        "details": {...},
        "metadata": {...}
    }
    """
    
    def __init__(self, logs_dir: Path = LOGS_DIR):
        self.logs_dir = logs_dir
        self._lock = threading.Lock()
        self._current_file = None
        self._current_date = None
        self._buffer = []
        self._buffer_size = 0
        self._max_buffer = 10  # Flush after 10 entries
    
    def _get_log_file(self) -> Path:
        """Get today's log file path"""
        today = datetime.now().strftime('%Y-%m-%d')
        return self.logs_dir / f"{today}.json"
    
    def _ensure_file(self):
        """Ensure log file exists and is properly initialized"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        # If date changed, flush and close old file
        if self._current_date != today:
            self._flush_buffer()
            self._current_date = today
        
        self._current_file = self._get_log_file()
        
        # Initialize file if new
        if not self._current_file.exists():
            self._init_log_file()
    
    def _init_log_file(self):
        """Initialize new log file with header"""
        log_data = {
            'version': '1.0',
            'created_at': datetime.now().isoformat(),
            'entries': []
        }
        
        with open(self._current_file, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)
    
    def _flush_buffer(self):
        """Flush buffered entries to disk"""
        if not self._buffer:
            return
        
        with self._lock:
            self._ensure_file()
            
            try:
                # Read existing log
                with open(self._current_file, 'r', encoding='utf-8') as f:
                    log_data = json.load(f)
                
                # Add buffered entries
                log_data['entries'].extend(self._buffer)
                log_data['updated_at'] = datetime.now().isoformat()
                log_data['entry_count'] = len(log_data['entries'])
                
                # Write back
                with open(self._current_file, 'w', encoding='utf-8') as f:
                    json.dump(log_data, f, indent=2, ensure_ascii=False)
                
                self._buffer = []
                self._buffer_size = 0
                
            except Exception as e:
                logger.error(f"Failed to flush audit log: {e}")
    
    def log(
        self,
        action: str,
        actor: str = 'system',
        result: str = 'success',
        details: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        flush: bool = False
    ):
        """
        Log an action
        
        Args:
            action: Action name (e.g., 'email_sent', 'invoice_created')
            actor: Who performed the action (system, user, service name)
            result: Outcome (success, failure, pending)
            details: Action-specific details
            metadata: Additional metadata (IP, session, etc.)
            flush: Immediately flush to disk
        
        Usage:
            audit.log(
                action='email_sent',
                actor='email_mcp',
                result='success',
                details={'to': 'user@example.com', 'subject': 'Test'}
            )
        """
        entry = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'actor': actor,
            'result': result,
            'details': details or {},
            'metadata': metadata or {}
        }
        
        with self._lock:
            self._buffer.append(entry)
            self._buffer_size += 1
            
            # Auto-flush if buffer full
            if self._buffer_size >= self._max_buffer or flush:
                self._flush_buffer()
    
    def log_success(
        self,
        action: str,
        actor: str = 'system',
        details: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """Log successful action"""
        self.log(action=action, actor=actor, result='success', details=details, **kwargs)
    
    def log_failure(
        self,
        action: str,
        actor: str = 'system',
        error: str = None,
        details: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """Log failed action"""
        detail_dict = details or {}
        if error:
            detail_dict['error'] = error
        
        self.log(action=action, actor=actor, result='failure', details=detail_dict, **kwargs)
    
    def log_pending(
        self,
        action: str,
        actor: str = 'system',
        details: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """Log pending action"""
        self.log(action=action, actor=actor, result='pending', details=details, **kwargs)
    
    def query(
        self,
        date: str = None,
        action: str = None,
        actor: str = None,
        result: str = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Query audit logs
        
        Args:
            date: Date in YYYY-MM-DD format (default: today)
            action: Filter by action name
            actor: Filter by actor
            result: Filter by result (success, failure, pending)
            limit: Maximum entries to return
        
        Returns:
            List of matching log entries
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        log_file = self.logs_dir / f"{date}.json"
        
        if not log_file.exists():
            return []
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                log_data = json.load(f)
            
            entries = log_data.get('entries', [])
            
            # Apply filters
            filtered = []
            for entry in entries:
                if action and entry.get('action') != action:
                    continue
                if actor and entry.get('actor') != actor:
                    continue
                if result and entry.get('result') != result:
                    continue
                filtered.append(entry)
                
                if len(filtered) >= limit:
                    break
            
            return filtered
        
        except Exception as e:
            logger.error(f"Failed to query audit log: {e}")
            return []
    
    def get_summary(self, date: str = None) -> Dict[str, Any]:
        """Get summary of audit logs for a date"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        entries = self.query(date=date, limit=10000)
        
        summary = {
            'date': date,
            'total_entries': len(entries),
            'by_result': {},
            'by_actor': {},
            'by_action': {},
            'recent_entries': entries[-10:] if entries else []
        }
        
        # Count by result
        for entry in entries:
            result = entry.get('result', 'unknown')
            summary['by_result'][result] = summary['by_result'].get(result, 0) + 1
            
            actor = entry.get('actor', 'unknown')
            summary['by_actor'][actor] = summary['by_actor'].get(actor, 0) + 1
            
            action = entry.get('action', 'unknown')
            summary['by_action'][action] = summary['by_action'].get(action, 0) + 1
        
        return summary
    
    def export(self, start_date: str, end_date: str, format: str = 'json') -> str:
        """
        Export audit logs for date range
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            format: Export format (json, csv)
        
        Returns:
            Path to exported file
        """
        from datetime import timedelta
        
        all_entries = []
        current = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        while current <= end:
            date_str = current.strftime('%Y-%m-%d')
            entries = self.query(date=date_str, limit=10000)
            all_entries.extend(entries)
            current += timedelta(days=1)
        
        # Sort by timestamp
        all_entries.sort(key=lambda x: x.get('timestamp', ''))
        
        # Export
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if format == 'json':
            export_file = self.logs_dir / f"audit_export_{timestamp}.json"
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'exported_at': datetime.now().isoformat(),
                    'start_date': start_date,
                    'end_date': end_date,
                    'entry_count': len(all_entries),
                    'entries': all_entries
                }, f, indent=2, ensure_ascii=False)
        
        elif format == 'csv':
            import csv
            export_file = self.logs_dir / f"audit_export_{timestamp}.csv"
            
            if all_entries:
                with open(export_file, 'w', newline='', encoding='utf-8') as f:
                    fieldnames = ['timestamp', 'action', 'actor', 'result', 'details', 'metadata']
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    
                    for entry in all_entries:
                        row = {
                            'timestamp': entry.get('timestamp', ''),
                            'action': entry.get('action', ''),
                            'actor': entry.get('actor', ''),
                            'result': entry.get('result', ''),
                            'details': json.dumps(entry.get('details', {})),
                            'metadata': json.dumps(entry.get('metadata', {}))
                        }
                        writer.writerow(row)
        
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        return str(export_file)
    
    def __del__(self):
        """Flush buffer on destruction"""
        try:
            self._flush_buffer()
        except:
            pass


# Global audit logger instance
audit_logger = AuditLogger()


# Convenience functions
def log_action(action: str, actor: str = 'system', result: str = 'success', **kwargs):
    """Log an action using global logger"""
    audit_logger.log(action=action, actor=actor, result=result, **kwargs)

def log_success(action: str, actor: str = 'system', **kwargs):
    """Log success using global logger"""
    audit_logger.log_success(action=action, actor=actor, **kwargs)

def log_failure(action: str, actor: str = 'system', error: str = None, **kwargs):
    """Log failure using global logger"""
    audit_logger.log_failure(action=action, actor=actor, error=error, **kwargs)

def query_logs(**kwargs):
    """Query logs using global logger"""
    return audit_logger.query(**kwargs)

def get_daily_summary(date: str = None):
    """Get daily summary using global logger"""
    return audit_logger.get_summary(date=date)


# Decorator for automatic audit logging
def audit_log(action_name: str = None, actor: str = 'system'):
    """
    Decorator for automatic audit logging
    
    Usage:
        @audit_log(action_name='email_sent', actor='email_mcp')
        def send_email(to, subject, body):
            # Your code here
            return {'success': True}
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            action = action_name or func.__name__
            
            try:
                result = func(*args, **kwargs)
                
                # Log success
                log_success(
                    action=action,
                    actor=actor,
                    details={'function': func.__name__, 'args': args, 'kwargs': kwargs}
                )
                
                return result
            
            except Exception as e:
                # Log failure
                log_failure(
                    action=action,
                    actor=actor,
                    error=str(e),
                    details={'function': func.__name__}
                )
                raise
        
        return wrapper
    return decorator


# Example usage and test
if __name__ == "__main__":
    print("Audit Logging Module - Test")
    print("="*60)
    
    # Test logging
    print("\nLogging test entries...")
    
    audit_logger.log_success(
        action='email_sent',
        actor='email_mcp',
        details={'to': 'user@example.com', 'subject': 'Test Email'}
    )
    
    audit_logger.log_success(
        action='invoice_created',
        actor='odoo_mcp',
        details={'invoice_id': 'INV-001', 'amount': 50000}
    )
    
    audit_logger.log_failure(
        action='api_call_failed',
        actor='social_mcp',
        error='Connection timeout',
        details={'endpoint': '/post'}
    )
    
    audit_logger.log_pending(
        action='approval_waiting',
        actor='system',
        details={'item': 'SOCIAL_POST_001'}
    )
    
    # Flush to ensure written
    audit_logger._flush_buffer()
    
    print(f"Log file: {audit_logger._current_file}")
    
    # Test query
    print("\nQuerying today's logs...")
    entries = audit_logger.query(limit=10)
    print(f"Found {len(entries)} entries")
    
    for entry in entries[-3:]:
        print(f"  - {entry['timestamp']}: {entry['action']} ({entry['result']})")
    
    # Test summary
    print("\nDaily Summary:")
    summary = audit_logger.get_summary()
    print(f"  Total Entries: {summary['total_entries']}")
    print(f"  By Result: {summary['by_result']}")
    print(f"  By Actor: {summary['by_actor']}")
    
    print("\n" + "="*60)
    print("Audit Logging Module - Test Complete")
    print(f"Log file created: {audit_logger._current_file}")
