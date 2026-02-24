# Skill: Audit Logging

**Skill ID:** `audit_logging`  
**Version:** 1.0  
**Tier:** Gold  
**Status:** ✅ Operational

---

## Overview

Comprehensive audit logging for all system actions. Every action is logged to `/Logs/YYYY-MM-DD.json` with:
- Timestamp
- Action
- Actor (system/user/service)
- Result (success/failure/pending)
- Details and metadata

---

## Log Entry Format

```json
{
  "timestamp": "2026-02-24T16:30:00.000000",
  "action": "email_sent",
  "actor": "system",
  "result": "success",
  "details": {
    "to": "user@example.com",
    "subject": "Test Email"
  },
  "metadata": {}
}
```

---

## Usage

### Basic Logging

```python
from audit_logger import audit_logger

# Log success
audit_logger.log_success(
    action='email_sent',
    actor='email_mcp',
    details={'to': 'user@example.com'}
)

# Log failure
audit_logger.log_failure(
    action='api_error',
    actor='odoo_mcp',
    error='Connection timeout'
)

# Log pending
audit_logger.log_pending(
    action='approval_waiting',
    details={'item': 'INV-001'}
)
```

### Decorator

```python
from audit_logger import audit_log

@audit_log(action_name='invoice_created', actor='odoo_mcp')
def create_invoice(data):
    # Your code here
    pass
```

### Query Logs

```python
# Query today's logs
entries = audit_logger.query(limit=100)

# Query by action
email_logs = audit_logger.query(action='email_sent')

# Get daily summary
summary = audit_logger.get_summary()
```

### Export Logs

```python
# Export date range to JSON
export_path = audit_logger.export(
    start_date='2026-02-01',
    end_date='2026-02-24',
    format='json'
)
```

---

## Log File Structure

```
Logs/
├── 2026-02-24.json       # Today's logs
├── 2026-02-23.json       # Yesterday's logs
├── audit_export_*.json   # Exported logs
└── audit_export_*.csv    # CSV exports
```

---

## Query Examples

```python
# Get all failed actions
failures = audit_logger.query(result='failure', limit=50)

# Get all email actions
emails = audit_logger.query(action='email_sent')

# Get actions by specific actor
odoo_actions = audit_logger.query(actor='odoo_mcp')
```

---

**Documentation:** `/Skills/audit_logging.md`  
**Module:** `audit_logger.py`
