# Platinum Tier Deployment Guide

**Oracle Cloud Free Tier - 24/7 Always-On AI Employee**

This guide covers deploying the Platinum Tier AI Employee to Oracle Cloud Free Tier VM with Odoo 19, health monitoring, and Git-based vault sync.

---

## Prerequisites

### Oracle Cloud Account
- Oracle Cloud Free Tier account
- Ampere A1 Compute instances available (4 OCPU, 24 GB RAM)

### Domain & DNS
- Domain name pointed to Oracle Cloud VM public IP
- DNS A record: `cloud.yourdomain.com` → VM public IP

### Local Machine
- Git installed
- Python 3.13+ installed
- SSH client installed

---

## Step 1: Create Oracle Cloud VM

### 1.1 Create Instance

1. **Login to Oracle Cloud Console**
   - Go to https://cloud.oracle.com
   - Navigate to **Compute** → **Instances**

2. **Create Instance**
   - Click **Create Instance**
   - **Name:** `platinum-cloud-agent`
   - **Compartment:** Select your compartment
   - **Availability Domain:** Any available

3. **Image and Shape**
   - **Image:** Ubuntu 24.04 LTS
   - **Shape:** VM.Standard.A1.Flex (Ampere)
   - **OCPUs:** 4
   - **Memory:** 24 GB

4. **Networking**
   - **VCN:** Select default VCN or create new
   - **Subnet:** Public subnet
   - **Assign Public IPv4 Address:** Yes

5. **SSH Keys**
   - **Generate key pair** or **Upload public key**
   - Save private key securely (e.g., `~/.ssh/oracle_cloud_key`)
   - Set permissions: `chmod 400 ~/.ssh/oracle_cloud_key`

6. **Boot Volume**
   - **Size:** 200 GB (minimum for Odoo + data)

7. **Create** the instance

### 1.2 Configure Security List

1. **Navigate to** **Networking** → **Virtual Cloud Networks**
2. **Select your VCN** → **Security Lists**
3. **Add Ingress Rules:**

