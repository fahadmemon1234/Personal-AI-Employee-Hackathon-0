"""
facebook_instagram_connector.py
Connector for Facebook and Instagram using Meta Graph API
"""

import requests
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional


class FacebookInstagramConnector:
    """
    Connector class for interacting with Facebook and Instagram via Meta Graph API
    """

    def __init__(self, access_token: str, facebook_page_id: str, instagram_business_account_id: str):
        """
        Initialize the Facebook/Instagram connector

        Args:
            access_token: Meta Graph API access token
            facebook_page_id: Facebook Page ID
            instagram_business_account_id: Instagram Business Account ID
        """
        self.access_token = access_token
        self.facebook_page_id = facebook_page_id
        self.instagram_business_account_id = instagram_business_account_id
        self.graph_api_version = "v18.0"
        self.base_url = f"https://graph.facebook.com/{self.graph_api_version}"

        print(f"Facebook/Instagram Connector initialized")
        print(f"- Facebook Page ID: {facebook_page_id}")
        print(f"- Instagram Business Account ID: {instagram_business_account_id}")

    def post_to_facebook(self, message: str, link: str = None, photo_url: str = None) -> Dict:
        """
        Post a message to Facebook Page

        Args:
            message: The message to post
            link: Optional link to share
            photo_url: Optional photo URL to post

        Returns:
            Dict with post_id and status
        """
        try:
            endpoint = f"{self.base_url}/{self.facebook_page_id}/feed"
            
            params = {
                "message": message,
                "access_token": self.access_token
            }

            if link:
                params["link"] = link
            
            if photo_url:
                params["picture"] = photo_url

            response = requests.post(endpoint, params=params, timeout=30)
            result = response.json()

            if response.status_code == 200 and "id" in result:
                print(f"Facebook post created successfully: {result['id']}")
                return {
                    "success": True,
                    "post_id": result["id"],
                    "platform": "facebook",
                    "timestamp": datetime.now().isoformat()
                }
            else:
                print(f"Facebook post failed: {result}")
                return {
                    "success": False,
                    "error": result.get("error", {}).get("message", "Unknown error"),
                    "platform": "facebook"
                }

        except Exception as e:
            print(f"Error posting to Facebook: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "platform": "facebook"
            }

    def post_to_instagram(self, caption: str, image_url: str) -> Dict:
        """
        Post an image to Instagram

        Args:
            caption: The caption for the post
            image_url: URL of the image to post

        Returns:
            Dict with post_id and status
        """
        try:
            # Step 1: Create a media container
            container_endpoint = f"{self.base_url}/{self.instagram_business_account_id}/media"
            
            container_params = {
                "image_url": image_url,
                "caption": caption,
                "access_token": self.access_token
            }

            container_response = requests.post(container_endpoint, params=container_params, timeout=30)
            container_result = container_response.json()

            if container_response.status_code != 200:
                print(f"Instagram container creation failed: {container_result}")
                return {
                    "success": False,
                    "error": container_result.get("error", {}).get("message", "Unknown error"),
                    "platform": "instagram"
                }

            creation_id = container_result.get("id")

            # Step 2: Publish the media
            publish_endpoint = f"{self.base_url}/{self.instagram_business_account_id}/media_publish"
            
            publish_params = {
                "creation_id": creation_id,
                "access_token": self.access_token
            }

            publish_response = requests.post(publish_endpoint, params=publish_params, timeout=30)
            publish_result = publish_response.json()

            if publish_response.status_code == 200 and "id" in publish_result:
                print(f"Instagram post created successfully: {publish_result['id']}")
                return {
                    "success": True,
                    "post_id": publish_result["id"],
                    "platform": "instagram",
                    "timestamp": datetime.now().isoformat()
                }
            else:
                print(f"Instagram post failed: {publish_result}")
                return {
                    "success": False,
                    "error": publish_result.get("error", {}).get("message", "Unknown error"),
                    "platform": "instagram"
                }

        except Exception as e:
            print(f"Error posting to Instagram: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "platform": "instagram"
            }

    def get_facebook_insights(self, days: int = 7) -> Dict:
        """
        Get Facebook Page insights for the last N days

        Args:
            days: Number of days to retrieve insights for

        Returns:
            Dict with engagement metrics
        """
        try:
            endpoint = f"{self.base_url}/{self.facebook_page_id}/insights"
            
            # Calculate date range
            since_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            until_date = datetime.now().strftime("%Y-%m-%d")

            params = {
                "metric": "page_impressions_unique,page_engaged_users,page_post_engagements,page_likes",
                "since": since_date,
                "until": until_date,
                "access_token": self.access_token
            }

            response = requests.get(endpoint, params=params, timeout=30)
            result = response.json()

            if response.status_code == 200:
                insights = result.get("data", [])
                
                summary = {
                    "platform": "facebook",
                    "period": f"{days} days",
                    "since": since_date,
                    "until": until_date,
                    "metrics": {}
                }

                for metric in insights:
                    name = metric.get("name")
                    values = metric.get("values", [])
                    total = sum(v.get("value", 0) for v in values)
                    summary["metrics"][name] = total

                print(f"Facebook insights retrieved for {days} days")
                return summary
            else:
                print(f"Facebook insights failed: {result}")
                return {
                    "platform": "facebook",
                    "error": result.get("error", {}).get("message", "Unknown error")
                }

        except Exception as e:
            print(f"Error getting Facebook insights: {str(e)}")
            return {
                "platform": "facebook",
                "error": str(e)
            }

    def get_instagram_insights(self, days: int = 7) -> Dict:
        """
        Get Instagram Business Account insights for the last N days

        Args:
            days: Number of days to retrieve insights for

        Returns:
            Dict with engagement metrics
        """
        try:
            endpoint = f"{self.base_url}/{self.instagram_business_account_id}/insights"
            
            # Calculate date range
            since_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            until_date = datetime.now().strftime("%Y-%m-%d")

            params = {
                "metric": "impressions,reach,engagement,profile_views,follower_count",
                "period": "day",
                "since": since_date,
                "until": until_date,
                "access_token": self.access_token
            }

            response = requests.get(endpoint, params=params, timeout=30)
            result = response.json()

            if response.status_code == 200:
                insights = result.get("data", [])
                
                summary = {
                    "platform": "instagram",
                    "period": f"{days} days",
                    "since": since_date,
                    "until": until_date,
                    "metrics": {}
                }

                for metric in insights:
                    name = metric.get("name")
                    values = metric.get("values", [])
                    total = sum(v.get("value", 0) for v in values)
                    summary["metrics"][name] = total

                print(f"Instagram insights retrieved for {days} days")
                return summary
            else:
                print(f"Instagram insights failed: {result}")
                return {
                    "platform": "instagram",
                    "error": result.get("error", {}).get("message", "Unknown error")
                }

        except Exception as e:
            print(f"Error getting Instagram insights: {str(e)}")
            return {
                "platform": "instagram",
                "error": str(e)
            }

    def get_recent_posts(self, platform: str, limit: int = 10) -> List[Dict]:
        """
        Get recent posts from Facebook or Instagram

        Args:
            platform: 'facebook' or 'instagram'
            limit: Number of posts to retrieve

        Returns:
            List of post data
        """
        try:
            if platform == "facebook":
                endpoint = f"{self.base_url}/{self.facebook_page_id}/posts"
                params = {
                    "fields": "message,created_time,likes.summary(true),comments.summary(true),shares",
                    "limit": limit,
                    "access_token": self.access_token
                }
            elif platform == "instagram":
                endpoint = f"{self.base_url}/{self.instagram_business_account_id}/media"
                params = {
                    "fields": "caption,timestamp,like_count,comments_count",
                    "limit": limit,
                    "access_token": self.access_token
                }
            else:
                return []

            response = requests.get(endpoint, params=params, timeout=30)
            result = response.json()

            if response.status_code == 200:
                posts = result.get("data", [])
                print(f"Retrieved {len(posts)} recent posts from {platform}")
                return posts
            else:
                print(f"Failed to get posts from {platform}: {result}")
                return []

        except Exception as e:
            print(f"Error getting posts from {platform}: {str(e)}")
            return []

    def generate_summary(self, days: int = 7) -> Dict:
        """
        Generate a comprehensive summary of Facebook and Instagram activity

        Args:
            days: Number of days to summarize

        Returns:
            Dict with combined summary
        """
        fb_insights = self.get_facebook_insights(days)
        ig_insights = self.get_instagram_insights(days)
        fb_posts = self.get_recent_posts("facebook", 5)
        ig_posts = self.get_recent_posts("instagram", 5)

        summary = {
            "period": f"Last {days} days",
            "generated_at": datetime.now().isoformat(),
            "facebook": {
                "insights": fb_insights.get("metrics", {}),
                "recent_posts_count": len(fb_posts),
                "top_posts": fb_posts[:3] if fb_posts else []
            },
            "instagram": {
                "insights": ig_insights.get("metrics", {}),
                "recent_posts_count": len(ig_posts),
                "top_posts": ig_posts[:3] if ig_posts else []
            },
            "recommendations": self._generate_recommendations(fb_insights, ig_insights)
        }

        return summary

    def _generate_recommendations(self, fb_insights: Dict, ig_insights: Dict) -> List[str]:
        """
        Generate recommendations based on insights
        """
        recommendations = []

        fb_metrics = fb_insights.get("metrics", {})
        ig_metrics = ig_insights.get("metrics", {})

        # Facebook recommendations
        if fb_metrics.get("page_post_engagements", 0) < 100:
            recommendations.append("Facebook engagement is low. Consider posting more interactive content like polls or questions.")

        if fb_metrics.get("page_impressions_unique", 0) < 500:
            recommendations.append("Facebook reach is limited. Try posting at peak hours (9-11 AM or 7-9 PM).")

        # Instagram recommendations
        if ig_metrics.get("engagement", 0) < 50:
            recommendations.append("Instagram engagement needs improvement. Use trending hashtags and post Stories daily.")

        if ig_metrics.get("follower_count", 0) > 0:
            follower_growth = ig_metrics.get("follower_count", 0)
            if follower_growth < 10:
                recommendations.append("Instagram follower growth is slow. Consider running a giveaway or collaboration.")

        if not recommendations:
            recommendations.append("Your social media performance is good! Continue current strategy and experiment with new content formats.")

        return recommendations[:3]


