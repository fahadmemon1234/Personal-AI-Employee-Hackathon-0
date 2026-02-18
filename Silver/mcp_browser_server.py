"""
MCP Browser Server
Implements a working MCP server for web browsing, scraping, and social media automation
Port: 8081
"""

import json
import asyncio
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime
import re

try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    print("Playwright not installed. Run: pip install playwright && playwright install chromium")
    PLAYWRIGHT_AVAILABLE = False


class MCPBrowserServer:
    """MCP Server for web browsing and automation tasks"""

    def __init__(self, host='localhost', port=8081, headless=True):
        self.host = host
        self.port = port
        self.headless = headless
        self.browser = None
        self.context = None
        self.page = None
        self.playwright = None

        # Directories for saving scraped content
        self.scraped_dir = Path("Scraped_Content")
        self.scraped_dir.mkdir(exist_ok=True)

    async def initialize(self):
        """Initialize Playwright browser"""
        if not PLAYWRIGHT_AVAILABLE:
            print("Playwright not available. Browser features will be limited.")
            return False

        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(headless=self.headless)
            self.context = await self.browser.new_context(
                viewport={'width': 1280, 'height': 800},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            self.page = await self.context.new_page()
            print("Browser initialized successfully")
            return True
        except Exception as e:
            print(f"Failed to initialize browser: {e}")
            return False

    async def browse_web(self, url, timeout=30):
        """Browse to a web page and return content"""
        if not self.page:
            if not await self.initialize():
                return {"success": False, "error": "Browser not available"}

        try:
            await self.page.goto(url, timeout=timeout * 1000, wait_until='domcontentloaded')
            
            # Get page content
            title = await self.page.title()
            html = await self.page.content()
            
            # Extract text content
            text = await self.page.evaluate('() => document.body.innerText')
            
            # Save scraped content
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            safe_filename = re.sub(r'[^\w\-_\.]', '_', url[:50])
            content_file = self.scraped_dir / f"{safe_filename}_{timestamp}.md"
            
            with open(content_file, 'w', encoding='utf-8') as f:
                f.write(f"# Scraped Content\n\n")
                f.write(f"**URL:** {url}\n")
                f.write(f"**Title:** {title}\n")
                f.write(f"**Timestamp:** {datetime.now().isoformat()}\n\n")
                f.write(f"## Content\n\n{text[:10000]}\n")  # Limit to 10k chars
            
            return {
                "success": True,
                "url": url,
                "title": title,
                "text_length": len(text),
                "content_file": str(content_file),
                "preview": text[:500] if len(text) > 500 else text
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def scrape_content(self, url, selector=None):
        """Scrape specific content from a web page"""
        if not self.page:
            if not await self.initialize():
                return {"success": False, "error": "Browser not available"}

        try:
            await self.page.goto(url, timeout=30000, wait_until='domcontentloaded')
            
            if selector:
                # Scrape specific element
                element = await self.page.query_selector(selector)
                if element:
                    content = await element.inner_text()
                else:
                    return {"success": False, "error": f"Selector '{selector}' not found"}
            else:
                # Scrape all text
                content = await self.page.evaluate('() => document.body.innerText')
            
            return {
                "success": True,
                "url": url,
                "selector": selector,
                "content": content
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def automate_browser(self, actions):
        """Execute a series of browser automation actions"""
        if not self.page:
            if not await self.initialize():
                return {"success": False, "error": "Browser not available"}

        results = []
        
        try:
            for action in actions:
                action_type = action.get('type')
                
                if action_type == 'navigate':
                    await self.page.goto(action.get('url'), timeout=30000)
                    results.append({"action": "navigate", "success": True})
                    
                elif action_type == 'click':
                    selector = action.get('selector')
                    await self.page.click(selector)
                    results.append({"action": "click", "selector": selector, "success": True})
                    
                elif action_type == 'fill':
                    selector = action.get('selector')
                    value = action.get('value')
                    await self.page.fill(selector, value)
                    results.append({"action": "fill", "selector": selector, "success": True})
                    
                elif action_type == 'screenshot':
                    filename = action.get('filename', f'screenshot_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png')
                    await self.page.screenshot(path=str(Path(filename)))
                    results.append({"action": "screenshot", "filename": filename, "success": True})
                    
                elif action_type == 'wait':
                    timeout = action.get('timeout', 1000)
                    await asyncio.sleep(timeout / 1000)
                    results.append({"action": "wait", "timeout": timeout, "success": True})
                    
                elif action_type == 'evaluate':
                    script = action.get('script')
                    result = await self.page.evaluate(script)
                    results.append({"action": "evaluate", "result": result, "success": True})
                    
                else:
                    results.append({"action": action_type, "success": False, "error": f"Unknown action type: {action_type}"})
            
            return {
                "success": True,
                "results": results
            }
        except Exception as e:
            return {"success": False, "error": str(e), "results": results}

    async def social_media_post(self, platform, content, credentials=None):
        """Post content to social media platforms"""
        if not self.page:
            if not await self.initialize():
                return {"success": False, "error": "Browser not available"}

        try:
            if platform.lower() == 'linkedin':
                # Navigate to LinkedIn
                await self.page.goto('https://www.linkedin.com', timeout=30000)
                await asyncio.sleep(3)  # Wait for page to load
                
                # Check if logged in (simplified check)
                is_logged_in = 'feed' in self.page.url.lower() or 'mynetwork' in self.page.url.lower()
                
                if not is_logged_in:
                    return {
                        "success": False,
                        "error": "Not logged in to LinkedIn. Please log in manually.",
                        "login_url": "https://www.linkedin.com/login"
                    }
                
                # For security, we don't automate posting without explicit user action
                # Instead, save the post content for manual review
                post_file = self.scraped_dir / f"linkedin_post_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
                
                with open(post_file, 'w', encoding='utf-8') as f:
                    f.write(f"# LinkedIn Post Draft\n\n")
                    f.write(f"**Platform:** LinkedIn\n")
                    f.write(f"**Created:** {datetime.now().isoformat()}\n\n")
                    f.write(f"## Post Content\n\n{content}\n\n")
                    f.write(f"\n**Status:** Ready for manual posting\n")
                    f.write(f"**Instructions:**\n")
                    f.write(f"1. Go to https://www.linkedin.com\n")
                    f.write(f"2. Click 'Start a post'\n")
                    f.write(f"3. Copy and paste the content above\n")
                    f.write(f"4. Review and post\n")
                
                return {
                    "success": True,
                    "platform": platform,
                    "message": "Post draft created (manual posting required for security)",
                    "draft_file": str(post_file),
                    "content": content
                }
                
            elif platform.lower() == 'twitter' or platform.lower() == 'x':
                # Similar approach for Twitter/X
                post_file = self.scraped_dir / f"twitter_post_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
                
                with open(post_file, 'w', encoding='utf-8') as f:
                    f.write(f"# Twitter/X Post Draft\n\n")
                    f.write(f"**Platform:** Twitter/X\n")
                    f.write(f"**Created:** {datetime.now().isoformat()}\n\n")
                    f.write(f"## Post Content\n\n{content}\n\n")
                    f.write(f"\n**Status:** Ready for manual posting\n")
                
                return {
                    "success": True,
                    "platform": platform,
                    "message": "Post draft created (manual posting required for security)",
                    "draft_file": str(post_file)
                }
            else:
                return {"success": False, "error": f"Unsupported platform: {platform}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def web_interaction(self, url, interaction_type, selector=None, value=None):
        """Perform a specific web interaction"""
        if not self.page:
            if not await self.initialize():
                return {"success": False, "error": "Browser not available"}

        try:
            await self.page.goto(url, timeout=30000)
            
            result = {
                "success": True,
                "url": url,
                "interaction": interaction_type
            }
            
            if interaction_type == 'click':
                await self.page.click(selector)
                result["selector"] = selector
                
            elif interaction_type == 'fill':
                await self.page.fill(selector, value)
                result["selector"] = selector
                result["value"] = value
                
            elif interaction_type == 'hover':
                await self.page.hover(selector)
                result["selector"] = selector
                
            elif interaction_type == 'select':
                await self.page.select_option(selector, value)
                result["selector"] = selector
                result["value"] = value
                
            elif interaction_type == 'checkbox':
                if value:
                    await self.page.check(selector)
                else:
                    await self.page.uncheck(selector)
                result["selector"] = selector
                
            elif interaction_type == 'scroll':
                scroll_amount = value or 500
                await self.page.evaluate(f'window.scrollBy(0, {scroll_amount})')
                result["scroll_amount"] = scroll_amount
                
            else:
                result["success"] = False
                result["error"] = f"Unknown interaction type: {interaction_type}"
            
            return result
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def close(self):
        """Close the browser"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()


class MCPBrowserRequestHandler(BaseHTTPRequestHandler):
    """HTTP Request Handler for MCP Browser Server"""

    server_instance = None
    event_loop = None

    def _set_headers(self, status=200, content_type='application/json'):
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers()

    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        if path == '/health':
            self._set_headers()
            self.wfile.write(json.dumps({
                "status": "healthy",
                "server": "MCP Browser Server",
                "port": self.server_instance.port,
                "browser_available": PLAYWRIGHT_AVAILABLE,
                "timestamp": datetime.now().isoformat()
            }).encode())

        elif path == '/capabilities':
            self._set_headers()
            self.wfile.write(json.dumps({
                "capabilities": [
                    "browse-web",
                    "scrape-content",
                    "automate-browser",
                    "social-media-post",
                    "web-interaction"
                ],
                "playwright_available": PLAYWRIGHT_AVAILABLE,
                "headless": self.server_instance.headless
            }).encode())

        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode())

    def do_POST(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')

        try:
            data = json.loads(body) if body else {}
        except json.JSONDecodeError:
            self._set_headers(400)
            self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode())
            return

        # Run async operations in event loop
        if not self.event_loop:
            self.event_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.event_loop)

        if path == '/browse':
            url = data.get('url')
            timeout = data.get('timeout', 30)
            
            if not url:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Missing 'url' field"}).encode())
                return

            result = self.event_loop.run_until_complete(
                self.server_instance.browse_web(url, timeout)
            )
            self._set_headers(200 if result['success'] else 500)
            self.wfile.write(json.dumps(result).encode())

        elif path == '/scrape':
            url = data.get('url')
            selector = data.get('selector')
            
            if not url:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Missing 'url' field"}).encode())
                return

            result = self.event_loop.run_until_complete(
                self.server_instance.scrape_content(url, selector)
            )
            self._set_headers(200 if result['success'] else 500)
            self.wfile.write(json.dumps(result).encode())

        elif path == '/automate':
            actions = data.get('actions', [])
            
            result = self.event_loop.run_until_complete(
                self.server_instance.automate_browser(actions)
            )
            self._set_headers(200 if result['success'] else 500)
            self.wfile.write(json.dumps(result).encode())

        elif path == '/social/post':
            platform = data.get('platform')
            content = data.get('content', '')
            
            if not platform:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Missing 'platform' field"}).encode())
                return

            result = self.event_loop.run_until_complete(
                self.server_instance.social_media_post(platform, content)
            )
            self._set_headers(200 if result['success'] else 500)
            self.wfile.write(json.dumps(result).encode())

        elif path == '/interact':
            url = data.get('url')
            interaction_type = data.get('type')
            selector = data.get('selector')
            value = data.get('value')
            
            if not url or not interaction_type:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Missing 'url' or 'type' field"}).encode())
                return

            result = self.event_loop.run_until_complete(
                self.server_instance.web_interaction(url, interaction_type, selector, value)
            )
            self._set_headers(200 if result['success'] else 500)
            self.wfile.write(json.dumps(result).encode())

        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode())

    def log_message(self, format, *args):
        print(f"[MCP Browser Server] {args[0]}")


def run_mcp_browser_server(host='localhost', port=8081, headless=True):
    """Run the MCP Browser Server"""
    server = MCPBrowserServer(host=host, port=port, headless=headless)
    MCPBrowserRequestHandler.server_instance = server

    # Initialize browser
    if PLAYWRIGHT_AVAILABLE:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(server.initialize())
        MCPBrowserRequestHandler.event_loop = loop

    httpd = HTTPServer((host, port), MCPBrowserRequestHandler)
    print(f"MCP Browser Server running on http://{host}:{port}")
    print(f"Capabilities: browse-web, scrape-content, automate-browser, social-media-post, web-interaction")
    print(f"Headless Mode: {headless}")
    print(f"Press Ctrl+C to stop")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down MCP Browser Server...")
        if server.browser:
            loop.run_until_complete(server.close())
        httpd.shutdown()


if __name__ == "__main__":
    run_mcp_browser_server()
