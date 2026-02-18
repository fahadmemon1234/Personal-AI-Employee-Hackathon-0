# Facebook/Instagram Agent Skill

## Overview
This skill enables the AI Agent to post content and analyze performance on Facebook and Instagram platforms using Meta Graph API.

## Capabilities
- **Post to Facebook**: Share text posts, links, and photos on your Facebook Page
- **Post to Instagram**: Publish image posts with captions to Instagram Business Account
- **Get Insights**: Retrieve engagement metrics, reach, and impressions
- **Generate Summary**: Create comprehensive performance reports with recommendations

## Configuration

### Required Environment Variables
```bash
META_ACCESS_TOKEN=your_meta_graph_api_access_token
FACEBOOK_PAGE_ID=your_facebook_page_id
INSTAGRAM_BUSINESS_ACCOUNT_ID=your_instagram_business_account_id
```

### How to Get Credentials

1. **Create a Meta Developer Account**
   - Go to https://developers.facebook.com/
   - Create a new app or use existing one

2. **Get Access Token**
   - Use Graph API Explorer: https://developers.facebook.com/tools/explorer/
   - Select your app and generate token with permissions:
     - `pages_manage_posts`
     - `pages_read_engagement`
     - `instagram_basic`
     - `instagram_content_publish`
     - `instagram_manage_insights`

3. **Get Facebook Page ID**
   - Go to your Facebook Page
   - Click About → Page ID

4. **Get Instagram Business Account ID**
   - Convert Instagram to Business Account
   - Connect to Facebook Page
   - Use Graph API: `GET /me/accounts` to find linked Instagram account

## Usage

### As MCP Server
```bash
python social_media_integration/facebook_instagram_mcp_server.py --port 8082
```

### API Endpoints
- `POST /api/v1/post/facebook` - Post to Facebook
- `POST /api/v1/post/instagram` - Post to Instagram
- `GET /api/v1/insights/facebook?days=7` - Get Facebook insights
- `GET /api/v1/insights/instagram?days=7` - Get Instagram insights
- `GET /api/v1/summary?days=7` - Generate combined summary

### Example Requests

#### Post to Facebook
```json
POST http://localhost:8082/api/v1/post/facebook
{
  "message": "Check out our new AI services!",
  "link": "https://example.com",
  "photo_url": "https://example.com/image.jpg"
}
```

#### Post to Instagram
```json
POST http://localhost:8082/api/v1/post/instagram
{
  "caption": "Exciting news! 🚀 #AI #Innovation",
  "image_url": "https://example.com/image.jpg"
}
```

#### Generate Summary
```
GET http://localhost:8082/api/v1/summary?days=7
```

## Output Format

### Post Response
```json
{
  "success": true,
  "post_id": "123456789_987654321",
  "platform": "facebook",
  "timestamp": "2026-02-17T10:30:00"
}
```

### Summary Response
```json
{
  "period": "Last 7 days",
  "generated_at": "2026-02-17T10:30:00",
  "facebook": {
    "insights": {
      "page_impressions_unique": 1500,
      "page_engaged_users": 250,
      "page_post_engagements": 180
    },
    "recent_posts_count": 5,
    "top_posts": [...]
  },
  "instagram": {
    "insights": {
      "impressions": 2000,
      "reach": 1800,
      "engagement": 320
    },
    "recent_posts_count": 3,
    "top_posts": [...]
  },
  "recommendations": [
    "Facebook engagement is low. Consider posting more interactive content."
  ]
}
```

## Error Handling
- Invalid credentials: Returns 503 with error message
- Missing parameters: Returns 400 with validation error
- API rate limits: Returns error with retry suggestion
- Network errors: Logged and returned as 500 error

## Best Practices
1. Post consistently (1-2 times per day)
2. Use high-quality images for Instagram
3. Include relevant hashtags (5-10 for Instagram)
4. Post during peak engagement hours (9-11 AM, 7-9 PM)
5. Respond to comments within 24 hours
6. Review insights weekly to optimize content strategy

## Troubleshooting

### "Invalid Access Token"
- Token may have expired. Generate a new long-lived token (60 days)
- Ensure all required permissions are granted

### "Page ID not found"
- Verify the Page ID is correct
- Ensure the access token has permission for this page

### "Instagram account not linked"
- Make sure Instagram is converted to Business Account
- Link Instagram to Facebook Page in Facebook Business Manager

## Security Notes
- Never commit access tokens to version control
- Use environment variables or secure secret management
- Rotate tokens every 60 days
- Limit token permissions to minimum required