| Source | Destination | Protocol | Port Range | Purpose |
|--------|-------------|----------|------------|---------|
| 0.0.0.0/0 | All | TCP | 22 | SSH |
| 0.0.0.0/0 | All | TCP | 80 | HTTP (Let's Encrypt) |
| 0.0.0.0/0 | All | TCP | 443 | HTTPS |
| 0.0.0.0/0 | All | TCP | 5000 | Health Monitor |
| 0.0.0.0/0 | All | TCP | 8069 | Odoo |
| 10.0.0.0/24 | All | TCP | 5432 | PostgreSQL (internal) |

---

## Step 2: SSH into VM

```bash
# SSH into VM
ssh -i ~/.ssh/oracle_cloud_key ubuntu@<VM_PUBLIC_IP>

# Test connection
ssh -i ~/.ssh/oracle_cloud_key ubuntu@<VM_PUBLIC_IP> "echo 'Connection successful'"
```

---

## Step 3: Install Dependencies

```bash
#!/bin/bash
# install_dependencies.sh

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.13+
sudo apt install -y software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.13 python3.13-venv python3.13-dev python3-pip

# Install Node.js v24+
curl -fsSL https://deb.nodesource.com/setup_24.x | sudo -E bash -
sudo apt install -y nodejs

# Install Git
sudo apt install -y git

# Install PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Install Nginx
sudo apt install -y nginx

# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Install supervisor
sudo apt install -y supervisor

# Install additional dependencies
sudo apt install -y curl wget build-essential libssl-dev libffi-dev

# Verify installations
python3.13 --version
node --version
npm --version
git --version
psql --version
nginx -v

echo "Dependencies installed successfully!"
```

---

## Step 4: Clone Vault Repository

```bash
# Create platinum user
sudo adduser platinum
sudo usermod -aG sudo platinum

# Switch to platinum user
sudo su - platinum

# Create application directory
mkdir -p /opt/platinum-vault
cd /opt/platinum-vault

# Initialize Git repository (if not already a repo)
git init

# Add remote (your GitHub/GitLab repo)
git remote add origin <YOUR_VAULT_REPO_URL>

# Configure Git
git config --global user.name "Platinum Cloud Agent"
git config --global user.email "cloud@yourdomain.com"

# Pull vault code
git pull origin main

# Create Python virtual environment
python3.13 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Install additional Python packages
pip install flask python-dotenv requests
```

---

## Step 5: Configure Environment

```bash
# Create .env.cloud (NEVER commit this file)
cat > /opt/platinum-vault/.env.cloud << 'EOF'
# Platinum Cloud Environment
AGENT_TYPE=cloud
DRAFT_ONLY_MODE=true
VAULT_PATH=/opt/platinum-vault

# Odoo Configuration
ODOO_URL=http://localhost:8069
ODOO_DATABASE=fahad-graphic-developer
ODOO_USERNAME=cloud_agent@example.com
ODOO_PASSWORD=your_odoo_password_here

# Gmail Configuration
GMAIL_SMTP_SERVER=smtp.gmail.com
GMAIL_SMTP_PORT=587
GMAIL_SENDER_EMAIL=softwarehouse131@gmail.com
GMAIL_APP_PASSWORD=your_gmail_app_password

# Social Media Configuration
FACEBOOK_PAGE_ID=110326951910826
FACEBOOK_ACCESS_TOKEN=your_facebook_token
INSTAGRAM_ACCOUNT_ID=17841457182813798
INSTAGRAM_ACCESS_TOKEN=your_instagram_token
TWITTER_USERNAME=software13702
TWITTER_API_KEY=your_twitter_key
TWITTER_API_SECRET=your_twitter_secret

# Health Monitor
HEALTH_MONITOR_PORT=5000
ALERT_EMAIL=admin@yourdomain.com

# Git Sync
GIT_SYNC_INTERVAL=5
EOF

# Set permissions
chmod 600 /opt/platinum-vault/.env.cloud
chown platinum:platinum /opt/platinum-vault/.env.cloud
```

---

## Step 6: Install Odoo 19 Community

```bash
#!/bin/bash
# install_odoo.sh

# Install Odoo dependencies
sudo apt install -y git python3-pip build-essential wget nodejs libsass-dev \
    zlib1g-dev libjpeg-dev libpq-dev libxml2-dev libxslt1-dev libldap2-dev \
    libsasl2-dev libssl-dev

# Create Odoo user
sudo useradd -m -r -s /bin/bash odoo

# Install wkhtmltopdf (for PDF reports)
wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-2/wkhtmltox_0.12.6.1-2.jammy_amd64.deb
sudo dpkg -i wkhtmltox_0.12.6.1-2.jammy_amd64.deb
sudo rm wkhtmltox_0.12.6.1-2.jammy_amd64.deb

# Clone Odoo 19 Community
sudo mkdir -p /opt/odoo19
sudo chown odoo:odoo /opt/odoo19
sudo su - odoo -c "git clone --depth 1 --branch 19.0 https://github.com/odoo/odoo.git /opt/odoo19/odoo"

# Create Odoo configuration
sudo cat > /etc/odoo19.conf << 'EOF'
[options]
admin_passwd = master_password_here
db_host = localhost
db_port = 5432
db_user = odoo19
db_password = odoo_db_password_here
db_name = fahad-graphic-developer
data_dir = /var/lib/odoo19
addons_path = /opt/odoo19/odoo/addons,/opt/odoo19/custom_addons
http_port = 8069
logfile = /var/log/odoo19/odoo.log
log_level = info
EOF

# Create Odoo directories
sudo mkdir -p /var/lib/odoo19
sudo mkdir -p /var/log/odoo19
sudo chown -R odoo:odoo /var/lib/odoo19
sudo chown -R odoo:odoo /var/log/odoo19

# Set up PostgreSQL
sudo -u postgres createuser -s odoo19
sudo -u postgres psql -c "ALTER USER odoo19 WITH PASSWORD 'odoo_db_password_here';"

# Install Python dependencies for Odoo
sudo pip3 install -r /opt/odoo19/odoo/requirements.txt

# Create systemd service
sudo cat > /etc/systemd/system/odoo19.service << 'EOF'
[Unit]
Description=Odoo 19
After=network.target postgresql.service

[Service]
Type=simple
User=odoo
Group=odoo
ExecStart=/usr/bin/python3 /opt/odoo19/odoo/odoo-bin -c /etc/odoo19.conf
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Enable and start Odoo
sudo systemctl daemon-reload
sudo systemctl enable odoo19
sudo systemctl start odoo19

# Check status
sudo systemctl status odoo19

echo "Odoo 19 installed successfully!"
```

---

## Step 7: Configure HTTPS (Let's Encrypt)

```bash
# Stop Nginx temporarily
sudo systemctl stop nginx

# Configure Nginx for Odoo
sudo cat > /etc/nginx/sites-available/odoo << 'EOF'
server {
    listen 80;
    server_name cloud.yourdomain.com;

    location / {
        proxy_pass http://localhost:8069;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /health {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/odoo /etc/nginx/sites-enabled/odoo

# Start Nginx
sudo systemctl start nginx

# Get SSL certificate
sudo certbot --nginx -d cloud.yourdomain.com

# Auto-renewal is configured automatically
# Test renewal
sudo certbot renew --dry-run
```

---

## Step 8: Configure Supervisor Services

```bash
# Cloud Orchestrator service
sudo cat > /etc/supervisor/conf.d/cloud_orchestrator.conf << 'EOF'
[program:cloud_orchestrator]
command=/opt/platinum-vault/venv/bin/python cloud_orchestrator.py
directory=/opt/platinum-vault
user=platinum
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/cloud_orchestrator.log
environment=PATH="/opt/platinum-vault/venv/bin:/usr/bin:/bin"
EOF

# Health Monitor service
sudo cat > /etc/supervisor/conf.d/health_monitor.conf << 'EOF'
[program:health_monitor]
command=/opt/platinum-vault/venv/bin/python health_monitor.py --port 5000
directory=/opt/platinum-vault
user=platinum
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/health_monitor.log
environment=PATH="/opt/platinum-vault/venv/bin:/usr/bin:/bin"
EOF

# Reload supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start cloud_orchestrator
sudo supervisorctl start health_monitor

# Check status
sudo supervisorctl status
```

---

## Step 9: Configure Git Sync Cron

```bash
# Edit crontab for platinum user
crontab -e

# Add sync job (every 5 minutes)
*/5 * * * * cd /opt/platinum-vault && /opt/platinum-vault/venv/bin/python sync_vault.py --mode sync >> /var/log/vault_sync.log 2>&1

# Create log file
sudo touch /var/log/vault_sync.log
sudo chown platinum:platinum /var/log/vault_sync.log
```

---

## Step 10: Configure Health Monitor External Access

```bash
# Configure firewall (UFW)
sudo apt install -y ufw
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 5000/tcp
sudo ufw enable

# Test health endpoint
curl http://localhost:5000/health

# Test from external machine
curl http://<VM_PUBLIC_IP>:5000/health
```

---

## Step 11: Set Up Daily Backups

```bash
#!/bin/bash
# backup_odoo.sh

BACKUP_DIR="/opt/backups/odoo"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="fahad-graphic-developer"
DB_USER="odoo19"
DB_PASS="odoo_db_password_here"

# Create backup directory
mkdir -p $BACKUP_DIR

# Dump database
PGPASSWORD=$DB_PASS pg_dump -U $DB_USER -h localhost $DB_NAME > $BACKUP_DIR/db_$DATE.sql

# Compress backup
tar -czf $BACKUP_DIR/backup_$DATE.tar.gz -C $BACKUP_DIR db_$DATE.sql
rm $BACKUP_DIR/db_$DATE.sql

# Keep only last 7 days of backups
find $BACKUP_DIR -name "backup_*.tar.gz" -mtime +7 -delete

echo "Backup completed: backup_$DATE.tar.gz"
```

```bash
# Add to crontab (daily at 2 AM)
0 2 * * * /opt/platinum-vault/backup_odoo.sh >> /var/log/odoo_backup.log 2>&1
```

---

## Step 12: Verify Deployment

```bash
# Check all services
sudo supervisorctl status
sudo systemctl status odoo19
sudo systemctl status nginx
sudo systemctl status postgresql

# Test health endpoint
curl http://localhost:5000/health

# Test Odoo
curl http://localhost:8069

# Test vault sync
cd /opt/platinum-vault
git status
python sync_vault.py --mode status

# Check logs
tail -f /var/log/cloud_orchestrator.log
tail -f /var/log/health_monitor.log
tail -f /var/log/odoo19/odoo.log
```

---

## Local Machine Configuration

### Configure Local Orchestrator

```bash
# On your local machine
cd D:\Fahad Project\AI-Driven\Personal-AI-Employee-Hackathon-0\Platinum

# Create .env.local
copy .env.local.example .env.local

# Edit .env.local with your local credentials
notepad .env.local

# Start local orchestrator
python local_orchestrator.py
```

### Configure Git Remote

```bash
# Ensure both Cloud and Local point to same Git repo
# Cloud VM:
cd /opt/platinum-vault
git remote -v

# Local machine:
cd D:\Fahad Project\AI-Driven\Personal-AI-Employee-Hackathon-0\Platinum
git remote -v

# Both should show the same remote URL
```

---

## Troubleshooting

### Cloud Orchestrator Not Running

```bash
# Check supervisor status
sudo supervisorctl status

# Restart if needed
sudo supervisorctl restart cloud_orchestrator

# Check logs
tail -f /var/log/cloud_orchestrator.log
```

### Git Sync Failing

```bash
# Check Git configuration
cd /opt/platinum-vault
git status
git remote -v

# Test manual sync
python sync_vault.py --mode sync

# Check for conflicts
python sync_vault.py --mode status
```

### Odoo Not Accessible

```bash
# Check Odoo status
sudo systemctl status odoo19

# Restart Odoo
sudo systemctl restart odoo19

# Check logs
tail -f /var/log/odoo19/odoo.log
```

### Health Monitor Down

```bash
# Check health monitor status
sudo supervisorctl status health_monitor

# Restart
sudo supervisorctl restart health_monitor

# Check logs
tail -f /var/log/health_monitor.log
```

---

## Post-Deployment Checklist

- [ ] Cloud VM accessible via SSH
- [ ] Odoo accessible at https://cloud.yourdomain.com
- [ ] Health monitor responding at http://cloud.yourdomain.com:5000/health
- [ ] Cloud orchestrator running (supervisorctl status)
- [ ] Git sync working (check /Updates/ on Local)
- [ ] Daily backups configured
- [ ] HTTPS certificate valid (certbot)
- [ ] Local orchestrator running on local machine
- [ ] Approval workflow tested

---

## Next Steps

1. **Run Platinum Demo Test** (see `platinum_demo_test.py`)
2. **Configure Email Watcher** (set up Gmail OAuth)
3. **Test Social Media Drafts** (create test post request)
4. **Test Odoo Integration** (create draft invoice)
5. **Monitor Health Dashboard** (check /health endpoint regularly)

---

**Deployment Complete!**

Your Platinum Tier AI Employee is now running 24/7 on Oracle Cloud Free Tier with:
- ✅ Cloud Agent (draft-only mode)
- ✅ Odoo 19 Community Edition
- ✅ Health Monitoring
- ✅ Git-based Vault Sync
- ✅ HTTPS Security
- ✅ Daily Backups

**Local Agent** on your machine handles:
- ✅ Approval workflows
- ✅ Final execution (send/post)
- ✅ WhatsApp sessions
- ✅ Banking credentials
