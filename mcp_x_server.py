"""
MCP X (Twitter) Server - X Posting & Summary Integration
Posts to X (Twitter) via API or browser automation

Uses X API v2 or browser automation for posting
"""

import os
import json
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from pathlib import Path

from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('mcp_x_server')

# Flask app for MCP server
app = Flask(__name__)
CORS(app)

# Configuration from environment variables
X_CONFIG = {
    'api_key': os.getenv('X_API_KEY', ''),
    'api_secret': os.getenv('X_API_SECRET', ''),
    'access_token': os.getenv('X_ACCESS_TOKEN', ''),
    'access_token_secret': os.getenv('X_ACCESS_TOKEN_SECRET', ''),
    'bearer_token': os.getenv('X_BEARER_TOKEN', ''),
    'username': os.getenv('X_USERNAME', ''),
    'use_browser_automation': os.getenv('X_USE_BROWSER', 'false').lower() == 'true',
    'dry_run': os.getenv('X_DRY_RUN', 'true').lower() == 'true',
}

# Posts storage (for summary generation)
X_POSTS_LOG = Path('Posts_Log_X.json')
BRIEFINGS_DIR = Path('Briefings')

# Create directories
BRIEFINGS_DIR.mkdir(exist_ok=True)


def log_post(content, result):
    """Log post to JSON file for summary generation"""
    posts = []
    if X_POSTS_LOG.exists():
        try:
            with open(X_POSTS_LOG, 'r', encoding='utf-8') as f:
                posts = json.load(f)
        except:
            posts = []
    
    posts.append({
        'timestamp': datetime.now().isoformat(),
        'content': content,
        'result': result
    })
    
    with open(X_POSTS_LOG, 'w', encoding='utf-8') as f:
        json.dump(posts, f, indent=2, ensure_ascii=False)


def generate_summary_data():
    """Generate summary from posts log"""
    posts = []
    if X_POSTS_LOG.exists():
        try:
            with open(X_POSTS_LOG, 'r', encoding='utf-8') as f:
                posts = json.load(f)
        except:
            posts = []
    
    # Filter last 7 days
    week_ago = datetime.now() - timedelta(days=7)
    recent_posts = [
        p for p in posts 
        if datetime.fromisoformat(p['timestamp']) > week_ago
    ]
    
    # Count stats
    total = len(recent_posts)
    successful = len([p for p in recent_posts if p['result'].get('success')])
    
    return {
        'period': f"{(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')} to {datetime.now().strftime('%Y-%m-%d')}",
        'total_posts': total,
        'successful_posts': successful,
        'failed_posts': total - successful,
        'success_rate': f"{(successful/total*100) if total > 0 else 0:.1f}%",
        'posts': recent_posts
    }


# ============================================================================
# MCP Tool Endpoints
# ============================================================================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'mcp-x-server',
        'username': X_CONFIG.get('username', 'Not configured'),
        'api_configured': bool(X_CONFIG.get('api_key')),
        'dry_run': X_CONFIG.get('dry_run', True),
        'browser_automation': X_CONFIG.get('use_browser_automation', False),
        'timestamp': datetime.now().isoformat()
    })


