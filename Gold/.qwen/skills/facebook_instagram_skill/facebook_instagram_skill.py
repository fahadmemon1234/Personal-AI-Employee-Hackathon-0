"""
facebook_instagram_skill.py
Agent Skill for Facebook and Instagram integration
Posts content and generates performance summaries
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import json

# Add the project root to the path
sys.path.append(str(Path(__file__).parent.parent.parent))

from social_media_integration.facebook_instagram_connector import (
    get_facebook_instagram_connection
)


def post_to_facebook(message: str, link: str = None, photo_url: str = None) -> dict:
    """
    Post content to Facebook Page

    Args:
        message: The message to post
        link: Optional link to share
        photo_url: Optional photo URL

    Returns:
        Dict with success status and post details
    """
    try:
        connector = get_facebook_instagram_connection()
        
        if not connector:
            return {
                "success": False,
                "error": "Could not connect to Facebook/Instagram. Check credentials.",
                "skill": "facebook_instagram"
            }

        result = connector.post_to_facebook(message, link, photo_url)
        result["skill"] = "facebook_instagram"
        
        # Log the action
        _log_action("facebook_post", result)
        
        return result

    except Exception as e:
        error_msg = f"Error posting to Facebook: {str(e)}"
        print(error_msg)
        return {
            "success": False,
            "error": error_msg,
            "skill": "facebook_instagram"
        }


def post_to_instagram(caption: str, image_url: str) -> dict:
    """
    Post content to Instagram

    Args:
        caption: The caption for the post
        image_url: URL of the image to post

    Returns:
        Dict with success status and post details
    """
    try:
        connector = get_facebook_instagram_connection()
        
        if not connector:
            return {
                "success": False,
                "error": "Could not connect to Facebook/Instagram. Check credentials.",
                "skill": "facebook_instagram"
            }

        result = connector.post_to_instagram(caption, image_url)
        result["skill"] = "facebook_instagram"
        
        # Log the action
        _log_action("instagram_post", result)
        
        return result

    except Exception as e:
        error_msg = f"Error posting to Instagram: {str(e)}"
        print(error_msg)
        return {
            "success": False,
            "error": error_msg,
            "skill": "facebook_instagram"
        }


def generate_social_media_summary(days: int = 7) -> dict:
    """
    Generate a comprehensive summary of Facebook and Instagram performance

    Args:
        days: Number of days to analyze

    Returns:
        Dict with performance summary and recommendations
    """
    try:
        connector = get_facebook_instagram_connection()
        
        if not connector:
            return {
                "success": False,
                "error": "Could not connect to Facebook/Instagram. Check credentials.",
                "skill": "facebook_instagram"
            }

        summary = connector.generate_summary(days)
        summary["success"] = True
        summary["skill"] = "facebook_instagram"
        
        # Save summary to file
        _save_summary(summary)
        
        return summary

    except Exception as e:
        error_msg = f"Error generating summary: {str(e)}"
        print(error_msg)
        return {
            "success": False,
            "error": error_msg,
            "skill": "facebook_instagram"
        }


def get_facebook_insights(days: int = 7) -> dict:
    """
    Get Facebook Page insights

    Args:
        days: Number of days to retrieve

    Returns:
        Dict with Facebook insights
    """
    try:
        connector = get_facebook_instagram_connection()
        
        if not connector:
            return {
                "success": False,
                "error": "Could not connect to Facebook/Instagram. Check credentials.",
                "skill": "facebook_instagram"
            }

        insights = connector.get_facebook_insights(days)
        insights["success"] = True
        insights["skill"] = "facebook_instagram"
        
        return insights

    except Exception as e:
        error_msg = f"Error getting Facebook insights: {str(e)}"
        print(error_msg)
        return {
            "success": False,
            "error": error_msg,
            "skill": "facebook_instagram"
        }


def get_instagram_insights(days: int = 7) -> dict:
    """
    Get Instagram Business Account insights

    Args:
        days: Number of days to retrieve

    Returns:
        Dict with Instagram insights
    """
    try:
        connector = get_facebook_instagram_connection()
        
        if not connector:
            return {
                "success": False,
                "error": "Could not connect to Facebook/Instagram. Check credentials.",
                "skill": "facebook_instagram"
            }

        insights = connector.get_instagram_insights(days)
        insights["success"] = True
        insights["skill"] = "facebook_instagram"
        
        return insights

    except Exception as e:
        error_msg = f"Error getting Instagram insights: {str(e)}"
        print(error_msg)
        return {
            "success": False,
            "error": error_msg,
            "skill": "facebook_instagram"
        }


def _log_action(action_type: str, result: dict):
    """Log actions to audit log"""
    try:
        audit_log_path = Path("Audit_Log.md")
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = "Success" if result.get("success") else "Failed"
        
        log_entry = f"- [{timestamp}] Facebook/Instagram Skill - {action_type} - {status}\n"
        
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
        
        filename = f"Social_Media_Summary_{datetime.now().strftime('%Y%m%d')}.md"
        filepath = summaries_dir / filename
        
        content = f"""# Social Media Performance Summary
