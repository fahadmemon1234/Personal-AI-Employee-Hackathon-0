# Agent Skill: Social Media Meta Integration

## Skill ID: `social_post_meta`

**Version:** 1.0  
**Created:** 2026-02-23  
**Author:** AI Digital FTE  
**Dependencies:** MCP Social Server (`mcp_social_server.py`), Playwright (optional for browser automation)

---

## Purpose

Automate Facebook and Instagram posting with Human-in-the-Loop (HITL) approval workflow. Generate engaging promotional content based on business goals, create draft posts, require approval before posting, and generate weekly summaries.

---

## Trigger Conditions

- Social media post request detected in `/Needs_Action/`
- Scheduled posting time (daily/weekly)
- Business milestone or announcement
- Manual invocation: `python reasoning_loop.py --skill=social_post_meta`

---

## Input

- `/Needs_Action/` files containing post requests
- `Business_Goals.md` for brand voice and messaging
- Email/WhatsApp messages with keywords: "post", "social media", "facebook", "instagram"
- Scheduled events (product launches, promotions)

---

## Output

- Draft posts in `/Plans/` requiring approval
- Posted content on Facebook/Instagram (after approval)
- Weekly summary in `/Briefings/meta_summary.md`
- Audit log in `/Audit_Log.md`

---

## MCP Server Configuration

### Environment Variables

Create/update `.env` file:

```bash
# Meta Social Media Settings
FACEBOOK_PAGE_ID=your_page_id_here
FACEBOOK_ACCESS_TOKEN=your_fb_token_here
INSTAGRAM_ACCOUNT_ID=your_ig_account_id
INSTAGRAM_ACCESS_TOKEN=your_ig_token_here

# Posting Mode
USE_BROWSER_AUTOMATION=false  # Set true if using browser instead of API
SOCIAL_DRY_RUN=true           # Set false for real posting
```

### Start MCP Social Server

```bash
python mcp_social_server.py
```

Server runs on: `http://localhost:8083`

---

## Available Tools (MCP Endpoints)

| Tool | Method | Endpoint | Description | Approval Required |
|------|--------|----------|-------------|-------------------|
| `post_to_facebook` | POST | `/tools/post_to_facebook` | Post to Facebook page | **Yes** |
| `post_to_instagram` | POST | `/tools/post_to_instagram` | Post to Instagram account | **Yes** |
| `generate_summary` | GET | `/tools/generate_summary` | Generate weekly summary | No |
| `list_posts` | GET | `/tools/list_posts` | List recent posts | No |

---

## Procedure

### Step 1: Detect Post Request

Scan `/Needs_Action/` for files containing:

**Keywords:**
- "post to facebook", "post to instagram", "social media"
- "promote", "announcement", "new product"
- "share", "update status"

**Classification:**
```python
SOCIAL_KEYWORDS = ['post', 'facebook', 'instagram', 'social media', 'promote', 'share']
PLATFORM_KEYWORDS = {
    'facebook': ['facebook', 'fb', 'meta'],
    'instagram': ['instagram', 'ig', 'insta']
}
```

### Step 2: Read Business Goals

Load `Business_Goals.md` (if exists) to understand:

- Brand voice (professional, friendly, casual)
- Target audience
- Key messaging points
- Hashtags to use
- Posting frequency

**Example Business_Goals.md:**
```markdown
# Business Goals

## Brand Voice
- Professional yet friendly
- Focus on quality and customer satisfaction
- Use emojis sparingly 😊

## Target Audience
- Small business owners
- Entrepreneurs
- Age: 25-45

## Key Hashtags
#WebDevelopment #GraphicDesign #AI #Pakistan #Freelancer
```

### Step 3: Generate Post Content

Create engaging post based on:

1. **Request content** (what to post)
2. **Business goals** (brand voice)
3. **Platform best practices** (character limits, hashtags)

