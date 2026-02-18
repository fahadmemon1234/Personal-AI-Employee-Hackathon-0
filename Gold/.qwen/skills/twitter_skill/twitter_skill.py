"""
twitter_skill.py
Agent Skill for Twitter (X) integration
Posts tweets, creates threads, and generates performance summaries
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import json

# Add the project root to the path
sys.path.append(str(Path(__file__).parent.parent.parent))

from social_media_integration.twitter_connector import (
    get_twitter_connection
)


def post_tweet(text: str, media_url: str = None) -> dict:
    """
    Post a tweet to Twitter

    Args:
        text: The tweet text (max 280 characters)
        media_url: Optional media URL to attach

    Returns:
        Dict with success status and tweet details
    """
    try:
        connector = get_twitter_connection()
        
        if not connector:
            return {
                "success": False,
                "error": "Could not connect to Twitter. Check credentials.",
                "skill": "twitter"
            }

        result = connector.post_tweet(text, media_url)
        result["skill"] = "twitter"
        
        # Log the action
        _log_action("tweet_post", result)
        
        return result

    except Exception as e:
        error_msg = f"Error posting tweet: {str(e)}"
        print(error_msg)
        return {
            "success": False,
            "error": error_msg,
            "skill": "twitter"
        }


def post_thread(tweets: list) -> dict:
    """
    Post a thread of tweets

    Args:
        tweets: List of tweet texts

    Returns:
        Dict with success status and thread details
    """
    try:
        connector = get_twitter_connection()
        
        if not connector:
            return {
                "success": False,
                "error": "Could not connect to Twitter. Check credentials.",
                "skill": "twitter"
            }

        result = connector.post_thread(tweets)
        result["skill"] = "twitter"
        
        # Log the action
        _log_action("thread_post", result)
        
        return result

    except Exception as e:
        error_msg = f"Error posting thread: {str(e)}"
        print(error_msg)
        return {
            "success": False,
            "error": error_msg,
            "skill": "twitter"
        }


def generate_twitter_summary(days: int = 7) -> dict:
    """
    Generate a comprehensive summary of Twitter performance

    Args:
        days: Number of days to analyze

    Returns:
        Dict with performance summary and recommendations
    """
    try:
        connector = get_twitter_connection()
        
        if not connector:
            return {
                "success": False,
                "error": "Could not connect to Twitter. Check credentials.",
                "skill": "twitter"
            }

        summary = connector.generate_summary(days)
        summary["success"] = True
        summary["skill"] = "twitter"
        
        # Save summary to file
        _save_summary(summary)
        
        return summary

    except Exception as e:
        error_msg = f"Error generating summary: {str(e)}"
        print(error_msg)
        return {
            "success": False,
            "error": error_msg,
            "skill": "twitter"
        }


def get_user_metrics(username: str = None) -> dict:
    """
    Get Twitter user metrics

    Args:
        username: Twitter username (without @)

    Returns:
        Dict with user metrics
    """
    try:
        connector = get_twitter_connection()
        
        if not connector:
            return {
                "success": False,
                "error": "Could not connect to Twitter. Check credentials.",
                "skill": "twitter"
            }

        metrics = connector.get_user_metrics(username)
        metrics["success"] = True
        metrics["skill"] = "twitter"
        
        return metrics

    except Exception as e:
        error_msg = f"Error getting user metrics: {str(e)}"
        print(error_msg)
        return {
            "success": False,
            "error": error_msg,
            "skill": "twitter"
        }


def get_tweet_metrics(tweet_id: str) -> dict:
    """
    Get metrics for a specific tweet

    Args:
        tweet_id: The tweet ID

    Returns:
        Dict with tweet metrics
    """
    try:
        connector = get_twitter_connection()
        
        if not connector:
            return {
                "success": False,
                "error": "Could not connect to Twitter. Check credentials.",
                "skill": "twitter"
            }

        metrics = connector.get_tweet_metrics(tweet_id)
        metrics["success"] = True
        metrics["skill"] = "twitter"
        
        return metrics

    except Exception as e:
        error_msg = f"Error getting tweet metrics: {str(e)}"
        print(error_msg)
        return {
            "success": False,
            "error": error_msg,
            "skill": "twitter"
        }


def _log_action(action_type: str, result: dict):
    """Log actions to audit log"""
    try:
        audit_log_path = Path("Audit_Log.md")
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = "Success" if result.get("success") else "Failed"
        
        log_entry = f"- [{timestamp}] Twitter Skill - {action_type} - {status}\n"
        
        if audit_log_path.exists():
            with open(audit_log_path, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        else:
            with open(audit_log_path, 'w', encoding='utf-8') as f:
                f.write("# Audit Log\n\n")
                f.write(log_entry)
                
    except Exception as e:
        print(f"Error logging action: {str(e)}")


def _save_summary(summary: dict):
    """Save summary to Social_Media_Summaries folder"""
    try:
        summaries_dir = Path("Social_Media_Summaries")
        summaries_dir.mkdir(exist_ok=True)
        
        filename = f"Twitter_Summary_{datetime.now().strftime('%Y%m%d')}.md"
        filepath = summaries_dir / filename
        
        content = f"""# Twitter Performance Summary