**Generated:** {summary.get('generated_at', datetime.now().isoformat())}
**Period:** {summary.get('period', 'Last 7 days')}

---

## Facebook Performance

### Key Metrics
"""
        
        fb_insights = summary.get('facebook', {}).get('insights', {})
        for metric, value in fb_insights.items():
            content += f"- **{metric.replace('_', ' ').title()}:** {value:,}\n"
        
        content += f"""
### Recent Posts
- Posts Count: {summary.get('facebook', {}).get('recent_posts_count', 0)}

---

## Instagram Performance

### Key Metrics
"""
        
        ig_insights = summary.get('instagram', {}).get('insights', {})
        for metric, value in ig_insights.items():
            content += f"- **{metric.replace('_', ' ').title()}:** {value:,}\n"
        
        content += f"""
### Recent Posts
- Posts Count: {summary.get('instagram', {}).get('recent_posts_count', 0)}

---

## Recommendations

"""
        
        for i, rec in enumerate(summary.get('recommendations', []), 1):
            content += f"{i}. {rec}\n"
        
        content += "\n---\n*This report was automatically generated by the Facebook/Instagram Agent Skill.*\n"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Summary saved to: {filepath}")
        
    except Exception as e:
        print(f"Error saving summary: {str(e)}")


def facebook_instagram_skill_cli():
    """Command-line interface for the Facebook/Instagram Skill"""
    import argparse

    parser = argparse.ArgumentParser(description="Facebook/Instagram Agent Skill")
    parser.add_argument("--action", choices=["post-facebook", "post-instagram", "summary", "insights"],
                       required=True, help="Action to perform")
    parser.add_argument("--message", help="Message to post (for Facebook)")
    parser.add_argument("--caption", help="Caption for Instagram post")
    parser.add_argument("--image-url", help="Image URL for Instagram post")
    parser.add_argument("--link", help="Link to share (for Facebook)")
    parser.add_argument("--days", type=int, default=7, help="Number of days for insights/summary")

    args = parser.parse_args()

    if args.action == "post-facebook":
        if not args.message:
            print("Error: --message is required for posting to Facebook")
            sys.exit(1)
        result = post_to_facebook(args.message, args.link)
        
    elif args.action == "post-instagram":
        if not args.caption or not args.image_url:
            print("Error: --caption and --image-url are required for Instagram post")
            sys.exit(1)
        result = post_to_instagram(args.caption, args.image_url)
        
    elif args.action == "summary":
        result = generate_social_media_summary(args.days)
        
    elif args.action == "insights":
        fb_result = get_facebook_insights(args.days)
        ig_result = get_instagram_insights(args.days)
        print(f"\nFacebook Insights: {json.dumps(fb_result, indent=2)}")
        print(f"\nInstagram Insights: {json.dumps(ig_result, indent=2)}")
        sys.exit(0)

    print(json.dumps(result, indent=2))
    
    if not result.get("success"):
        sys.exit(1)


if __name__ == "__main__":
    facebook_instagram_skill_cli()