@app.route('/tools/post_tweet', methods=['POST'])
def post_tweet():
    """
    Post a tweet to X (Twitter)
    
    Request JSON:
    {
        "text": "Tweet content here",
        "image_path": "path/to/image.jpg",  # Optional
        "dry_run": true  # Optional
    }
    
    Response:
    {
        "success": true,
        "tweet_id": "1234567890",
        "message": "Posted successfully"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        text = data.get('text', '')
        image_path = data.get('image_path')
        dry_run = data.get('dry_run', X_CONFIG.get('dry_run', True))
        
        if not text:
            return jsonify({'success': False, 'error': 'text is required'}), 400
        
        # Check tweet length (X limit is 280 characters)
        if len(text) > 280:
            return jsonify({
                'success': False, 
                'error': f'Tweet too long ({len(text)}/280 characters). Please shorten.'
            }), 400
        
        # Dry run mode
        if dry_run:
            logger.info(f"[DRY RUN] Would post tweet: {text[:50]}...")
            result = {
                'success': True,
                'dry_run': True,
                'message': f'[DRY RUN] Would post: "{text[:100]}..."',
                'character_count': len(text)
            }
            log_post({'text': text, 'image_path': image_path}, result)
            return jsonify(result)
        
        # Real posting - Check if API is configured
        if X_CONFIG.get('access_token') and X_CONFIG.get('access_token_secret'):
            # Use OAuth 1.0a authentication with requests-oauthlib
            try:
                from requests_oauthlib import OAuth1Session
                from oauthlib.oauth1 import SIGNATURE_HMAC, VERSION_1_0
                
                # X API v2 endpoint for creating tweets
                url = "https://api.twitter.com/2/tweets"
                
                # For OAuth 1.0a, we need consumer key (API key) and consumer secret
                # If API secret is not available, we can't use OAuth 1.0a properly
                api_key = X_CONFIG.get('api_key', '')
                api_secret = X_CONFIG.get('api_secret', '')
                
                # Check if we have proper credentials
                if not api_secret or api_secret == 'your_x_api_secret_here':
                    return jsonify({
                        'success': False,
                        'error': 'X_API_SECRET not configured. Please get it from https://developer.twitter.com/en/portal/dashboard'
                    })
                
                # Create OAuth1 session
                oauth = OAuth1Session(
                    api_key,
                    client_secret=api_secret,
                    resource_owner_key=X_CONFIG.get('access_token', ''),
                    resource_owner_secret=X_CONFIG.get('access_token_secret', '')
                )
                
                payload = {
                    'text': text
                }
                
                response = oauth.post(url, json=payload, timeout=30)
                
                # Log full response for debugging
                logger.info(f"X API Response Status: {response.status_code}")
                logger.info(f"X API Response: {response.text}")
                
                if response.status_code in [200, 201]:
                    api_result = response.json()
                    if 'data' in api_result and 'id' in api_result['data']:
                        tweet_id = api_result['data']['id']
                        result = {
                            'success': True,
                            'tweet_id': tweet_id,
                            'message': 'Posted via X API v2 (OAuth 1.0a)',
                            'character_count': len(text)
                        }
                        log_post({'text': text, 'image_path': image_path}, result)
                        return jsonify(result)
                    else:
                        error_msg = f'Unexpected response: {api_result}'
                        return jsonify({'success': False, 'error': error_msg})
                else:
                    try:
                        api_result = response.json()
                        errors = api_result.get('errors', [])
                        if errors:
                            error_msg = errors[0].get('message', str(errors))
                        else:
                            error_msg = f'HTTP {response.status_code}: {api_result}'
                    except:
                        error_msg = f'HTTP {response.status_code}: {response.text}'
                    return jsonify({'success': False, 'error': error_msg})
                    
            except ImportError:
                return jsonify({
                    'success': False,
                    'error': 'requests-oauthlib not installed. Run: pip install requests-oauthlib'
                })
            except Exception as e:
                return jsonify({'success': False, 'error': f'X API Error: {str(e)}'})
        
        elif X_CONFIG.get('bearer_token'):
            # Use Bearer token (only works for read operations usually)
            import requests

            url = "https://api.twitter.com/2/tweets"

            headers = {
                'Authorization': f'Bearer {X_CONFIG.get("bearer_token", "")}',
                'Content-Type': 'application/json'
            }

            payload = {
                'text': text
            }

            try:
                response = requests.post(url, json=payload, headers=headers, timeout=30)
                api_result = response.json()
                
                logger.info(f"X API Response Status: {response.status_code}")
                logger.info(f"X API Response: {api_result}")

                if 'data' in api_result and 'id' in api_result['data']:
                    tweet_id = api_result['data']['id']
                    result = {
                        'success': True,
                        'tweet_id': tweet_id,
                        'message': 'Posted via X API v2',
                        'character_count': len(text)
                    }
                    log_post({'text': text, 'image_path': image_path}, result)
                    return jsonify(result)
                else:
                    errors = api_result.get('errors', [])
                    if errors:
                        error_msg = errors[0].get('message', str(errors))
                    else:
                        error_msg = f'HTTP {response.status_code}: {api_result}'
                    return jsonify({'success': False, 'error': error_msg})

            except Exception as e:
                return jsonify({'success': False, 'error': f'X API Error: {str(e)}'})
        
        elif X_CONFIG.get('use_browser_automation'):
            # Browser automation (requires login credentials)
            return jsonify({
                'success': False, 
                'error': 'Browser automation not yet implemented. Please use X API.'
            }), 400
        
        else:
            return jsonify({
                'success': False, 
                'error': 'X API not configured. Set X_API_KEY and X_API_SECRET in .env'
            }), 400
        
    except Exception as e:
        logger.error(f"Error posting tweet: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/tools/get_recent_posts', methods=['GET'])
def get_recent_posts():
    """
    Get recent posts/tweets
    
    Query Parameters:
    - limit: Max results (default: 10, max: 100)
    
    Response:
    {
        "success": true,
        "count": 10,
        "posts": [...]
    }
    """
    try:
        limit = int(request.args.get('limit', 10))
        limit = min(limit, 100)  # Max 100
        
        posts = []
        if X_POSTS_LOG.exists():
            with open(X_POSTS_LOG, 'r', encoding='utf-8') as f:
                posts = json.load(f)
        
        # Get most recent
        recent = posts[-limit:] if len(posts) > limit else posts
        
        return jsonify({
            'success': True,
            'count': len(recent),
            'posts': recent
        })
        
    except Exception as e:
        logger.error(f"Error getting recent posts: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/tools/generate_x_summary', methods=['GET'])
def generate_x_summary():
    """
    Generate weekly summary of X activity
    
    Response:
    {
        "success": true,
        "summary": {
            "period": "2026-02-17 to 2026-02-24",
            "total_posts": 10,
            "success_rate": "95%"
        },
        "saved_to": "Briefings/x_weekly.md"
    }
    """
    try:
        summary = generate_summary_data()
        
        # Save to Briefings folder
        summary_file = BRIEFINGS_DIR / 'x_weekly.md'
        summary_content = f"""# X (Twitter) Weekly Summary

