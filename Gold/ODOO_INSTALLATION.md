# Odoo 19 Community Edition - Local Installation Guide

## System Requirements

- **OS:** Ubuntu 20.04/22.04 or Debian 11/12
- **RAM:** Minimum 4GB (8GB recommended)
- **Storage:** 10GB free space
- **Python:** 3.10 or higher
- **PostgreSQL:** 12 or higher

---

## Step 1: Update System & Install Dependencies

```bash
# Update package list
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y git python3 python3-pip python3-dev python3-venv \
    python3-wheel build-essential libxslt1-dev libzip-dev libldap2-dev \
    libsasl2-dev libpng-dev libjpeg-dev libfreetype6-dev libxml2-dev \
    libmysqlclient-dev libxrender1 libjpeg8 libzmq5 libgeos-dev \
    postgresql postgresql-contrib node-less npm libpq-dev libffi-dev
```

---

## Step 2: Install PostgreSQL & Create Database User

```bash
# Start PostgreSQL service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create Odoo database user
sudo -u postgres createuser -s odoo19

# Set password for odoo19 user (remember this password)
sudo -u postgres psql -c "ALTER USER odoo19 WITH PASSWORD 'odoo19_password';"
```

---

## Step 3: Create Odoo System User

```bash
# Create odoo user (no login shell for security)
sudo useradd -m -d /opt/odoo19 -U -r -s /bin/bash odoo19

# Set home directory permissions
sudo chmod -R 755 /opt/odoo19
```

---

## Step 4: Download & Install Odoo 19 Community

```bash
# Switch to odoo user
sudo su - odoo19

# Clone Odoo 19 Community from GitHub
cd /opt/odoo19
git clone https://github.com/odoo/odoo.git --depth 1 --branch 19.0 .

# Create Python virtual environment
python3 -m venv odoo-venv

# Activate virtual environment
source odoo-venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install Python dependencies
pip install -r requirements.txt

# Install additional Python packages for accounting
pip install psycopg2-binary xlwt passlib pyserial ofxparse

# Exit odoo user
exit
```

---

## Step 5: Create Odoo Configuration File

```bash
# Create config directory
sudo mkdir -p /etc/odoo19
sudo mkdir -p /var/log/odoo19
sudo mkdir -p /var/lib/odoo19

# Create odoo.conf file
sudo nano /etc/odoo19/odoo.conf
```

**Add this configuration:**

```ini
[options]
; Admin password for database management
admin_passwd = master_admin_password_123

; Database connection
db_host = localhost
db_port = 5432
db_user = odoo19
db_password = odoo19_password
db_name = my_business_db

; Server configuration
http_port = 8069
; For local development, bind to all interfaces
http_interface = 0.0.0.0

; Logging
logfile = /var/log/odoo19/odoo.log
log_level = info

; Data directory
data_dir = /var/lib/odoo19

; Addons paths
addons_path = /opt/odoo19/addons,/opt/odoo19/odoo/addons

; Enable developer mode by default
; Uncomment below for development
; dev_mode = True
```

**Set permissions:**

```bash
sudo chown -R odoo19:odoo19 /var/log/odoo19
sudo chown -R odoo19:odoo19 /var/lib/odoo19
sudo chown -R odoo19:odoo19 /etc/odoo19
sudo chmod 640 /etc/odoo19/odoo.conf
```

---

## Step 6: Create Systemd Service

```bash
# Create systemd service file
sudo nano /etc/systemd/system/odoo19.service
```

**Add this content:**

```ini
[Unit]
Description=Odoo 19 Community Edition
After=network.target postgresql.service

[Service]
Type=simple
User=odoo19
Group=odoo19
ExecStart=/opt/odoo19/odoo-venv/bin/python3 /opt/odoo19/odoo-bin --config=/etc/odoo19/odoo.conf
Restart=always
RestartSec=5
Environment="PATH=/opt/odoo19/odoo-venv/bin"

[Install]
WantedBy=multi-user.target
```

**Reload systemd and start Odoo:**

```bash
# Reload systemd daemon
sudo systemctl daemon-reload

# Enable Odoo service
sudo systemctl enable odoo19

# Start Odoo
sudo systemctl start odoo19

# Check status
sudo systemctl status odoo19

# View logs
sudo journalctl -u odoo19 -f
```

---

## Step 7: Create Database "my_business_db"

### Option A: Via Web Interface (Recommended)

1. Open browser: `http://localhost:8069`
2. Click **"Create Database"**
3. Fill in:
   - **Database Name:** `my_business_db`
   - **Email:** your-email@example.com
   - **Password:** (admin password for Odoo)
   - **Language:** English (US)
   - **Country:** Pakistan (or your country)