def get_facebook_instagram_connection() -> Optional[FacebookInstagramConnector]:
    """
    Helper function to get Facebook/Instagram connection using environment variables
    """
    access_token = os.getenv('META_ACCESS_TOKEN', '')
    facebook_page_id = os.getenv('FACEBOOK_PAGE_ID', '')
    instagram_business_account_id = os.getenv('INSTAGRAM_BUSINESS_ACCOUNT_ID', '')

    if not all([access_token, facebook_page_id, instagram_business_account_id]):
        print("Missing Facebook/Instagram credentials. Please set environment variables:")
        print("- META_ACCESS_TOKEN")
        print("- FACEBOOK_PAGE_ID")
        print("- INSTAGRAM_BUSINESS_ACCOUNT_ID")
        return None

    try:
        return FacebookInstagramConnector(access_token, facebook_page_id, instagram_business_account_id)
    except Exception as e:
        print(f"Failed to connect to Facebook/Instagram: {str(e)}")
        return None


if __name__ == "__main__":
    # Example usage
    try:
        connector = get_facebook_instagram_connection()
        
        if connector:
            # Generate summary
            summary = connector.generate_summary(7)
            print(f"\nSocial Media Summary:")
            print(f"Period: {summary['period']}")
            print(f"Facebook Insights: {summary['facebook']['insights']}")
            print(f"Instagram Insights: {summary['instagram']['insights']}")
            print(f"Recommendations: {summary['recommendations']}")

    except Exception as e:
        print(f"Could not connect to Facebook/Instagram: {str(e)}")
