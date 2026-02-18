"""
Facebook/Instagram MCP Server
Provides skills to post and analyze Facebook and Instagram content
"""

import asyncio
import json
from aiohttp import web
from datetime import datetime
from pathlib import Path
import sys

# Add the project root to the path
sys.path.append(str(Path(__file__).parent.parent))

from social_media_integration.facebook_instagram_connector import (
    FacebookInstagramConnector,
    get_facebook_instagram_connection
)


class FacebookInstagramMCPServer:
    """MCP Server for Facebook and Instagram integration"""

    def __init__(self):
        self.app = web.Application()
        self.app.router.add_get('/health', self.health_check)
        self.app.router.add_post('/api/v1/post/facebook', self.post_to_facebook)
        self.app.router.add_post('/api/v1/post/instagram', self.post_to_instagram)
        self.app.router.add_get('/api/v1/insights/facebook', self.get_facebook_insights)
        self.app.router.add_get('/api/v1/insights/instagram', self.get_instagram_insights)
        self.app.router.add_get('/api/v1/summary', self.generate_summary)
        self.connector = None

    async def health_check(self, request):
        """Health check endpoint"""
        return web.json_response({"status": "healthy", "service": "Facebook/Instagram MCP Server"})

    def _get_connector(self):
        """Get or create connector instance"""
        if not self.connector:
            self.connector = get_facebook_instagram_connection()
        return self.connector

    async def post_to_facebook(self, request):
        """Post a message to Facebook"""
        try:
            data = await request.json()
            message = data.get('message', '')
            link = data.get('link')
            photo_url = data.get('photo_url')

            if not message:
                return web.json_response(
                    {"error": "Message is required"},
                    status=400
                )

            connector = self._get_connector()
            if not connector:
                return web.json_response(
                    {"error": "Could not connect to Facebook/Instagram. Check credentials."},
                    status=503
                )

            result = connector.post_to_facebook(message, link, photo_url)

            if result.get('success'):
                return web.json_response({
                    "success": True,
                    "message": "Posted to Facebook successfully",
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

    async def post_to_instagram(self, request):
        """Post an image to Instagram"""
        try:
            data = await request.json()
            caption = data.get('caption', '')
            image_url = data.get('image_url')

            if not caption or not image_url:
                return web.json_response(
                    {"error": "Caption and image_url are required"},
                    status=400
                )

            connector = self._get_connector()
            if not connector:
                return web.json_response(
                    {"error": "Could not connect to Facebook/Instagram. Check credentials."},
                    status=503
                )

            result = connector.post_to_instagram(caption, image_url)

            if result.get('success'):
                return web.json_response({
                    "success": True,
                    "message": "Posted to Instagram successfully",
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

    async def get_facebook_insights(self, request):
        """Get Facebook insights"""
        try:
            days = int(request.query.get('days', 7))

            connector = self._get_connector()
            if not connector:
                return web.json_response(
                    {"error": "Could not connect to Facebook/Instagram. Check credentials."},
                    status=503
                )

            insights = connector.get_facebook_insights(days)
            return web.json_response(insights)

        except Exception as e:
            return web.json_response(
                {"error": str(e)},
                status=500
            )

    async def get_instagram_insights(self, request):
        """Get Instagram insights"""
        try:
            days = int(request.query.get('days', 7))

            connector = self._get_connector()
            if not connector:
                return web.json_response(
                    {"error": "Could not connect to Facebook/Instagram. Check credentials."},
                    status=503
                )

            insights = connector.get_instagram_insights(days)
            return web.json_response(insights)

        except Exception as e:
            return web.json_response(
                {"error": str(e)},
                status=500
            )

    async def generate_summary(self, request):
        """Generate combined social media summary"""
        try:
            days = int(request.query.get('days', 7))

            connector = self._get_connector()
            if not connector:
                return web.json_response(
                    {"error": "Could not connect to Facebook/Instagram. Check credentials."},
                    status=503
                )

            summary = connector.generate_summary(days)
            return web.json_response(summary)

        except Exception as e:
            return web.json_response(
                {"error": str(e)},
                status=500
            )

    def run(self, host='0.0.0.0', port=8082):
        """Run the MCP server"""
        print(f"Starting Facebook/Instagram MCP Server on {host}:{port}")
        web.run_app(self.app, host=host, port=port)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Facebook/Instagram MCP Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8082, help="Port to bind to")

    args = parser.parse_args()

    server = FacebookInstagramMCPServer()
    server.run(args.host, args.port)
