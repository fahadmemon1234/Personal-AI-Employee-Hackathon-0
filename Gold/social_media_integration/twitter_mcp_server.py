"""
Twitter (X) MCP Server
Provides skills to post and analyze Twitter content
"""

import asyncio
import json
from aiohttp import web
from datetime import datetime
from pathlib import Path
import sys

# Add the project root to the path
sys.path.append(str(Path(__file__).parent.parent))

from social_media_integration.twitter_connector import (
    TwitterConnector,
    get_twitter_connection
)


class TwitterMCPServer:
    """MCP Server for Twitter (X) integration"""

    def __init__(self):
        self.app = web.Application()
        self.app.router.add_get('/health', self.health_check)
        self.app.router.add_post('/api/v1/post/tweet', self.post_tweet)
        self.app.router.add_post('/api/v1/post/thread', self.post_thread)
        self.app.router.add_get('/api/v1/metrics/user', self.get_user_metrics)
        self.app.router.add_get('/api/v1/metrics/tweet', self.get_tweet_metrics)
        self.app.router.add_get('/api/v1/summary', self.generate_summary)
        self.connector = None

    async def health_check(self, request):
        """Health check endpoint"""
        return web.json_response({"status": "healthy", "service": "Twitter MCP Server"})

    def _get_connector(self):
        """Get or create connector instance"""
        if not self.connector:
            self.connector = get_twitter_connection()
        return self.connector

    async def post_tweet(self, request):
        """Post a tweet"""
        try:
            data = await request.json()
            text = data.get('text', '')
            media_url = data.get('media_url')

            if not text:
                return web.json_response(
                    {"error": "Text is required"},
                    status=400
                )

            connector = self._get_connector()
            if not connector:
                return web.json_response(
                    {"error": "Could not connect to Twitter. Check credentials."},
                    status=503
                )

            result = connector.post_tweet(text, media_url)

            if result.get('success'):
                return web.json_response({
                    "success": True,
                    "message": "Tweet posted successfully",
                    "data": result
                })
            else:
                return web.json_response({
                    "success": False,
                    "error": result.get('error'),
                    "data": result
                }, status=400)

        except Exception as e:
            return web.json_response(
                {"error": str(e)},
                status=500
            )

    async def post_thread(self, request):
        """Post a thread of tweets"""
        try:
            data = await request.json()
            tweets = data.get('tweets', [])

            if not tweets or not isinstance(tweets, list):
                return web.json_response(
                    {"error": "Tweets array is required"},
                    status=400
                )

            connector = self._get_connector()
            if not connector:
                return web.json_response(
                    {"error": "Could not connect to Twitter. Check credentials."},
                    status=503
                )

            result = connector.post_thread(tweets)

            if result.get('success'):
                return web.json_response({
                    "success": True,
                    "message": f"Thread posted successfully ({result.get('thread_count')} tweets)",
                    "data": result
                })
            else:
                return web.json_response({
                    "success": False,
                    "error": result.get('error'),
                    "data": result
                }, status=400)

        except Exception as e:
            return web.json_response(
                {"error": str(e)},
                status=500
            )

    async def get_user_metrics(self, request):
        """Get user metrics"""
        try:
            username = request.query.get('username')

            connector = self._get_connector()
            if not connector:
                return web.json_response(
                    {"error": "Could not connect to Twitter. Check credentials."},
                    status=503
                )

            metrics = connector.get_user_metrics(username)
            return web.json_response(metrics)

        except Exception as e:
            return web.json_response(
                {"error": str(e)},
                status=500
            )

    async def get_tweet_metrics(self, request):
        """Get tweet metrics"""
        try:
            tweet_id = request.query.get('tweet_id')

            if not tweet_id:
                return web.json_response(
                    {"error": "tweet_id parameter is required"},
                    status=400
                )

            connector = self._get_connector()
            if not connector:
                return web.json_response(
                    {"error": "Could not connect to Twitter. Check credentials."},
                    status=503
                )

            metrics = connector.get_tweet_metrics(tweet_id)
            return web.json_response(metrics)

        except Exception as e:
            return web.json_response(
                {"error": str(e)},
                status=500
            )

    async def generate_summary(self, request):
        """Generate Twitter summary"""
        try:
            days = int(request.query.get('days', 7))

            connector = self._get_connector()
            if not connector:
                return web.json_response(
                    {"error": "Could not connect to Twitter. Check credentials."},
                    status=503
                )

            summary = connector.generate_summary(days)
            return web.json_response(summary)

        except Exception as e:
            return web.json_response(
                {"error": str(e)},
                status=500
            )

    def run(self, host='0.0.0.0', port=8083):
        """Run the MCP server"""
        print(f"Starting Twitter MCP Server on {host}:{port}")
        web.run_app(self.app, host=host, port=port)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Twitter MCP Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8083, help="Port to bind to")

    args = parser.parse_args()

    server = TwitterMCPServer()
    server.run(args.host, args.port)
