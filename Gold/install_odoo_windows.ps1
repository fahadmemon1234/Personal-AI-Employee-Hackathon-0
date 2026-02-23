# Odoo 19 Windows Auto-Installer Script
# Run as Administrator

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Odoo 19 Community - Windows Auto-Installer" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "ERROR: Please run this script as Administrator!" -ForegroundColor Red
    Write-Host "Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    exit 1
}

Write-Host "[1/8] Checking system requirements..." -ForegroundColor Green

# Check PowerShell version
$psVersion = $PSVersionTable.PSVersion.Major
if ($psVersion -lt 5) {
    Write-Host "WARNING: PowerShell version should be 5 or higher" -ForegroundColor Yellow
}

# Check available disk space
$disk = Get-PSDrive C
$freeSpaceGB = [math]::Round($disk.Free / 1GB, 2)
Write-Host "  Available Disk Space: ${freeSpaceGB}GB" -ForegroundColor Cyan

if ($freeSpaceGB -lt 10) {
    Write-Host "ERROR: Need at least 10GB free space!" -ForegroundColor Red
    exit 1
}

# Check RAM
$ramGB = [math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1GB, 2)
Write-Host "  Total RAM: ${ramGB}GB" -ForegroundColor Cyan

if ($ramGB -lt 4) {
    Write-Host "WARNING: Less than 4GB RAM may cause performance issues" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[2/8] Downloading Odoo 19 Windows Installer..." -ForegroundColor Green

$downloadUrl = "https://nightly.odoo.com/19.0/nightly/win/odoo_19.0.latest.exe"
$installerPath = "$env:TEMP\odoo_19_installer.exe"

Write-Host "  Download URL: $downloadUrl" -ForegroundColor Cyan
Write-Host "  Download Path: $installerPath" -ForegroundColor Cyan

$downloadSuccess = $false
try {
    $webClient = New-Object System.Net.WebClient
    $webClient.Headers.Add("User-Agent", "PowerShell Script")
    $webClient.DownloadFile($downloadUrl, $installerPath)
    $downloadSuccess = $true
    Write-Host "  Download completed!" -ForegroundColor Green
} catch {
    Write-Host "  ERROR: Download failed!" -ForegroundColor Red
}

if (-not $downloadSuccess) {
    Write-Host "  Manual download required from: https://nightly.odoo.com/19.0/nightly/win/" -ForegroundColor Yellow
    Write-Host "  After downloading, run the installer manually." -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "[3/8] Installing Odoo 19..." -ForegroundColor Green
Write-Host "  This may take 5-10 minutes..." -ForegroundColor Cyan

# Run installer silently
$installProcess = Start-Process -FilePath $installerPath -ArgumentList "/S" -Wait -PassThru

if ($installProcess.ExitCode -eq 0) {
    Write-Host "  Installation completed!" -ForegroundColor Green
} else {
    Write-Host "  WARNING: Installer exited with code: $($installProcess.ExitCode)" -ForegroundColor Yellow
    Write-Host "  Installation may still be successful. Check manually." -ForegroundColor Yellow
}

# Clean up installer
Remove-Item $installerPath -Force -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "[4/8] Configuring Odoo..." -ForegroundColor Green

$odooPath = "C:\Program Files\Odoo 19.0"
$odooServerPath = "$odooPath\server"
$odooConfPath = "$odooServerPath\odoo.conf"

# Check if Odoo is installed
if (-not (Test-Path $odooPath)) {
    Write-Host "  ERROR: Odoo installation folder not found!" -ForegroundColor Red
    Write-Host "  Please install Odoo manually from: https://nightly.odoo.com/19.0/nightly/win/" -ForegroundColor Yellow
    exit 1
}

Write-Host "  Odoo Path: $odooPath" -ForegroundColor Cyan

# Create odoo.conf
$odooConf = @"
[options]
; Admin password for database management
admin_passwd = master_admin_123

; Database connection
db_host = localhost
db_port = 5432
db_user = odoo
db_password = odoo
db_name = my_business_db

; Server configuration
http_port = 8069
http_interface = 0.0.0.0

; Logging
logfile = $odooServerPath\odoo.log
log_level = info

; Data directory
data_dir = $odooPath\data

; Addons paths
addons_path = $odooPath\server\odoo\addons
"@

try {
    Set-Content -Path $odooConfPath -Value $odooConf -Encoding UTF8
    Write-Host "  Configuration file created!" -ForegroundColor Green
} catch {
    Write-Host "  ERROR: Could not create config file!" -ForegroundColor Red
}

Write-Host ""
Write-Host "[5/8] Starting Odoo Service..." -ForegroundColor Green

$serviceName = "odoo_server_19"
$serviceFound = $false

# Check if service exists
try {
    $service = Get-Service -Name $serviceName -ErrorAction SilentlyContinue
    if ($service) {
        $serviceFound = $true
        Write-Host "  Service found: $serviceName" -ForegroundColor Cyan
        
        try {
            Start-Service -Name $serviceName
            Write-Host "  Odoo service started!" -ForegroundColor Green
        } catch {
            Write-Host "  WARNING: Could not start service automatically" -ForegroundColor Yellow
        }
    }
} catch {
    Write-Host "  Service not found. Will start manually..." -ForegroundColor Yellow
}

if (-not $serviceFound) {
    Write-Host "  Starting Odoo manually..." -ForegroundColor Yellow
    $odooBinPath = "$odooServerPath\odoo-bin.py"
    if (Test-Path $odooBinPath) {
        Write-Host "  Found odoo-bin.py at: $odooBinPath" -ForegroundColor Cyan
        Write-Host "  Note: Run manually from new terminal" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "[6/8] Configuring Windows Firewall..." -ForegroundColor Green

# Add firewall rule for Odoo
try {
    $ruleName = "Odoo 19 HTTP"
    $existingRule = Get-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue
    
    if (-not $existingRule) {
        New-NetFirewallRule -DisplayName $ruleName -Direction Inbound -Protocol TCP -LocalPort 8069 -Action Allow
        Write-Host "  Firewall rule created for port 8069" -ForegroundColor Green
    } else {
        Write-Host "  Firewall rule already exists" -ForegroundColor Cyan
    }
} catch {
    Write-Host "  WARNING: Could not configure firewall" -ForegroundColor Yellow
    Write-Host "  Manually allow port 8069 in Windows Firewall" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[7/8] Creating .env file for MCP..." -ForegroundColor Green

$goldPath = "D:\Fahad Project\AI-Driven\Personal-AI-Employee-Hackathon-0\Gold"
$envPath = "$goldPath\.env"

if (Test-Path $goldPath) {
    $envContent = @"
ODOO_URL=http://localhost:8069
ODOO_DB=my_business_db
ODOO_USERNAME=mcp@yourbusiness.local
ODOO_PASSWORD=McpPassword123
MCP_ODOO_PORT=8082
MCP_ODOO_HOST=0.0.0.0
ODOO_MOCK=false
"@
    
    Set-Content -Path $envPath -Value $envContent -Encoding UTF8
    Write-Host "  .env file created at: $envPath" -ForegroundColor Green
} else {
    Write-Host "  WARNING: Gold directory not found!" -ForegroundColor Yellow
    Write-Host "  Create .env file manually" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[8/8] Opening Odoo in Browser..." -ForegroundColor Green

Start-Process "http://localhost:8069"

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Installation Complete!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "NEXT STEPS:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Open browser: http://localhost:8069" -ForegroundColor White
Write-Host "2. Click 'Create Database'" -ForegroundColor White
Write-Host "3. Fill in:" -ForegroundColor White
Write-Host "   - Database: my_business_db" -ForegroundColor Cyan
Write-Host "   - Email: admin@yourbusiness.com" -ForegroundColor Cyan
Write-Host "   - Password: AdminPassword123" -ForegroundColor Cyan
Write-Host ""
Write-Host "4. Install 'Invoicing' app from Apps menu" -ForegroundColor White
Write-Host "5. Create MCP user in Settings -> Users" -ForegroundColor White
Write-Host ""
Write-Host "MCP Server Start karne ke liye:" -ForegroundColor Yellow
Write-Host "  cd '$goldPath'" -ForegroundColor Cyan
Write-Host "  python mcp_odoo_server.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
