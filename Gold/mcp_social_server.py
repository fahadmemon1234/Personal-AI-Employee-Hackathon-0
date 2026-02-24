"""
MCP Social Media Server - Facebook & Instagram Integration
Posts to Meta platforms (Facebook, Instagram) via browser automation or API

Uses Playwright for browser automation when API is not available
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
logger = logging.getLogger('mcp_social_server')

# Flask app for MCP server
app = Flask(__name__)
CORS(app)

# Configuration from environment variables
SOCIAL_CONFIG = {
    'facebook_page_id': os.getenv('FACEBOOK_PAGE_ID', ''),
    'facebook_access_token': os.getenv('FACEBOOK_ACCESS_TOKEN', ''),
    'instagram_account_id': os.getenv('INSTAGRAM_ACCOUNT_ID', ''),
    'instagram_access_token': os.getenv('INSTAGRAM_ACCESS_TOKEN', ''),
    'use_browser_automation': os.getenv('USE_BROWSER_AUTOMATION', 'true').lower() == 'true',
    'dry_run': os.getenv('SOCIAL_DRY_RUN', 'true').lower() == 'true',
}

# Posts storage (for summary generation)
POSTS_LOG = Path('Posts_Log.json')
BRIEFINGS_DIR = Path('Briefings')

# Create directories
BRIEFINGS_DIR.mkdir(exist_ok=True)


class MetaBrowserAutomation:
    """Browser automation for Meta platforms (Facebook/Instagram)"""
    
    def __init__(self):
        self.driver = None
        self.logged_in = False
        
    def initialize(self):
        """Initialize browser (Playwright)"""
        try:
            from playwright.sync_api import sync_playwright
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(headless=False)
            self.context = self.browser.new_context()
            self.page = self.context.new_page()
            logger.info("Browser initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize browser: {e}")
            return False
    
    def login_facebook(self, email, password):
        """Login to Facebook"""
        try:
            self.page.goto('https://www.facebook.com/login')
            self.page.fill('#email', email)
            self.page.fill('#pass', password)
            self.page.click('button[name="login"]')
            self.page.wait_for_load_state('networkidle')
            self.logged_in = True
            logger.info("Facebook login successful")
            return True
        except Exception as e:
            logger.error(f"Facebook login failed: {e}")
            return False
    
    def post_to_facebook(self, page_id, message, image_path=None):
        """Post to Facebook page via browser"""
        if not self.logged_in:
            return {'success': False, 'error': 'Not logged in'}
        
        try:
            # Navigate to page
            self.page.goto(f'https://www.facebook.com/{page_id}')
            self.page.wait_for_load_state('networkidle')
            
            # Find post creation box
            post_box = self.page.locator('[data-testid="create_post_placeholder"]').first
            if post_box.is_visible():
                post_box.click()
                post_box.fill(message)
                
                # Add image if provided
                if image_path and os.path.exists(image_path):
                    file_input = self.page.locator('input[type="file"]')
                    file_input.set_input_files(image_path)
                
                # Click post button
                post_button = self.page.locator('button[aria-label="Post"]').first
                if post_button.is_enabled():
                    post_button.click()
                    self.page.wait_for_load_state('networkidle')
                    logger.info(f"Posted to Facebook page: {page_id}")
                    return {'success': True, 'message': 'Posted successfully'}
            
            return {'success': False, 'error': 'Could not find post box'}
        except Exception as e:
            logger.error(f"Facebook post failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def post_to_instagram(self, account, caption, media_path=None):
        """Post to Instagram via browser"""
        if not self.logged_in:
            return {'success': False, 'error': 'Not logged in'}
        
        try:
            # Navigate to Instagram
            self.page.goto('https://www.instagram.com/')
            self.page.wait_for_load_state('networkidle')
            
            # Click create post
            self.page.click('svg[aria-label="New post"]')
            
            # Upload media
            if media_path and os.path.exists(media_path):
                file_input = self.page.locator('input[type="file"]').first
                file_input.set_input_files(media_path)
                self.page.wait_for_timeout(3000)
                
                # Add caption
                textarea = self.page.locator('textarea')
                if textarea.is_visible():
                    textarea.fill(caption)
                    
                    # Click share
                    share_button = self.page.locator('button:has-text("Share")').first
                    if share_button.is_enabled():
                        share_button.click()
                        self.page.wait_for_load_state('networkidle')
                        logger.info(f"Posted to Instagram: {account}")
                        return {'success': True, 'message': 'Posted successfully'}
            
            return {'success': False, 'error': 'Could not complete post'}
        except Exception as e:
            logger.error(f"Instagram post failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def close(self):
        """Close browser"""
        if hasattr(self, 'browser'):
            self.browser.close()
        if hasattr(self, 'playwright'):
            self.playwright.stop()


class MetaAPI:
    """Meta Graph API for Facebook/Instagram posting"""
    
    def __init__(self, access_token):
        self.access_token = access_token
        self.base_url = 'https://graph.facebook.com/v18.0'
    
    def post_to_facebook(self, page_id, message, image_path=None):
        """Post to Facebook page via Graph API"""
        import requests
        
        url = f"{self.base_url}/{page_id}/feed"
        params = {
            'message': message,
            'access_token': self.access_token
        }
        
        if image_path and os.path.exists(image_path):
            # Upload photo
            url = f"{self.base_url}/{page_id}/photos"
            files = {'source': open(image_path, 'rb')}
            response = requests.post(url, params=params, files=files)
        else:
            response = requests.post(url, params=params)
        
        result = response.json()
        
        if 'id' in result:
            return {'success': True, 'post_id': result['id']}
        else:
            return {'success': False, 'error': result.get('error', {}).get('message', 'Unknown error')}
    
    def post_to_instagram(self, account_id, caption, media_path=None):
        """Post to Instagram via Graph API"""
        import requests
        
        if not media_path:
            return {'success': False, 'error': 'Instagram requires media'}
        
        # Step 1: Create media container
        container_url = f"{self.base_url}/{account_id}/media"
        container_params = {
            'image_url': f'file://{os.path.abspath(media_path)}',
            'caption': caption,
            'access_token': self.access_token
        }
        
        container_response = requests.post(container_url, params=container_params)
        container_result = container_response.json()
        
        if 'id' not in container_result:
            return {'success': False, 'error': container_result.get('error', {}).get('message', 'Failed to create container')}
        
        creation_id = container_result['id']
        
        # Step 2: Publish media
        publish_url = f"{self.base_url}/{account_id}/media_publish"
        publish_params = {
            'creation_id': creation_id,
            'access_token': self.access_token
        }
        
        publish_response = requests.post(publish_url, params=publish_params)
        publish_result = publish_response.json()
        
        if 'id' in publish_result:
            return {'success': True, 'post_id': publish_result['id']}
        else:
            return {'success': False, 'error': publish_result.get('error', {}).get('message', 'Failed to publish')}


# Initialize automation client
browser_automation = MetaBrowserAutomation()
api_client = None

if SOCIAL_CONFIG.get('facebook_access_token'):
    api_client = MetaAPI(SOCIAL_CONFIG['facebook_access_token'])


def log_post(platform, content, result):
    """Log post to JSON file for summary generation"""
    posts = []
    if POSTS_LOG.exists():
        try:
            with open(POSTS_LOG, 'r', encoding='utf-8') as f:
                posts = json.load(f)
        except:
            posts = []
    
    posts.append({
        'timestamp': datetime.now().isoformat(),
        'platform': platform,
        'content': content,
        'result': result
    })
    
    with open(POSTS_LOG, 'w', encoding='utf-8') as f:
        json.dump(posts, f, indent=2, ensure_ascii=False)


def generate_summary_data():
    """Generate summary from posts log"""
    posts = []
    if POSTS_LOG.exists():
        try:
            with open(POSTS_LOG, 'r') as f:
                posts = json.load(f)
        except:
            posts = []
    
    # Filter last 7 days
    week_ago = datetime.now() - timedelta(days=7)
    recent_posts = [
        p for p in posts 
        if datetime.fromisoformat(p['timestamp']) > week_ago
    ]
    
    # Count by platform
    facebook_posts = len([p for p in recent_posts if p['platform'] == 'facebook'])
    instagram_posts = len([p for p in recent_posts if p['platform'] == 'instagram'])
    
    # Success rate
    successful = len([p for p in recent_posts if p['result'].get('success')])
    total = len(recent_posts)
    
    return {
        'period': f"{(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')} to {datetime.now().strftime('%Y-%m-%d')}",
        'total_posts': total,
        'facebook_posts': facebook_posts,
        'instagram_posts': instagram_posts,
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
        'service': 'mcp-social-server',
        'facebook_configured': bool(SOCIAL_CONFIG.get('facebook_page_id')),
        'instagram_configured': bool(SOCIAL_CONFIG.get('instagram_account_id')),
        'dry_run': SOCIAL_CONFIG.get('dry_run', True),
        'browser_automation': SOCIAL_CONFIG.get('use_browser_automation', True),
        'timestamp': datetime.now().isoformat()
    })


@app.route('/webhook/instagram', methods=['GET', 'POST'])
def instagram_webhook():
    """
    Instagram Webhook for real-time notifications
    Meta will send verification request (GET) and events (POST)
    """
    # Verification request from Meta (GET)
    if request.method == 'GET':
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        
        # Check mode and token
        if mode == 'subscribe' and token == SOCIAL_CONFIG.get('webhook_verify_token', 'IGAAc0Y32nQHpBZAFpsdVk5M3VXXzlnRUhXd3FRbHhncHcwdGRfVjZAUZA0p3ZAVl1c01yU1ZA4dlhlTFZAUS2VPcGVKa1dQUVFGMmtNY2RKU293LV9NVUplcHlJbDJuSlhVemx2NFdBdVhuSGFUcXpvSzZA3RTQ3b2FrWkx0YTM4OVlyOAZDZD'):
            logger.info("Webhook verified successfully!")
            return challenge, 200
        else:
            logger.warning(f"Webhook verification failed. Mode: {mode}, Token: {token}")
            return 'Forbidden', 403
    
    # Event notification (POST)
    elif request.method == 'POST':
        data = request.get_json()
        logger.info(f"Webhook event received: {json.dumps(data, indent=2)}")
        
        # Process the event (save to log, trigger actions, etc.)
        if data:
            # Save webhook events to file
            webhook_log = BRIEFINGS_DIR / 'webhook_events.json'
            events = []
            if webhook_log.exists():
                try:
                    with open(webhook_log, 'r', encoding='utf-8') as f:
                        events = json.load(f)
                except:
                    events = []
            
            events.append({
                'timestamp': datetime.now().isoformat(),
                'event': data
            })
            
            with open(webhook_log, 'w', encoding='utf-8') as f:
                json.dump(events[-100:], f, indent=2)  # Keep last 100 events
        
        return 'OK', 200


@app.route('/auth/callback', methods=['GET', 'POST'])
def auth_callback():
    """
    OAuth callback endpoint for Instagram/Facebook login
    """
    if request.method == 'GET':
        code = request.args.get('code')
        error = request.args.get('error')
        
        if error:
            return jsonify({'success': False, 'error': error})
        
        if code:
            # Exchange code for token (implement token exchange)
            logger.info(f"OAuth code received: {code[:20]}...")
            return jsonify({'success': True, 'code': code})
        
        return jsonify({'success': False, 'error': 'No code provided'})
    
    elif request.method == 'POST':
        data = request.get_json()
        logger.info(f"OAuth callback: {json.dumps(data, indent=2)}")
        return jsonify({'success': True})


@app.route('/tools/post_to_facebook', methods=['POST'])
def post_to_facebook():
    """
    Post to Facebook page
    
    Request JSON:
    {
        "page_id": "your_page_id",
        "message": "Post content here",
        "image_path": "path/to/image.jpg",  # Optional
        "dry_run": true  # Optional, default from config
    }
    
    Response:
    {
        "success": true,
        "post_id": "12345",
        "message": "Posted successfully",
        "dry_run": true
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        page_id = data.get('page_id', SOCIAL_CONFIG.get('facebook_page_id'))
        message = data.get('message', '')
        image_path = data.get('image_path')
        dry_run = data.get('dry_run', SOCIAL_CONFIG.get('dry_run', True))
        
        if not page_id:
            return jsonify({'success': False, 'error': 'page_id is required'}), 400
        
        if not message:
            return jsonify({'success': False, 'error': 'message is required'}), 400
        
        # Dry run mode
        if dry_run:
            logger.info(f"[DRY RUN] Would post to Facebook: {message[:50]}...")
            result = {
                'success': True,
                'dry_run': True,
                'message': f'[DRY RUN] Would post: "{message[:100]}..."',
                'page_id': page_id
            }
            log_post('facebook', {'message': message, 'page_id': page_id}, result)
            return jsonify(result)

        # Real posting - Direct Graph API call
        access_token = SOCIAL_CONFIG.get('facebook_access_token', '')
        if access_token:
            import requests as req
            url = f"https://graph.facebook.com/v18.0/{page_id}/feed"
            params = {
                'message': message,
                'access_token': access_token
            }
            if image_path:
                url = f"https://graph.facebook.com/v18.0/{page_id}/photos"
                files = {'source': open(image_path, 'rb')}
                resp = req.post(url, params=params, files=files, timeout=30)
            else:
                resp = req.post(url, params=params, timeout=30)
            
            api_result = resp.json()
            
            if 'id' in api_result:
                result = {'success': True, 'post_id': api_result['id'], 'message': 'Posted via Graph API'}
                log_post('facebook', {'message': message, 'page_id': page_id}, result)
                return jsonify(result)
            else:
                error_msg = api_result.get('error', {}).get('message', 'Unknown API error')
                return jsonify({'success': False, 'error': error_msg})
        else:
            return jsonify({'success': False, 'error': 'No Facebook access token configured'})
        
    except Exception as e:
        logger.error(f"Error posting to Facebook: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/tools/post_to_instagram', methods=['POST'])
def post_to_instagram():
    """
    Post to Instagram account
    
    Request JSON:
    {
        "account_id": "your_account_id",
        "caption": "Post caption here",
        "media_path": "path/to/image.jpg",  # Required for Instagram
        "dry_run": true  # Optional
    }
    
    Response:
    {
        "success": true,
        "post_id": "12345",
        "message": "Posted successfully"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        account_id = data.get('account_id', SOCIAL_CONFIG.get('instagram_account_id'))
        caption = data.get('caption', '')
        media_path = data.get('media_path')
        dry_run = data.get('dry_run', SOCIAL_CONFIG.get('dry_run', True))
        
        if not account_id:
            return jsonify({'success': False, 'error': 'account_id is required'}), 400
        
        if not caption:
            return jsonify({'success': False, 'error': 'caption is required'}), 400
        
        # Instagram requires either image_url or media_path
        if not data.get('image_url') and not data.get('media_path'):
            return jsonify({'success': False, 'error': 'image_url or media_path is required for Instagram'}), 400
        
        # Dry run mode
        if dry_run:
            logger.info(f"[DRY RUN] Would post to Instagram: {caption[:50]}...")
            result = {
                'success': True,
                'dry_run': True,
                'message': f'[DRY RUN] Would post: "{caption[:100]}..."',
                'account_id': account_id
            }
            log_post('instagram', {'caption': caption, 'account_id': account_id}, result)
            return jsonify(result)
        
        # Use API for Instagram
        if SOCIAL_CONFIG.get('instagram_access_token'):
            import requests as req
            access_token = SOCIAL_CONFIG.get('instagram_access_token')
            
            # Get image URL or media path
            image_url = data.get('image_url')
            media_path = data.get('media_path')
            
            if not image_url and not media_path:
                return jsonify({'success': False, 'error': 'image_url or media_path is required for Instagram'}), 400
            
            # Use image_url if provided, otherwise use media_path
            media_url = image_url if image_url else f'file://{media_path}'
            
            # Step 1: Create media container
            container_url = f"https://graph.facebook.com/v18.0/{account_id}/media"
            container_params = {
                'image_url': media_url,
                'caption': caption,
                'access_token': access_token
            }
            
            try:
                container_resp = req.post(container_url, params=container_params, timeout=30)
                container_result = container_resp.json()
                
                if 'id' not in container_result:
                    error_msg = container_result.get('error', {}).get('message', 'Failed to create media container')
                    return jsonify({'success': False, 'error': error_msg})
                
                creation_id = container_result['id']
                
                # Step 2: Publish media
                publish_url = f"https://graph.facebook.com/v18.0/{account_id}/media_publish"
                publish_params = {
                    'creation_id': creation_id,
                    'access_token': access_token
                }
                
                publish_resp = req.post(publish_url, params=publish_params, timeout=30)
                publish_result = publish_resp.json()
                
                if 'id' in publish_result:
                    result = {'success': True, 'post_id': publish_result['id'], 'message': 'Posted to Instagram'}
                    log_post('instagram', {'caption': caption, 'account_id': account_id}, result)
                    return jsonify(result)
                else:
                    error_msg = publish_result.get('error', {}).get('message', 'Failed to publish')
                    return jsonify({'success': False, 'error': error_msg})
                    
            except Exception as e:
                return jsonify({'success': False, 'error': f'Instagram API Error: {str(e)}'})
        else:
            return jsonify({
                'success': False,
                'error': 'Instagram API not configured'
            }), 400
        
        log_post('instagram', {'caption': caption, 'account_id': account_id}, result)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error posting to Instagram: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/tools/generate_summary', methods=['GET'])
def generate_summary():
    """
    Generate weekly summary of social media activity
    
    Response:
    {
        "success": true,
        "summary": {
            "period": "2026-02-16 to 2026-02-23",
            "total_posts": 10,
            "facebook_posts": 6,
            "instagram_posts": 4,
            "success_rate": "95%"
        }
    }
    """
    try:
        summary = generate_summary_data()
        
        # Save to Briefings folder
        summary_file = BRIEFINGS_DIR / 'meta_summary.md'
        summary_content = f"""# Meta Social Media Summary

**Period:** {summary['period']}

## Overview

| Metric | Value |
|--------|-------|
| Total Posts | {summary['total_posts']} |
| Facebook Posts | {summary['facebook_posts']} |
| Instagram Posts | {summary['instagram_posts']} |
| Successful | {summary['successful_posts']} |
| Failed | {summary['failed_posts']} |
| Success Rate | {summary['success_rate']} |

## Recent Posts

"""
        for post in summary['posts'][-10:]:  # Last 10 posts
            status = 'Success' if post['result'].get('success') else 'Failed'
            summary_content += f"""
### {post['platform'].title()} - {post['timestamp'][:10]}

**Content:** {post['content'].get('message', post['content'].get('caption', 'N/A'))[:200]}

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


@app.route('/tools/list_posts', methods=['GET'])
def list_posts():
    """
    List recent posts
    
    Query Parameters:
    - platform: facebook, instagram, all (default: all)
    - limit: Max results (default: 20)
    """
    try:
        platform = request.args.get('platform', 'all')
        limit = int(request.args.get('limit', 20))
        
        posts = []
        if POSTS_LOG.exists():
            with open(POSTS_LOG, 'r') as f:
                posts = json.load(f)
        
        # Filter by platform
        if platform != 'all':
            posts = [p for p in posts if p['platform'] == platform]
        
        # Limit results
        posts = posts[-limit:]
        
        return jsonify({
            'success': True,
            'count': len(posts),
            'posts': posts
        })
        
    except Exception as e:
        logger.error(f"Error listing posts: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("MCP Social Media Server - Facebook & Instagram")
    print("="*60)
    print(f"\nFacebook Page ID: {SOCIAL_CONFIG.get('facebook_page_id', 'Not configured')}")
    print(f"Instagram Account: {SOCIAL_CONFIG.get('instagram_account_id', 'Not configured')}")
    print(f"Browser Automation: {SOCIAL_CONFIG.get('use_browser_automation', True)}")
    print(f"Dry Run Mode: {SOCIAL_CONFIG.get('dry_run', True)}")
    print("\nAvailable Tools:")
    print("  POST /tools/post_to_facebook  - Post to Facebook page")
    print("  POST /tools/post_to_instagram - Post to Instagram account")
    print("  GET  /tools/generate_summary  - Generate weekly summary")
    print("  GET  /tools/list_posts        - List recent posts")
    print("  GET  /health                  - Health check")
    print("\nStarting server on http://localhost:8083")
    print("="*60 + "\n")
    
    # Run the server
    app.run(host='0.0.0.0', port=8083, debug=False)