**Period:** {summary['period']}

## Overview

| Metric | Value |
|--------|-------|
| Total Posts | {summary['total_posts']} |
| Successful | {summary['successful_posts']} |
| Failed | {summary['failed_posts']} |
| Success Rate | {summary['success_rate']} |

## Recent Posts

"""
        for post in summary['posts'][-10:]:  # Last 10 posts
            timestamp = post.get('timestamp', 'N/A')[:16].replace('T', ' ')
            content = post.get('content', {})
            text = content.get('text', 'N/A')[:200]
            status = '✅ Success' if post.get('result', {}).get('success') else '❌ Failed'
            
            summary_content += f"""
### {timestamp}

**Tweet:** {text}

**Status:** {status}

---
"""
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary_content)
        
        return jsonify({
            'success': True,
            'summary': summary,
            'saved_to': str(summary_file)
        })
        
    except Exception as e:
        logger.error(f"Error generating summary: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("MCP X (Twitter) Server - Posting & Summary")
    print("="*60)
    print(f"\nUsername: @{X_CONFIG.get('username', 'Not configured')}")
    print(f"API Configured: {bool(X_CONFIG.get('api_key'))}")
    print(f"Browser Automation: {X_CONFIG.get('use_browser_automation', False)}")
    print(f"Dry Run Mode: {X_CONFIG.get('dry_run', True)}")
    print("\nAvailable Tools:")
    print("  POST /tools/post_tweet        - Post a tweet")
    print("  GET  /tools/get_recent_posts  - Get recent posts")
    print("  GET  /tools/generate_x_summary - Generate weekly summary")
    print("  GET  /health                  - Health check")
    print("\nStarting server on http://localhost:8084")
    print("="*60 + "\n")
    
    # Run the server
    app.run(host='0.0.0.0', port=8084, debug=False)
