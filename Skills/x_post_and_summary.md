# Agent Skill: X (Twitter) Post and Summary

## Skill ID: `x_post_and_summary`

**Version:** 1.0  
**Created:** 2026-02-24  
**Author:** AI Digital FTE  
**Dependencies:** MCP X Server (`mcp_x_server.py`)

---

## Purpose

Automate X (Twitter) posting with Human-in-the-Loop (HITL) approval workflow. Generate tweets from business updates, require approval before posting, and generate weekly summaries with engagement metrics.

**Compliance:** Follows X Terms of Service - no spam, no automated mass posting.

---

## Trigger Conditions

- Business update available for sharing
- Scheduled posting time (daily/weekly)
- Milestone or announcement
- Manual invocation: `python reasoning_loop.py --skill=x_post_and_summary`

---

## Input

- `/Needs_Action/` files containing post requests
- `Business_Goals.md` for brand voice
- Email/WhatsApp messages with keywords: "tweet", "X post", "announce"
- Scheduled events (product launches, promotions)

---

## Output

- Draft tweets in `/Plans/` requiring approval
- Posted tweets on X (after approval)
- Weekly summary in `/Briefings/x_weekly.md`
- Audit log in `/Audit_Log.md`

---

## MCP Server Configuration

### Environment Variables

Create/update `.env` file:

```bash
# X (Twitter) Settings
X_API_KEY=your_api_key_here
X_API_SECRET=your_api_secret_here
X_ACCESS_TOKEN=your_access_token_here
X_ACCESS_TOKEN_SECRET=your_access_token_secret_here
X_BEARER_TOKEN=your_bearer_token_here
X_USERNAME=your_username

# Posting Mode
X_USE_BROWSER=false
X_DRY_RUN=true  # Keep true for testing
```

### Get X API Credentials

1. Visit: https://developer.twitter.com/en/portal/dashboard
2. Create a Project & App
3. Generate API Key & Secret
4. Generate Access Token & Secret
5. Copy Bearer Token

### Start MCP X Server

```bash
python mcp_x_server.py
```

Server runs on: `http://localhost:8084`

---

## Available Tools (MCP Endpoints)

| Tool | Method | Endpoint | Description | Approval Required |
|------|--------|----------|-------------|-------------------|
| `post_tweet` | POST | `/tools/post_tweet` | Post a tweet (280 chars) | **Yes** |
| `get_recent_posts` | GET | `/tools/get_recent_posts` | Get recent tweets | No |
| `generate_x_summary` | GET | `/tools/generate_x_summary` | Generate weekly summary | No |
| `health` | GET | `/health` | Health check | No |

---

## Procedure

### Step 1: Detect Post Request

Scan `/Needs_Action/` for files containing:

**Keywords:**
- "tweet", "X post", "twitter", "announce"
- "share", "post update", "public announcement"

**Classification:**
```python
X_KEYWORDS = ['tweet', 'x post', 'twitter', 'announce', 'share update']
```

### Step 2: Read Business Goals

Load `Business_Goals.md` (if exists) to understand:

- Brand voice (professional, friendly, technical)
- Target audience
- Key messaging points
- Hashtags to use
- Posting frequency

### Step 3: Generate Tweet Content

Create engaging tweet based on:

1. **Request content** (what to post)
2. **Business goals** (brand voice)
3. **X best practices** (280 char limit, hashtags)

**Tweet Template:**
```
🎉 [Headline]

[Main content - concise, 280 chars max]

✅ [Key point 1]
✅ [Key point 2]

#Hashtag1 #Hashtag2 #Hashtag3
```

**Character Count:** Must be ≤ 280 characters

### Step 4: Create Draft Plan

Create `/Plans/Plan_X_[timestamp].md`:

```markdown
# X (Twitter) Post Plan

**Generated:** 2026-02-24 10:00:00  
**Source:** email_Announcement_20260224.md  
**Priority:** Normal

---

## Tweet Content

```
🎉 Exciting News!

We're launching AI-driven web development services!

✅ 50% faster delivery
✅ Higher quality code

#AI #WebDev #Pakistan
```

**Character Count:** 156/280

---

## Required Approvals

| Action | Type | Status |
|--------|------|--------|
| Review content | Content | Pending |
| Approve for posting | Publishing | Pending |

---

## MCP Calls Required

1. `mcp_x_server` - POST /tools/post_tweet

---

## Approval Instructions

1. Review tweet content
2. Check character count (≤280)
3. Verify hashtags
4. If correct, move to `/Approved/`
5. System will post to X

---

*Created by x_post_and_summary skill*
```

### Step 5: Wait for Approval

- File stays in `/Pending_Approval/` until human reviews
- Human moves to `/Approved/` to authorize posting
- System posts to X

### Step 6: Post Tweet (After Approval)

```python
# Post to X
response = requests.post('http://localhost:8084/tools/post_tweet', json={
    "text": tweet_content,
    "dry_run": False  # Real posting
})

result = response.json()
```

### Step 7: Generate Weekly Summary

```python
# Generate summary
response = requests.get('http://localhost:8084/tools/generate_x_summary')
summary = response.json()

# Save to Briefings/x_weekly.md
```

