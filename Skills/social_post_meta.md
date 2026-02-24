# Agent Skill: Social Media Meta Integration

## Skill ID: `social_post_meta`

**Purpose:** Generate and post social media content to Facebook/Instagram with approval workflow.

## MCP Server

- **Port:** 8083
- **URL:** http://localhost:8083

## Available Tools

| Tool | Endpoint | Method |
|------|----------|--------|
| Post to Facebook | `/tools/post_to_facebook` | POST |
| Post to Instagram | `/tools/post_to_instagram` | POST |
| Generate Summary | `/tools/generate_summary` | GET |
| List Posts | `/tools/list_posts` | GET |

## Usage

```bash
# Start server
python mcp_social_server.py

# Test (dry-run)
python test_social_mcp.py --dry-run

# Post approved content
python post_approved.py
```

## Configuration (.env)

```env
FACEBOOK_PAGE_ID=110326951910826
FACEBOOK_ACCESS_TOKEN=your_token
INSTAGRAM_ACCOUNT_ID=17841457182813798
INSTAGRAM_ACCESS_TOKEN=your_token
SOCIAL_DRY_RUN=false
```

## Workflow

```
/Needs_Action/post_request.md
    ↓
[Generate post content]
    ↓
/Pending_Approval/SOCIAL_POST_*.md
    ↓ (human approval)
[Post to Facebook/Instagram]
    ↓
/Completed/
    ↓
[Briefings/meta_summary.md]
```

---

*For full documentation, see the original skill implementation*
