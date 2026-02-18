{
  "apps": [
    {
      "name": "gmail-watcher",
      "script": "./gmail_watcher.py",
      "instances": 1,
      "autorestart": true,
      "watch": false,
      "time": true,
      "env": {
        "NODE_ENV": "production"
      }
    },
    {
      "name": "whatsapp-watcher",
      "script": "./agent_interface.py",
      "instances": 1,
      "autorestart": true,
      "watch": false,
      "time": true,
      "env": {
        "NODE_ENV": "production"
      }
    },
    {
      "name": "linkedin-poster",
      "script": "./linkedin_poster.py",
      "instances": 1,
      "autorestart": true,
      "watch": false,
      "time": true,
      "env": {
        "NODE_ENV": "production"
      }
    },
    {
      "name": "scheduler",
      "script": "./scheduler.py",
      "instances": 1,
      "autorestart": true,
      "watch": false,
      "time": true,
      "env": {
        "NODE_ENV": "production"
      }
    },
    {
      "name": "reasoning-loop",
      "script": "./reasoning_loop.py",
      "instances": 1,
      "autorestart": true,
      "watch": false,
      "time": true,
      "env": {
        "NODE_ENV": "production"
      }
    },
    {
      "name": "odoo-mcp-server",
      "script": "./odoo_integration/mcp_server.py",
      "instances": 1,
      "autorestart": true,
      "watch": false,
      "time": true,
      "env": {
        "NODE_ENV": "production"
      }
    },
    {
      "name": "twitter-mcp-server",
      "script": "./social_media_integration/twitter_mcp_server.py",
      "instances": 1,
      "autorestart": true,
      "watch": false,
      "time": true,
      "env": {
        "NODE_ENV": "production"
      }
    },
    {
      "name": "facebook-instagram-mcp-server",
      "script": "./social_media_integration/facebook_instagram_mcp_server.py",
      "instances": 1,
      "autorestart": true,
      "watch": false,
      "time": true,
      "env": {
        "NODE_ENV": "production"
      }
    },
    {
      "name": "ceo-briefing",
      "script": "./ceo_briefing_skill.py",
      "instances": 1,
      "autorestart": true,
      "watch": false,
      "time": true,
      "env": {
        "NODE_ENV": "production"
      }
    }
  ]
}