---

## Company Handbook Compliance

| Rule | Implementation |
|------|----------------|
| **Efficiency First** | Auto-generate tweets, manual approval only |
| **Data Integrity** | All posts logged in Posts_Log_X.json |
| **Security** | API tokens via environment variables |
| **Transparency** | Draft posts in `/Plans/` for review |
| **Proactivity** | Suggest tweets based on business events |
| **Polite Tone** | All posts maintain professional brand voice |
| **Approval Required** | No posting without human approval |
| **X Terms Compliance** | No spam, limited posting frequency |

---

## X Terms of Service Compliance

### ✅ DO:

- Post valuable, original content
- Engage authentically with followers
- Use relevant hashtags (3-5 max)
- Post 3-5 times per day maximum
- Include media when relevant

### ❌ DON'T:

- Spam or post duplicate content
- Use misleading hashtags
- Post more than 5 times per day
- Automate follows/unfollows
- Post sensitive or private information

---

## Error Handling

| Error | Action |
|-------|--------|
| API token missing | Log error, use dry-run mode, notify admin |
| Tweet too long | Truncate to 280 chars, flag for review |
| Post failed | Log error, keep in `/Pending_Approval/`, retry option |
| Rate limit exceeded | Queue for later, notify admin |

---

## Usage Examples

### Example 1: Post Business Update

**Input:** `/Needs_Action/email_New_Service_Launch.md`

```
Subject: New AI Service Launch

Please tweet about our new AI-driven web development service.

Key points:
- 50% faster delivery
- Better code quality
- Competitive pricing
```

**Skill Execution:**
```bash
python reasoning_loop.py --skill=x_post_and_summary
```

**Output:**
- Draft plan: `/Plans/Plan_X_20260224_100000.md`
- Approval file: `/Pending_Approval/X_POST_001.md`

### Example 2: Generate Weekly Summary

**Input:** Manual request or scheduled

**Skill Execution:**
```bash
curl http://localhost:8084/tools/generate_x_summary
```

**Output:**
- Summary saved to: `/Briefings/x_weekly.md`

---

## Integration with Approval Workflow

### File Movement Pattern

```
/Needs_Action/post_request.md
       ↓ (detected by skill)
[Generate tweet content]
       ↓
/Pending_Approval/X_POST_*.md
       ↓ (human moves to Approved)
[Post to X]
       ↓
/Completed/X_POST_*.md
```

### Approval File States

| Location | State | Action |
|----------|-------|--------|
| `/Pending_Approval/` | Awaiting Review | Human must review content |
| `/Approved/` | Approved | System will post |
| `/Completed/` | Executed | Posted successfully |
| `/Rejected/` | Rejected | Post cancelled, reason logged |

---

## Testing

### Test Without Real Posting (Dry Run)

```bash
# Ensure dry_run is true in .env
X_DRY_RUN=true

# Run skill
python reasoning_loop.py --skill=x_post_and_summary

# Or direct API test
curl -X POST http://localhost:8084/tools/post_tweet \
  -H "Content-Type: application/json" \
  -d '{"text":"Test tweet","dry_run":true}'
```

### Test With Real Posting

```bash
# 1. Set dry_run to false
X_DRY_RUN=false

# 2. Configure API tokens in .env

# 3. Create post request
echo "Tweet: Test announcement" > Needs_Action/test_tweet.md

# 4. Run skill
python reasoning_loop.py --skill=x_post_and_summary
```

---

## Audit Trail

All actions logged in `Audit_Log.md`:

```markdown
## 2026-02-24 10:30:00 - X Posting Skill

- **Action:** Tweet Created
- **Content:** "Exciting News!..."
- **Character Count:** 156/280
- **Status:** Draft (awaiting approval)
- **Approval File:** /Pending_Approval/X_POST_001.md

## 2026-02-24 11:00:00 - X Posting Skill

- **Action:** Tweet Published
- **Tweet ID:** 1234567890
- **Status:** Success
```

---

## Posts Log Format

`Posts_Log_X.json`:

```json
[
  {
    "timestamp": "2026-02-24T10:30:00",
    "content": {
      "text": "Exciting News!...",
      "character_count": 156
    },
    "result": {
      "success": true,
      "tweet_id": "1234567890"
    }
  }
]
```

---

## Future Enhancements

- [ ] Thread creation (multiple connected tweets)
- [ ] Image upload support
- [ ] Poll creation
- [ ] Engagement tracking (likes, retweets)
- [ ] Auto-reply to mentions
- [ ] Scheduled posting
- [ ] Analytics integration

---

## Troubleshooting

### "API token missing"

```bash
# Check .env file
cat .env | grep X_API

# Get tokens from:
# https://developer.twitter.com/en/portal/dashboard
```

### "Tweet too long"

```
Error: Tweet too long (350/280 characters)

Fix: Shorten content to 280 characters or less
Tip: Use abbreviations, remove unnecessary words
```

### "Rate limit exceeded"

```
X API has rate limits:
- 300 tweets per 3 hours (standard)
- Wait before posting more
```

---

*End of Skill Document*