**Facebook Post Template:**
```
🎉 [Headline]

[Main content - 2-3 paragraphs]

✅ [Key benefit 1]
✅ [Key benefit 2]
✅ [Key benefit 3]

📞 Contact us: [Contact info]
🌐 Visit: [Website]

#Hashtag1 #Hashtag2 #Hashtag3
```

**Instagram Post Template:**
```
[Engaging caption - 1-2 paragraphs]

[Emoji for visual appeal]

#Hashtag1 #Hashtag2 #Hashtag3 #Hashtag4 #Hashtag5
```

### Step 4: Create Draft Plan

Create `/Plans/Plan_Social_[timestamp]_[platform].md`:

```markdown
# Social Media Post Plan

**Generated:** 2026-02-23 10:00:00  
**Platform:** Facebook / Instagram  
**Source:** email_Post_Request_20260223.md  
**Priority:** Normal

---

## Post Content

### Facebook
```
🎉 Exciting News!

We're thrilled to announce our new AI-driven web development services!

✅ Faster delivery times
✅ Higher quality code
✅ Better customer support

📞 +92-300-1234567
🌐 www.yourbusiness.com

#WebDev #AI #Pakistan
```

### Instagram
```
Transform your business with AI-powered solutions! 🚀

#WebDevelopment #AI #Tech #Pakistan #Business
```

---

## Media

- [ ] Image attached: `social_media_image.jpg`
- [ ] Use default brand image
- [ ] No image (text only)

---

## Posting Schedule

- [ ] Post immediately after approval
- [ ] Schedule for: [Date/Time]
- [ ] Best time: Facebook (9 AM), Instagram (6 PM)

---

## Required Approvals

| Action | Type | Status |
|--------|------|--------|
| Review content | Content | Pending |
| Approve for posting | Publishing | Pending |
| Media selection | Creative | Pending |

---

## MCP Calls Required

1. `mcp_social_server` - POST /tools/post_to_facebook
2. `mcp_social_server` - POST /tools/post_to_instagram

---

## Approval Instructions

1. Review the post content above
2. Check for typos and brand alignment
3. If correct, move this file to `/Approved/`
4. The system will post to selected platforms
5. If changes needed, edit and add comments

---

*Created by social_post_meta skill*
```

### Step 5: Wait for Approval

- File stays in `/Pending_Approval/` until human reviews
- Human moves to `/Approved/` to authorize posting
- System posts to Facebook/Instagram

### Step 6: Post Content (After Approval)

```python
# Post to Facebook
response = requests.post('http://localhost:8083/tools/post_to_facebook', json={
    "page_id": page_id,
    "message": post_content,
    "image_path": image_path,
    "dry_run": False  # Real posting
})

# Post to Instagram
response = requests.post('http://localhost:8083/tools/post_to_instagram', json={
    "account_id": account_id,
    "caption": caption,
    "media_path": image_path,
    "dry_run": False
})
```

### Step 7: Generate Weekly Summary

```python
# Generate summary
response = requests.get('http://localhost:8083/tools/generate_summary')
summary = response.json()

# Save to Briefings
with open('Briefings/meta_summary.md', 'w') as f:
    f.write(summary_content)
```

---

## Company Handbook Compliance

| Rule | Implementation |
|------|----------------|
| **Efficiency First** | Auto-generate posts, manual approval only |
| **Data Integrity** | All posts logged in Posts_Log.json |
| **Security** | API tokens via environment variables |
| **Transparency** | Draft posts in `/Plans/` for review |
| **Proactivity** | Suggest posts based on business events |
| **Polite Tone** | All posts maintain professional brand voice |
| **Approval Required** | No posting without human approval |
| **Dry Run Default** | Safe mode enabled by default |

---

## Error Handling

| Error | Action |
|-------|--------|
| API token missing | Log error, use dry-run mode, notify admin |
| Image not found | Skip image, post text only, flag for review |
| Post failed | Log error, keep in `/Pending_Approval/`, retry option |
| Rate limit exceeded | Queue for later, notify admin |