4. Click **"Create Database"**

### Option B: Via Command Line

```bash
# Create database using odoo-bin
sudo su - odoo19
source /opt/odoo19/odoo-venv/bin/activate

# Create database with demo data
/opt/odoo19/odoo-bin -c /etc/odoo19/odoo.conf -d my_business_db --without-demo=all --install base

exit
```

---

## Step 8: Install Accounting + Invoicing Modules

### Via Web Interface:

1. Login to Odoo: `http://localhost:8069`
2. Select database: `my_business_db`
3. Login with your credentials
4. Go to **Apps** (from main menu)
5. Remove "Apps" filter in search bar
6. Search and install these modules:

| Module | Technical Name | Description |
|--------|---------------|-------------|
| **Invoicing** | `account` | Core accounting/invoicing |
| **Accounting** | `account_full_reconcile` | Full accounting features |
| **Payments** | `payment` | Payment processing |
| **Bank Synchronization** | `account_bank_statement_import` | Bank statements |

7. Click **"Install"** on each module

### Via Command Line:

```bash
sudo su - odoo19
source /opt/odoo19/odoo-venv/bin/activate

# Install accounting modules
/opt/odoo19/odoo-bin -c /etc/odoo19/odoo.conf -d my_business_db \
    -i account,invoice,account_accountant,payment --without-demo=all

exit
```

---

## Step 9: Configure Accounting

1. Go to **Invoicing App** (or Accounting if installed)
2. Complete the **Configuration Wizard**:
   - Company information
   - Chart of accounts (select based on your country)
   - Tax configuration
   - Fiscal year settings
3. Set up:
   - **Customers** (Create test customer)
   - **Vendors** (Create test vendor)
   - **Products/Services** (Create test products)
   - **Bank Accounts** (Add your business bank account)

---

## Step 10: Create API User for MCP Integration

1. Go to **Settings** → **Users & Companies** → **Users**
2. Click **Create**
3. Fill in:
   - **Name:** `MCP Integration User`
   - **Email:** `mcp@yourbusiness.local`
   - **Access Rights:** 
     - Invoicing / Accounting: **Administrator**
     - Settings: **Internal User**
4. Set a strong password (save for MCP config)
5. Click **Save**

---

## Step 11: Enable Developer Mode (for API access)

1. Go to **Settings**
2. Scroll to bottom
3. Click **"Activate the developer mode"**

---

## Verify Installation

```bash
# Check if Odoo is running
sudo systemctl status odoo19

# Check logs
tail -f /var/log/odoo19/odoo.log

# Test web access
curl http://localhost:8069
```

**Access Points:**
- **Web Interface:** http://localhost:8069
- **Database:** my_business_db
- **Database User:** odoo19
- **Database Password:** odoo19_password

---

## Firewall Configuration (if needed)

```bash
# Allow Odoo port through firewall
sudo ufw allow 8069/tcp
sudo ufw reload
```

---

## Backup Configuration

```bash
# Create backup script
sudo nano /opt/odoo19/backup_odoo.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/odoo19"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="my_business_db"

mkdir -p $BACKUP_DIR

# Database backup
sudo -u postgres pg_dump $DB_NAME > $BACKUP_DIR/${DB_NAME}_${DATE}.sql

# Filestore backup
tar -czf $BACKUP_DIR/filestore_${DATE}.tar.gz /var/lib/odoo19/filestore/

# Keep only last 7 backups
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
```

```bash
# Make executable and add to cron
chmod +x /opt/odoo19/backup_odoo.sh

# Add to crontab (daily at 2 AM)
crontab -e
# Add: 0 2 * * * /opt/odoo19/backup_odoo.sh
```

---

## Troubleshooting

### Odoo won't start:
```bash
# Check logs
sudo journalctl -u odoo19 -n 50

# Check PostgreSQL
sudo systemctl status postgresql

# Check port conflict
sudo netstat -tlnp | grep 8069
```

### Database connection error:
```bash
# Verify PostgreSQL user
sudo -u postgres psql -c "\du odoo19"

# Reset password if needed
sudo -u postgres psql -c "ALTER USER odoo19 WITH PASSWORD 'odoo19_password';"
```

### Module installation fails:
```bash
# Update module list
sudo su - odoo19
source /opt/odoo19/odoo-venv/bin/activate
/opt/odoo19/odoo-bin -c /etc/odoo19/odoo.conf -d my_business_db -u all --stop-after-init
exit
```

---

## Next Steps

After installation is complete:
1. Configure the MCP Odoo server (see `mcp_odoo_server.py`)
2. Set up environment variables
3. Test API connectivity
4. Create your first invoice via MCP

---

*Installation guide created for Odoo 19 Community Edition*
