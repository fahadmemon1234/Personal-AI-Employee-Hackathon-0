module.exports = {
  apps: [
    {
      name: "gmail-watcher",
      script: "python",
      args: "./gmail_watcher.py",
      instances: 1,
      autorestart: true,
      watch: false,
      time: true,
      env: {
        NODE_ENV: "production"
      }
    },
    {
      name: "whatsapp-watcher",
      script: "python",
      args: "./whatsapp_watcher.py",
      instances: 1,
      autorestart: true,
      watch: false,
      time: true,
      env: {
        NODE_ENV: "production"
      }
    },
    {
      name: "linkedin-poster",
      script: "python",
      args: "./linkedin_poster.py",
      instances: 1,
      autorestart: true,
      watch: false,
      time: true,
      env: {
        NODE_ENV: "production"
      }
    },
    {
      name: "scheduler",
      script: "python",
      args: "./scheduler.py",
      instances: 1,
      autorestart: true,
      watch: false,
      time: true,
      env: {
        NODE_ENV: "production"
      }
    },
    {
      name: "reasoning-loop",
      script: "python",
      args: "./reasoning_loop.py",
      instances: 1,
      autorestart: true,
      watch: false,
      time: true,
      env: {
        NODE_ENV: "production"
      }
    },
    {
      name: "agent-interface",
      script: "python",
      args: "./agent_interface.py",
      instances: 1,
      autorestart: true,
      watch: false,
      time: true,
      env: {
        NODE_ENV: "production"
      }
    },
    {
      name: "odoo-mcp-server",
      script: "python",
      args: "./odoo_integration/mcp_server.py",
      instances: 1,
      autorestart: true,
      watch: false,
      time: true,
      env: {
        NODE_ENV: "production"
      }
    },
    {
      name: "twitter-mcp-server",
      script: "python",
      args: "./social_media_integration/twitter_mcp_server.py",
      instances: 1,
      autorestart: true,
      watch: false,
      time: true,
      env: {
        NODE_ENV: "production"
      }
    },
    {
      name: "facebook-instagram-mcp-server",
      script: "python",
      args: "./social_media_integration/facebook_instagram_mcp_server.py",
      instances: 1,
      autorestart: true,
      watch: false,
      time: true,
      env: {
        NODE_ENV: "production"
      }
    },
    {
      name: "ceo-briefing",
      script: "python",
      args: "./ceo_briefing_skill.py",
      instances: 1,
      autorestart: true,
      watch: false,
      time: true,
      env: {
        NODE_ENV: "production"
      }
    }
  ]
};
