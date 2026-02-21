"""
twitter_connector.py
Connector for Twitter (X) using Twitter API v2
"""

import requests
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import base64


class TwitterConnector:
    """
    Connector class for interacting with Twitter (X) via Twitter API v2
    """

    def __init__(self, api_key: str, api_secret: str, access_token: str, access_token_secret: str):
        """
        Initialize the Twitter connector

        Args:
            api_key: Twitter API Key
            api_secret: Twitter API Secret
            access_token: Twitter Access Token
            access_token_secret: Twitter Access Token Secret
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        self.base_url = "https://api.twitter.com"
        self.bearer_token = None
        
        # Authenticate and get bearer token
        self._authenticate()

    def _authenticate(self):
        """Authenticate and get bearer token"""
        try:
            key_secret = f"{self.api_key}:{self.api_secret}".encode('ascii')
            b64_encoded_key = base64.b64encode(key_secret).decode('ascii')

            url = "https://api.twitter.com/oauth2/token"
            headers = {
                "Authorization": f"Basic {b64_encoded_key}",
                "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"
            }
            data = {"grant_type": "client_credentials"}

            response = requests.post(url, headers=headers, data=data, timeout=30)
            result = response.json()

            if response.status_code == 200:
                self.bearer_token = result.get("access_token")
                print(f"Twitter authentication successful")
            else:
                print(f"Twitter authentication failed: {result}")
                raise Exception(f"Twitter auth failed: {result.get('error', 'Unknown error')}")

        except Exception as e:
            print(f"Error authenticating with Twitter: {str(e)}")
            raise

    def _get_auth_headers(self) -> Dict:
        """Get authentication headers for API requests"""
        return {
            "Authorization": f"Bearer {self.bearer_token}",
            "Content-Type": "application/json"
        }

    def post_tweet(self, text: str, media_url: str = None) -> Dict:
        """
        Post a tweet to Twitter

        Args:
            text: The tweet text (max 280 characters)
            media_url: Optional media URL to attach

        Returns:
            Dict with tweet_id and status
        """
        try:
            # Check text length
            if len(text) > 280:
                return {
                    "success": False,
                    "error": "Tweet text must be 280 characters or less",
                    "platform": "twitter"
                }

            endpoint = f"{self.base_url}/2/tweets"
            
            payload = {"text": text}

            # Note: Media upload requires additional steps with Twitter API v2
            # This is a simplified version - full implementation would upload media first
            
            response = requests.post(endpoint, headers=self._get_auth_headers(), 
                                   json=payload, timeout=30)
            result = response.json()

            if response.status_code == 201 and "data" in result:
                tweet_id = result["data"]["id"]
                print(f"Tweet posted successfully: {tweet_id}")
                return {
                    "success": True,
                    "tweet_id": tweet_id,
                    "platform": "twitter",
                    "text": text,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                print(f"Tweet post failed: {result}")
                return {
                    "success": False,
                    "error": result.get("error", {}).get("message", "Unknown error"),
                    "platform": "twitter"
                }

        except Exception as e:
            print(f"Error posting tweet: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "platform": "twitter"
            }

    def post_thread(self, tweets: List[str]) -> Dict:
        """
        Post a thread of tweets

        Args:
            tweets: List of tweet texts

        Returns:
            Dict with tweet IDs and status
        """
        try:
            tweet_ids = []
            
            for i, tweet_text in enumerate(tweets):
                result = self.post_tweet(tweet_text)
                
                if result.get("success"):
                    tweet_ids.append(result["tweet_id"])
                else:
                    return {
                        "success": False,
                        "error": f"Failed at tweet {i+1}: {result.get('error')}",
                        "posted_count": len(tweet_ids),
                        "platform": "twitter"
                    }

            print(f"Thread posted successfully: {len(tweet_ids)} tweets")
            return {
                "success": True,
                "tweet_ids": tweet_ids,
                "thread_count": len(tweet_ids),
                "platform": "twitter",
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            print(f"Error posting thread: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "platform": "twitter"
            }

    def get_user_metrics(self, username: str = None) -> Dict:
        """
        Get user account metrics

        Args:
            username: Twitter username (without @)

        Returns:
            Dict with user metrics
        """
        try:
            # Get user ID first
            if username:
                user_url = f"{self.base_url}/2/users/by/username/{username}"
            else:
                # Get authenticated user
                user_url = f"{self.base_url}/2/users/me"

            user_response = requests.get(user_url, headers=self._get_auth_headers(), timeout=30)
            user_result = user_response.json()

            if user_response.status_code != 200:
                return {
                    "platform": "twitter",
                    "error": user_result.get("error", "Failed to get user info")
                }

            user_id = user_result["data"]["id"]

            # Get user metrics
            metrics_url = f"{self.base_url}/2/users/{user_id}"
            params = {
                "user.fields": "public_metrics,created_at,description"
            }

            metrics_response = requests.get(metrics_url, headers=self._get_auth_headers(), 
                                          params=params, timeout=30)
            metrics_result = metrics_response.json()

            if metrics_response.status_code == 200:
                user_data = metrics_result.get("data", {})
                public_metrics = user_data.get("public_metrics", {})

                return {
                    "platform": "twitter",
                    "username": user_data.get("username"),
                    "metrics": {
                        "followers_count": public_metrics.get("followers_count", 0),
                        "following_count": public_metrics.get("following_count", 0),
                        "tweet_count": public_metrics.get("tweet_count", 0),
                        "listed_count": public_metrics.get("listed_count", 0)
                    },
                    "created_at": user_data.get("created_at"),
                    "description": user_data.get("description")
                }
            else:
                return {
                    "platform": "twitter",
                    "error": metrics_result.get("error", "Failed to get metrics")
                }

        except Exception as e:
            print(f"Error getting user metrics: {str(e)}")
            return {
                "platform": "twitter",
                "error": str(e)
            }

    def get_tweet_metrics(self, tweet_id: str) -> Dict:
        """
        Get metrics for a specific tweet

        Args:
            tweet_id: The tweet ID

        Returns:
            Dict with tweet metrics
        """
        try:
            endpoint = f"{self.base_url}/2/tweets/{tweet_id}"
            params = {
                "tweet.fields": "public_metrics,created_at,text"
            }

            response = requests.get(endpoint, headers=self._get_auth_headers(), 
                                  params=params, timeout=30)
            result = response.json()

            if response.status_code == 200 and "data" in result:
                tweet_data = result["data"]
                metrics = tweet_data.get("public_metrics", {})

                return {
                    "platform": "twitter",
                    "tweet_id": tweet_id,
                    "text": tweet_data.get("text", "")[:50],
                    "metrics": {
                        "retweet_count": metrics.get("retweet_count", 0),
                        "reply_count": metrics.get("reply_count", 0),
                        "like_count": metrics.get("like_count", 0),
                        "quote_count": metrics.get("quote_count", 0),
                        "impression_count": metrics.get("impression_count", 0)
                    },
                    "created_at": tweet_data.get("created_at")
                }
            else:
                return {
                    "platform": "twitter",
                    "error": result.get("error", "Failed to get tweet metrics")
                }

        except Exception as e:
            print(f"Error getting tweet metrics: {str(e)}")
            return {
                "platform": "twitter",
                "error": str(e)
            }

    def get_recent_tweets(self, count: int = 10) -> List[Dict]:
        """
        Get recent tweets from authenticated user

        Args:
            count: Number of tweets to retrieve

        Returns:
            List of tweet data
        """
        try:
            # Get user ID
            user_url = f"{self.base_url}/2/users/me"
            user_response = requests.get(user_url, headers=self._get_auth_headers(), timeout=30)
            user_result = user_response.json()

            if user_response.status_code != 200:
                return []

            user_id = user_result["data"]["id"]

            # Get user tweets
            tweets_url = f"{self.base_url}/2/users/{user_id}/tweets"
            params = {
                "max_results": min(count, 100),  # API limit is 100
                "tweet.fields": "public_metrics,created_at,text"
            }

            response = requests.get(tweets_url, headers=self._get_auth_headers(), 
                                  params=params, timeout=30)
            result = response.json()

            if response.status_code == 200 and "data" in result:
                tweets = result.get("data", [])
                print(f"Retrieved {len(tweets)} recent tweets")
                return tweets
            else:
                print(f"Failed to get tweets: {result}")
                return []

        except Exception as e:
            print(f"Error getting recent tweets: {str(e)}")
            return []

    def generate_summary(self, days: int = 7) -> Dict:
        """
        Generate a comprehensive summary of Twitter activity

        Args:
            days: Number of days to summarize

        Returns:
            Dict with combined summary
        """
        user_metrics = self.get_user_metrics()
        recent_tweets = self.get_recent_tweets(10)

        # Calculate engagement from recent tweets
        total_engagement = 0
        total_impressions = 0
        
        for tweet in recent_tweets:
            metrics = tweet.get("public_metrics", {})
            total_engagement += (
                metrics.get("like_count", 0) +
                metrics.get("retweet_count", 0) +
                metrics.get("reply_count", 0) +
                metrics.get("quote_count", 0)
            )
            total_impressions += metrics.get("impression_count", 0)

        summary = {
            "period": f"Last {days} days",
            "generated_at": datetime.now().isoformat(),
            "account": {
                "username": user_metrics.get("username"),
                "followers": user_metrics.get("metrics", {}).get("followers_count", 0),
                "following": user_metrics.get("metrics", {}).get("following_count", 0),
                "total_tweets": user_metrics.get("metrics", {}).get("tweet_count", 0)
            },
            "recent_activity": {
                "tweets_analyzed": len(recent_tweets),
                "total_engagement": total_engagement,
                "total_impressions": total_impressions,
                "avg_engagement_per_tweet": total_engagement / len(recent_tweets) if recent_tweets else 0
            },
            "top_tweets": recent_tweets[:5],
            "recommendations": self._generate_recommendations(user_metrics, recent_tweets)
        }

        return summary

    def _generate_recommendations(self, user_metrics: Dict, recent_tweets: List) -> List[str]:
        """
        Generate recommendations based on metrics
        """
        recommendations = []

        followers = user_metrics.get("metrics", {}).get("followers_count", 0)
        
        # Follower recommendations
        if followers < 100:
            recommendations.append("Focus on growing your audience by engaging with trending topics in your niche.")
        elif followers < 1000:
            recommendations.append("Consider posting more consistently (3-5 times daily) to accelerate growth.")

        # Engagement recommendations
        if recent_tweets:
            avg_engagement = sum(
                t.get("public_metrics", {}).get("like_count", 0) for t in recent_tweets
            ) / len(recent_tweets)
            
            if avg_engagement < 10:
                recommendations.append("Engagement is low. Try asking questions and using relevant hashtags.")
            elif avg_engagement > 50:
                recommendations.append("Great engagement! Continue your current content strategy.")

        # Content recommendations
        if not recommendations:
            recommendations.append("Your Twitter performance is strong. Experiment with threads and media content.")

        return recommendations[:3]


def get_twitter_connection() -> Optional[TwitterConnector]:
    """
    Helper function to get Twitter connection using environment variables
    """
    api_key = os.getenv('TWITTER_API_KEY', '')
    api_secret = os.getenv('TWITTER_API_SECRET', '')
    access_token = os.getenv('TWITTER_ACCESS_TOKEN', '')
    access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET', '')

    if not all([api_key, api_secret, access_token, access_token_secret]):
        print("Missing Twitter credentials. Please set environment variables:")
        print("- TWITTER_API_KEY")
        print("- TWITTER_API_SECRET")
        print("- TWITTER_ACCESS_TOKEN")
        print("- TWITTER_ACCESS_TOKEN_SECRET")
        return None

    try:
        return TwitterConnector(api_key, api_secret, access_token, access_token_secret)
    except Exception as e:
        print(f"Failed to connect to Twitter: {str(e)}")
        return None


if __name__ == "__main__":
    # Example usage
    try:
        connector = get_twitter_connection()
        
        if connector:
            # Generate summary
            summary = connector.generate_summary(7)
            print(f"\nTwitter Summary:")
            print(f"Period: {summary['period']}")
            print(f"Username: {summary['account']['username']}")
            print(f"Followers: {summary['account']['followers']}")
            print(f"Avg Engagement: {summary['recent_activity']['avg_engagement_per_tweet']:.2f}")
            print(f"Recommendations: {summary['recommendations']}")

    except Exception as e:
        print(f"Could not connect to Twitter: {str(e)}")