---

## Usage Examples

### Example 1: Post Product Launch

**Input:** `/Needs_Action/email_New_Product_Launch.md`

```
Subject: New AI Service Launch

Please post about our new AI-driven web development service on Facebook and Instagram.

Key points:
- 50% faster delivery
- Better code quality
- Competitive pricing
```

**Skill Execution:**
```bash
python reasoning_loop.py --skill=social_post_meta
```

**Output:**
- Draft plan: `/Plans/Plan_Social_20260223_Facebook.md`
- Approval file: `/Pending_Approval/SOCIAL_POST_001.md`

### Example 2: Generate Weekly Summary

**Input:** Manual request or scheduled

**Skill Execution:**
```bash
curl http://localhost:8083/tools/generate_summary
```

**Output:**
- Summary saved to: `/Briefings/meta_summary.md`

---

## Integration with Approval Workflow

### File Movement Pattern

```
/Needs_Action/post_request.md
       ↓ (detected by skill)
[Generate post content]
       ↓
/Pending_Approval/SOCIAL_POST_*.md
       ↓ (human moves to Approved)
[Post to Facebook/Instagram]
       ↓
/Completed/SOCIAL_POST_*.md
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
SOCIAL_DRY_RUN=true

# Run skill
python reasoning_loop.py --skill=social_post_meta

# Or direct API test
curl -X POST http://localhost:8083/tools/post_to_facebook \
  -H "Content-Type: application/json" \
  -d '{"page_id":"test","message":"Test post","dry_run":true}'
```

### Test With Real Posting

```bash
# 1. Set dry_run to false
SOCIAL_DRY_RUN=false

# 2. Configure API tokens in .env

# 3. Create post request
echo "Post to Facebook: Test announcement" > Needs_Action/test_post.md

# 4. Run skill
python reasoning_loop.py --skill=social_post_meta
```

---

## Audit Trail

All actions logged in `Audit_Log.md`:

```markdown
## 2026-02-23 10:30:00 - Social Media Skill

- **Action:** Post Created
- **Platform:** Facebook
- **Content:** "Exciting News!..."
- **Status:** Draft (awaiting approval)
- **Approval File:** /Pending_Approval/SOCIAL_POST_001.md

## 2026-02-23 11:00:00 - Social Media Skill

- **Action:** Post Published
- **Platform:** Facebook
- **Post ID:** 12345_67890
- **Status:** Success
```

---

## Posts Log Format

`Posts_Log.json`:

```json
[
  {
    "timestamp": "2026-02-23T10:30:00",
    "platform": "facebook",
    "content": {
      "message": "Exciting News!...",
      "page_id": "your_page_id"
    },
    "result": {
      "success": true,
      "post_id": "12345_67890"
    }
  }
]
```

---

## Future Enhancements

- [ ] Auto-scheduling for optimal posting times
- [ ] Image generation with DALL-E
- [ ] A/B testing for post variations
- [ ] Engagement tracking (likes, comments, shares)
- [ ] Cross-posting to LinkedIn, Twitter
- [ ] Sentiment analysis on comments
- [ ] Auto-reply to common comments

---

## Troubleshooting

### "API token missing"

```bash
# Check .env file
cat .env | grep ACCESS_TOKEN

# Get Facebook token from:
# https://developers.facebook.com/tools/explorer/

# Get Instagram token from:
# https://developers.facebook.com/docs/instagram-api
```

### "Browser automation failed"

```bash
# Install Playwright
pip install playwright
playwright install

# Or use API mode instead
USE_BROWSER_AUTOMATION=false
```

### "Post not appearing"

```bash
# Check if dry_run is enabled
cat .env | grep DRY_RUN

# If true, posts are simulated
# Set to false for real posting
SOCIAL_DRY_RUN=false
```

---

*End of Skill Document*
