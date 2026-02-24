# Skill: Error Recovery with Exponential Backoff

**Skill ID:** `error_recovery`  
**Version:** 1.0  
**Tier:** Gold  
**Status:** ✅ Operational

---

## Overview

Provides resilient error recovery patterns for all watchers and MCP servers:
- Exponential backoff retry logic
- Circuit breaker pattern
- Offline queue for API failures
- Graceful degradation

---

## Features

### 1. Retry with Exponential Backoff

```python
from error_recovery import retry_with_backoff

@retry_with_backoff(max_retries=5, base_delay=1.0)
def api_call():
    # Your API call here
    pass
```

### 2. Circuit Breaker

```python
from error_recovery import circuit_breakers

# Check status
status = circuit_breakers['odoo'].get_status()
# {'state': 'CLOSED', 'failures': 0, ...}
```

### 3. Offline Queue

```python
from error_recovery import offline_queues

# Queue operation for later
queue_id = offline_queues['email'].enqueue(operation)
```

### 4. Resilient API Calls

```python
from error_recovery import resilient_api_call

result = resilient_api_call(
    'odoo',
    create_invoice,
    invoice_data,
    queue_if_offline=True
)
```

---

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| MAX_RETRIES | 5 | Maximum retry attempts |
| BASE_DELAY | 1.0s | Initial delay |
| MAX_DELAY | 60.0s | Maximum delay |
| EXPONENTIAL_BASE | 2 | Backoff multiplier |

---

## Usage Examples

### Watcher with Retry

```python
from error_recovery import retry_with_backoff

@retry_with_backoff(max_retries=3)
def check_gmail():
    # Gmail API call
    pass
```

### MCP Server with Circuit Breaker

```python
from error_recovery import resilient_api_call

def create_invoice(invoice_data):
    return resilient_api_call(
        'odoo',
        _create_invoice_internal,
        invoice_data
    )
```

---

**Documentation:** `/Skills/error_recovery.md`  
**Module:** `error_recovery.py`
