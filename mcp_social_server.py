"""
MCP Social Media Server - Facebook & Instagram Integration
Posts to Meta platforms (Facebook, Instagram) via API

Uses Meta Graph API for posting
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
    'dry_run': os.getenv('SOCIAL_DRY_RUN', 'true').lower() == 'true',
}

# Posts storage (for summary generation)
POSTS_LOG = Path('Posts_Log.json')
BRIEFINGS_DIR = Path('Briefings')

# Create directories
BRIEFINGS_DIR.mkdir(exist_ok=True)


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
            with open(POSTS_LOG, 'r', encoding='utf-8') as f:
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
        'timestamp': datetime.now().isoformat()
    })


@app.route('/tools/post_to_facebook', methods=['POST'])
def post_to_facebook():
    """Post to Facebook page"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        page_id = data.get('page_id', SOCIAL_CONFIG.get('facebook_page_id'))
        message = data.get('message', '')
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
    """Post to Instagram account"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        account_id = data.get('account_id', SOCIAL_CONFIG.get('instagram_account_id'))
        caption = data.get('caption', '')
        
        if not account_id:
            return jsonify({'success': False, 'error': 'account_id is required'}), 400
        
        if not caption:
            return jsonify({'success': False, 'error': 'caption is required'}), 400
        
        # Instagram requires either image_url or media_path
        if not data.get('image_url') and not data.get('media_path'):
            return jsonify({'success': False, 'error': 'image_url or media_path is required for Instagram'}), 400
        
        # Dry run mode
        dry_run = data.get('dry_run', SOCIAL_CONFIG.get('dry_run', True))
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
        
    except Exception as e:
        logger.error(f"Error posting to Instagram: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/tools/generate_summary', methods=['GET'])
def generate_summary():
    """Generate weekly summary of social media activity"""
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
    """List recent posts"""
    try:
        platform = request.args.get('platform', 'all')
        limit = int(request.args.get('limit', 20))
        
        posts = []
        if POSTS_LOG.exists():
            with open(POSTS_LOG, 'r', encoding='utf-8') as f:
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
