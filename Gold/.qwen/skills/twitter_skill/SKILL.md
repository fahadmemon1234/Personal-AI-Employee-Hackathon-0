# Twitter (X) Agent Skill

## Overview
This skill enables the AI Agent to post tweets, create threads, and analyze Twitter performance using Twitter API v2.

## Capabilities
- **Post Tweet**: Publish tweets (max 280 characters)
- **Post Thread**: Create multi-tweet threads
- **Get User Metrics**: Retrieve follower count, following count, tweet count
- **Get Tweet Metrics**: Analyze individual tweet performance (likes, retweets, impressions)
- **Generate Summary**: Create comprehensive Twitter performance reports

## Configuration

### Required Environment Variables
```bash
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
TWITTER_ACCESS_TOKEN=your_twitter_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_twitter_access_token_secret
```

### How to Get Twitter API Credentials

1. **Apply for Twitter Developer Account**
   - Go to https://developer.twitter.com/
   - Apply for a developer account
   - Explain your use case (AI Agent automation)

2. **Create a Project and App**
   - Create a new project in Developer Portal
   - Create a new app within the project
   - Note down API Key and API Secret

3. **Generate Access Tokens**
   - Go to your app settings
   - Generate Access Token and Secret
   - Save all four credentials securely

4. **Set Permissions**
   - Ensure app has "Read and Write" permissions
   - For DM features, add "Direct Message" permissions

## Usage

### As MCP Server
```bash
python social_media_integration/twitter_mcp_server.py --port 8083
```

### API Endpoints
- `POST /api/v1/post/tweet` - Post a single tweet
- `POST /api/v1/post/thread` - Post a thread of tweets
- `GET /api/v1/metrics/user?username=example` - Get user metrics
- `GET /api/v1/metrics/tweet?tweet_id=123456` - Get tweet metrics
- `GET /api/v1/summary?days=7` - Generate performance summary

### Example Requests

#### Post a Tweet
```json
POST http://localhost:8083/api/v1/post/tweet
{
  "text": "Excited to announce our new AI services! 🚀 #AI #Innovation #TechStartup"
}
```

#### Post a Thread
```json
POST http://localhost:8083/api/v1/post/thread
{
  "tweets": [
    "🧵 Thread: 5 Ways AI is Transforming Business in 2026",
    "1/ Automation: AI-powered automation is reducing manual work by 60% across industries.",
    "2/ Customer Service: Chatbots now handle 80% of routine inquiries instantly.",
    "3/ Analytics: Predictive analytics help businesses make data-driven decisions faster.",
    "4/ Personalization: AI enables hyper-personalized customer experiences at scale.",
    "5/ Cost Savings: Companies using AI report average cost reductions of 25-30%."
  ]
}
```

#### Get Summary
```
GET http://localhost:8083/api/v1/summary?days=7
```

## Output Format

### Tweet Response
```json
{
  "success": true,
  "tweet_id": "1234567890123456789",
  "platform": "twitter",
  "text": "Excited to announce our new AI services! 🚀",
  "timestamp": "2026-02-17T10:30:00"
}
```

### Thread Response
```json
{
  "success": true,
  "tweet_ids": ["1234567890123456789", "1234567890123456790"],
  "thread_count": 2,
  "platform": "twitter",
  "timestamp": "2026-02-17T10:30:00"
}
```

### Summary Response
```json
{
  "period": "Last 7 days",
  "generated_at": "2026-02-17T10:30:00",
  "account": {
    "username": "yourhandle",
    "followers": 1500,
    "following": 350,
    "total_tweets": 423
  },
  "recent_activity": {
    "tweets_analyzed": 10,
    "total_engagement": 450,
    "total_impressions": 12500,
    "avg_engagement_per_tweet": 45.0
  },
  "top_tweets": [...],
  "recommendations": [
    "Great engagement! Continue your current content strategy."
  ]
}
```

## Best Practices

### Content Strategy
1. **Tweet Consistently**: Post 3-5 times daily for optimal growth
2. **Use Threads**: Threads get 3-5x more engagement than single tweets
3. **Include Media**: Tweets with images/videos get 150% more retweets
4. **Engage**: Reply to comments within 2 hours
5. **Use Hashtags**: 2-3 relevant hashtags per tweet
6. **Timing**: Post during peak hours (8-10 AM, 6-9 PM in your timezone)

### Thread Best Practices
- Start with a compelling hook (first tweet)
- Number each tweet (1/, 2/, etc.)
- Keep each tweet under 260 characters (leave room for engagement)
- End with a call-to-action or summary
- Use emojis to make threads visually appealing

### Engagement Tips
- Reply to every comment in the first hour
- Quote tweet with valuable additions
- Participate in trending topics in your niche
- Tag relevant accounts when appropriate (don't spam)

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| "Tweet text must be 280 characters or less" | Text too long | Shorten your tweet or use a thread |
| "Authentication failed" | Invalid credentials | Check all four API credentials |
| "Rate limit exceeded" | Too many requests | Wait 15 minutes before retrying |
| "Account is suspended" | Policy violation | Review Twitter Rules |

## Rate Limits

Twitter API v2 limits:
- **Tweets**: 200 per 24 hours (free tier)
- **Read requests**: 300 per 15 minutes
- **User lookup**: 300 per 15 minutes

## Security Notes
- Never commit API credentials to version control
- Use environment variables or secret management
- Rotate credentials every 90 days
- Monitor app usage for unusual activity
- Follow Twitter Developer Agreement and Policy

## Troubleshooting

### "Could not connect to Twitter"
- Verify all four credentials are set correctly
- Check if your Twitter Developer account is approved
- Ensure app permissions include "Read and Write"

### "Rate limit exceeded"
- Free tier has strict limits
- Consider upgrading to Basic tier ($100/month) for higher limits
- Implement request queuing to stay within limits

### Tweets not appearing
- Check if account is shadow-banned
- Verify app has write permissions
- Review Twitter Rules for content compliance

## Integration with Agent System

The Twitter skill integrates with the AI Agent system through:
- **Agent Skills Framework**: Located in `.qwen/skills/twitter_skill/`
- **MCP Server**: Runs on port 8083
- **Audit Logging**: All actions logged to `Audit_Log.md`
- **Summary Reports**: Saved to `Social_Media_Summaries/` folder

## Example: Automated Daily Tweet

```python
from twitter_skill import post_tweet, generate_summary

# Post daily update
post_tweet("🌅 Good morning! Today's focus: Building amazing AI solutions for our clients. #MondayMotivation #AI")

# Generate weekly summary every Monday
if datetime.now().weekday() == 0:  # Monday
    summary = generate_summary(7)
    # Save summary and review recommendations
```
