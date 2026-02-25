# Skill: Health Monitor (Cloud Agent)

**Domain:** Infrastructure
**Agent Type:** Cloud
**Capability:** Health monitoring and alerting
**Execution:** Cloud Agent (24/7)

---

## Overview

This skill enables the Cloud Agent to:
1. Run Flask health monitoring endpoint
2. Monitor system services (MCP servers, Odoo, PostgreSQL)
3. Check disk space, memory, and system health
4. Send email alerts when services are down
5. Provide health status API for external monitoring

**CRITICAL:** Health monitor runs 24/7 on Cloud VM for uptime monitoring.

---

## Usage

### Start Health Monitor

```bash
# Start health monitor (Flask app on port 5000)
python health_monitor.py

# Start with custom port
python health_monitor.py --port 5001

# Start in background (production)
nohup python health_monitor.py --port 5000 &
```

### Health Endpoints

```bash
# Full health status
curl http://localhost:5000/health

# Simplified summary
curl http://localhost:5000/health/summary

# Force immediate health check (POST)
curl -X POST http://localhost:5000/health/check

# Root endpoint (info)
curl http://localhost:5000/
```

### Example Response

```json
{
  "status": "healthy",
  "uptime": "2:34:56.789012",
  "last_check": "2026-02-25T10:30:00",
  "services": {
    "cloud_orchestrator": {"healthy": true},
    "email_mcp": {"healthy": true},
    "social_mcp": {"healthy": true},
    "odoo_mcp": {"healthy": true},
    "odoo": {"healthy": true},
    "postgres": {"healthy": true},
    "nginx": {"healthy": true},
    "disk_space": {"healthy": true},
    "memory": {"healthy": true},
    "git_sync": {"healthy": true}
  },
  "version": "1.0.0"
}
```

---

## Configuration

### Environment Variables

```bash
# .env.cloud

# Email alert configuration
GMAIL_SMTP_SERVER=smtp.gmail.com
GMAIL_SMTP_PORT=587
GMAIL_SENDER_EMAIL=cloud_agent@example.com
GMAIL_APP_PASSWORD=your_app_password
ALERT_EMAIL=admin@example.com

# Vault path
VAULT_PATH=/opt/platinum-vault

# Health monitor settings
HEALTH_MONITOR_PORT=5000
ALERT_COOLDOWN_MINUTES=15
```

### Supervisor Configuration

```ini
# /etc/supervisor/conf.d/health_monitor.conf

[program:health_monitor]
command=/usr/bin/python3 /opt/platinum-vault/health_monitor.py
directory=/opt/platinum-vault
user=platinum
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/health_monitor.log
environment=PATH="/usr/bin:/bin"
```

---

## Health Checks

### Service Monitoring

The health monitor checks:

| Service | Port | Check Method |
|---------|------|--------------|
| Cloud Orchestrator | - | Process running |
| Email MCP | 8080 | Port listening |
| Social MCP | 8083 | Port listening |
| X MCP | 8084 | Port listening |
| Odoo MCP | 8082 | Port listening |
| Odoo | 8069 | Port listening |
| PostgreSQL | 5432 | Port listening |
| Nginx | 80 | Port listening |

### System Checks

| Check | Threshold | Alert If |
|-------|-----------|----------|
| Disk Space | < 90% used | > 90% used |
| Memory | < 90% used | > 90% used |
| Git Sync | < 15 min old | > 15 min old |

---

## Alert Configuration

### Email Alerts

```python
# Alert is sent when:
# 1. Any service is unhealthy
# 2. No alert sent in last ALERT_COOLDOWN_MINUTES (default: 15)

# Example alert email
Subject: [ALERT] Cloud Agent Unhealthy - 2 services down

Health Alert - Cloud Agent

Timestamp: 2026-02-25T10:30:00

Failed Services:
  - email_mcp
  - odoo

Details:
Failed services: email_mcp, odoo

---
Cloud Agent Health Monitor
Platinum Tier
```

### Alert Cooldown

```python
# Prevents alert spam
ALERT_COOLDOWN_MINUTES = 15

# After sending an alert, wait 15 minutes before sending another
# unless the status changes (healthy → unhealthy → healthy → unhealthy)
```

---

## Integration with Monitoring Services

### Uptime Robot

```
# Configure Uptime Robot to ping health endpoint
URL: http://your-cloud-vm-ip:5000/health/summary
Monitor Type: HTTP(S)
Port: 5000
Request Type: GET
```

### Custom Monitoring Script

```python
#!/usr/bin/env python3
"""External monitoring script for Cloud Agent health."""

import requests
import sys
from datetime import datetime

def check_cloud_health(cloud_url: str) -> bool:
    """Check Cloud Agent health."""
    try:
        response = requests.get(f'{cloud_url}/health/summary', timeout=10)
        data = response.json()
        
        if data.get('status') == 'healthy':
            print(f"✓ Cloud Agent healthy at {datetime.now()}")
            return True
        else:
            failed = data.get('failed_services', [])
            print(f"✗ Cloud Agent unhealthy: {failed}")
            return False
            
    except Exception as e:
        print(f"✗ Cannot reach Cloud Agent: {e}")
        return False

if __name__ == '__main__':
    cloud_url = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:5000'
    healthy = check_cloud_health(cloud_url)
    sys.exit(0 if healthy else 1)
```

---

## Security Rules

**Health Monitor:**
- ✅ Bind to 0.0.0.0 for external access (with firewall)
- ✅ Use HTTPS in production (with Nginx reverse proxy)
- ✅ Rate limit health check requests
- ✅ Log all health check requests
- ❌ NEVER expose sensitive data in health response
- ❌ NEVER allow unauthenticated write operations

---

## Troubleshooting

### Health Monitor Won't Start

```bash
# Check if port is in use
sudo ss -tlnp | grep 5000

# Check logs
tail -f /var/log/health_monitor.log

# Check Flask installation
pip3 list | grep Flask

# Install if needed
pip3 install flask python-dotenv
```

### Alerts Not Sending

```bash
# Check email configuration
cat .env.cloud | grep GMAIL

# Test SMTP connection
python3 -c "
import smtplib
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login('your_email@gmail.com', 'your_password')
print('SMTP OK')
"

# Check alert cooldown
# Wait ALERT_COOLDOWN_MINUTES or restart health monitor
```

---

## Related Skills

- [[sync_vault_skill]] - Git-based vault synchronization
- [[email_draft_skill]] - Cloud Agent skill for email drafts
- [[approval_handler]] - Local Agent skill for handling approvals

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-25 | Initial implementation |