**Generated:** {summary.get('generated_at', datetime.now().isoformat())}
**Period:** {summary.get('period', 'Last 7 days')}

---

## Account Overview

- **Username:** @{summary.get('account', {}).get('username', 'N/A')}
- **Followers:** {summary.get('account', {}).get('followers', 0):,}
- **Following:** {summary.get('account', {}).get('following', 0):,}
- **Total Tweets:** {summary.get('account', {}).get('total_tweets', 0):,}

---

## Recent Activity

- **Tweets Analyzed:** {summary.get('recent_activity', {}).get('tweets_analyzed', 0)}
- **Total Engagement:** {summary.get('recent_activity', {}).get('total_engagement', 0):,}
- **Total Impressions:** {summary.get('recent_activity', {}).get('total_impressions', 0):,}
- **Avg Engagement per Tweet:** {summary.get('recent_activity', {}).get('avg_engagement_per_tweet', 0):.2f}

---

## Recommendations

"""
        
        for i, rec in enumerate(summary.get('recommendations', []), 1):
            content += f"{i}. {rec}\n"
        
        content += "\n---\n*This report was automatically generated by the Twitter Agent Skill.*\n"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Summary saved to: {filepath}")
        
    except Exception as e:
        print(f"Error saving summary: {str(e)}")


def twitter_skill_cli():
    """Command-line interface for the Twitter Skill"""
    import argparse

    parser = argparse.ArgumentParser(description="Twitter Agent Skill")
    parser.add_argument("--action", choices=["post-tweet", "post-thread", "summary", "metrics"],
                       required=True, help="Action to perform")
    parser.add_argument("--text", help="Tweet text (for post-tweet)")
    parser.add_argument("--tweets", nargs='+', help="List of tweets for thread (for post-thread)")
    parser.add_argument("--username", help="Twitter username (for metrics)")
    parser.add_argument("--tweet-id", help="Tweet ID (for tweet metrics)")
    parser.add_argument("--days", type=int, default=7, help="Number of days for summary")

    args = parser.parse_args()

    if args.action == "post-tweet":
        if not args.text:
            print("Error: --text is required for posting a tweet")
            sys.exit(1)
        result = post_tweet(args.text)
        
    elif args.action == "post-thread":
        if not args.tweets:
            print("Error: --tweets is required for posting a thread")
            sys.exit(1)
        result = post_thread(args.tweets)
        
    elif args.action == "summary":
        result = generate_twitter_summary(args.days)
        
    elif args.action == "metrics":
        if args.tweet_id:
            result = get_tweet_metrics(args.tweet_id)
        else:
            result = get_user_metrics(args.username)
        
    print(json.dumps(result, indent=2))
    
    if not result.get("success"):
        sys.exit(1)


if __name__ == "__main__":
    twitter_skill_cli()
