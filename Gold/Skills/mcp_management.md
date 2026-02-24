# MCP Management Documentation

## Overview

This document describes how to manage and use the 5 MCP (Model Context Protocol) servers configured for this project.

## Servers Configuration

### Server List

| Server | Port | Description |
|--------|------|-------------|
| `email-mcp` | 8080 | Email management with approval workflow |
| `browser-mcp` | 8081 | Web browsing and automation |
| `odoo-mcp` | 8082 | Odoo ERP integration |
| `social-mcp` | 8083 | Facebook & Instagram posting |
| `x-mcp` | 8084 | Twitter/X posting |

### Configuration File Location

- **Claude Code Config**: `~/.config/claude-code/mcp.json`
- **Project Config**: `./claude-mcp-config.json`

## Starting Servers

### Option 1: Start All Servers at Once

```bash
python start_all_mcp_servers.py
```

This starts all 5 servers in separate threads.

### Option 2: Start Individual Servers

```bash
# Email Server
python mcp_email_server.py

# Browser Server
python mcp_browser_server.py

# Odoo Server
python mcp_odoo_server.py

# Social Media Server (Meta)
python mcp_social_server.py

# X (Twitter) Server
python mcp_x_server.py
```

### Option 3: Via Claude Code

Claude Code will automatically start servers based on the `mcp.json` configuration when needed.

## Health Check Endpoints

Each server provides a `/health` endpoint:

```bash
# Email
curl http://localhost:8080/health

# Browser
curl http://localhost:8081/health

# Odoo
curl http://localhost:8082/health

# Social (Meta)
curl http://localhost:8083/health

# X (Twitter)
curl http://localhost:8084/health
```

## Testing All Servers

### Quick Test Commands

```python
import requests

# Test Email MCP
print("Email:", requests.get('http://localhost:8080/health').json())

# Test Browser MCP
print("Browser:", requests.get('http://localhost:8081/health').json())

# Test Odoo MCP
print("Odoo:", requests.get('http://localhost:8082/health').json())

# Test Social MCP
print("Social:", requests.get('http://localhost:8083/health').json())

# Test X MCP
print("X:", requests.get('http://localhost:8084/health').json())
```

### Comprehensive Test

```bash
python test_all.py
```

## Server Capabilities

### Email MCP (Port 8080)

- `send-email` - Send emails with approval workflow
- `receive-email` - Receive and process emails
- `process-email` - Process incoming emails
- `gmail-watch` - Watch Gmail for new messages
- `email-approval` - Manage email approval workflow

**Example Request:**
```bash
curl -X POST http://localhost:8080/tools/send_email \
  -H "Content-Type: application/json" \
  -d '{"to": "user@example.com", "subject": "Test", "body": "Hello"}'
```

### Browser MCP (Port 8081)

- `browse-web` - Browse web pages
- `scrape-content` - Scrape web content
- `automate-browser` - Browser automation tasks
- `web-interaction` - Interact with web elements

**Example Request:**
```bash
curl -X POST http://localhost:8081/tools/browse \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

### Odoo MCP (Port 8082)

- `search-partners` - Search Odoo partners
- `get-invoices` - Get invoices
- `create-invoice` - Create new invoices
- `get-account-balances` - Get account balances
- `odoo-query` - General Odoo queries

**Example Request:**
```bash
curl -X POST http://localhost:8082/tools/search_partners \
  -H "Content-Type: application/json" \
  -d '{"query": "partner name"}'
```

### Social MCP (Port 8083)

- `post-facebook` - Post to Facebook
- `post-instagram` - Post to Instagram
- `get-social-summary` - Get social media summary
- `social-analytics` - Social media analytics

**Example Request:**
```bash
curl -X POST http://localhost:8083/tools/create_post \
  -H "Content-Type: application/json" \
  -d '{"platform": "instagram", "message": "Hello World!"}'
```

### X MCP (Port 8084)

- `post-tweet` - Post tweets to X (Twitter)
- `get-recent-posts` - Get recent tweets
- `generate-x-summary` - Generate X activity summary

**Example Request:**
```bash
curl -X POST http://localhost:8084/tools/post_tweet \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello from MCP!"}'
```

## Environment Variables

All servers use environment variables from `.env` file:

### Email MCP
- Gmail credentials (`credentials.json`, `token.pickle`)

### Browser MCP
- Browser type (Chrome/Firefox)
- Headless mode setting

### Odoo MCP
- `ODOO_URL` - Odoo instance URL
- `ODOO_DB` - Database name
- `ODOO_USERNAME` - Username
- `ODOO_PASSWORD` - Password/API key

### Social MCP (Meta)
- `FACEBOOK_PAGE_ID` - Facebook page ID
- `FACEBOOK_ACCESS_TOKEN` - Facebook access token
- `INSTAGRAM_ACCOUNT_ID` - Instagram account ID
- `INSTAGRAM_ACCESS_TOKEN` - Instagram access token

### X MCP (Twitter)
- `X_API_KEY` - Twitter API key
- `X_API_SECRET` - Twitter API secret
- `X_ACCESS_TOKEN` - Access token
- `X_ACCESS_TOKEN_SECRET` - Access token secret
- `X_BEARER_TOKEN` - Bearer token

## Workflow Integration

### Email Approval Workflow

1. Email received → `Inbox/`
2. Categorized → `Needs_Action/`
3. Pending approval → `Pending_Approval/`
4. Approved → `Approved/`
5. Completed → `Completed/`

### Social Media Posting

1. Content created
2. Approval (if required)
3. Posted to platform
4. Logged in `Posts_Log.json` or `Posts_Log_X.json`

## Troubleshooting

### Server Won't Start

1. Check if port is already in use:
   ```bash
   netstat -ano | findstr :8080
   ```

2. Kill existing process:
   ```bash
   taskkill /F /PID <PID>
   ```

3. Check Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### API Connection Issues

1. Verify `.env` file has correct credentials
2. Check API endpoints are accessible
3. Review server logs for errors

### Authentication Errors

1. Re-authenticate with the service
2. Refresh tokens
3. Check credential files exist

## Best Practices

1. **Start servers before heavy usage** - Reduces initial latency
2. **Monitor server health** - Check `/health` endpoints regularly
3. **Review logs** - Check server output for issues
4. **Keep credentials secure** - Never commit `.env` to git
5. **Use dry-run mode** - Test without real actions first

## File Structure

```
Gold/
├── mcp_email_server.py      # Email MCP server
├── mcp_browser_server.py    # Browser MCP server
├── mcp_odoo_server.py       # Odoo MCP server
├── mcp_social_server.py     # Social Media MCP server
├── mcp_x_server.py          # X (Twitter) MCP server
├── start_all_mcp_servers.py # Start all servers script
├── claude-mcp-config.json   # Claude Code configuration
├── .env                     # Environment variables (credentials)
└── Skills/
    └── mcp_management.md    # This documentation
```

## Quick Reference

### Start All Servers
```bash
python start_all_mcp_servers.py
```

### Check All Health Endpoints
```bash
python -c "import requests; [print(f'{p}:', requests.get(f'http://localhost:{p}/health').json()) for p in [8080,8081,8082,8083,8084]]"
```

### Stop All Python Servers
```bash
taskkill /F /IM python.exe
```

---

**Last Updated:** 2026-02-24
**Version:** 1.0
**Status:** All 5 servers operational ✅
