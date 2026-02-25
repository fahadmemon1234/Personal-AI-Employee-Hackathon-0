#!/usr/bin/env python3
"""
health_monitor.py - Platinum Tier Health Monitoring

Flask-based health monitoring endpoint for Cloud Agent.
Provides /health endpoint for uptime monitoring.
Sends email alerts if services are down.

Run as a systemd/supervisor service on Cloud VM.
"""

import os
import sys
import time
import logging
import smtplib
import subprocess
from pathlib import Path
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, jsonify
from dotenv import load_dotenv
import threading

# Load environment variables
load_dotenv('.env.cloud')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('health_monitor')

app = Flask(__name__)

# Health state
health_state = {
    'status': 'healthy',
    'uptime': datetime.now(),
    'last_check': None,
    'services': {},
    'version': '1.0.0'
}


class HealthChecker:
    """Performs health checks on system services."""
    
    def __init__(self, vault_path: str = None):
        if vault_path:
            self.vault_path = Path(vault_path)
        elif os.getenv('VAULT_PATH'):
            self.vault_path = Path(os.getenv('VAULT_PATH'))
        else:
            self.vault_path = Path.cwd()
            
        # Services to monitor
        self.services = {
            'cloud_orchestrator': {'port': None, 'process': 'cloud_orchestrator.py'},
            'email_mcp': {'port': 8080, 'process': 'mcp_email_server.py'},
            'social_mcp': {'port': 8083, 'process': 'mcp_social_server.py'},
            'x_mcp': {'port': 8084, 'process': 'mcp_x_server.py'},
            'odoo_mcp': {'port': 8082, 'process': 'mcp_odoo_server.py'},
            'odoo': {'port': 8069, 'process': 'odoo'},
            'postgres': {'port': 5432, 'process': 'postgres'},
            'nginx': {'port': 80, 'process': 'nginx'},
        }
        
    def check_port(self, port: int) -> bool:
        """Check if a port is listening."""
        try:
            result = subprocess.run(
                ['ss', '-tln', f'sport = :{port}'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return str(port) in result.stdout
        except Exception:
            return False
            
    def check_process(self, process_name: str) -> bool:
        """Check if a process is running."""
        try:
            result = subprocess.run(
                ['pgrep', '-f', process_name],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0 and bool(result.stdout.strip())
        except Exception:
            return False
            
    def check_disk_space(self, threshold: float = 90.0) -> bool:
        """Check if disk space is below threshold."""
        try:
            result = subprocess.run(
                ['df', str(self.vault_path)],
                capture_output=True,
                text=True,
                timeout=5
            )
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:
                # Parse usage percentage
                parts = lines[1].split()
                for part in parts:
                    if '%' in part:
                        usage = float(part.replace('%', ''))
                        return usage < threshold
            return True
        except Exception:
            return True  # Assume OK on error
            
    def check_memory(self, threshold: float = 90.0) -> bool:
        """Check if memory usage is below threshold."""
        try:
            result = subprocess.run(
                ['free', '-m'],
                capture_output=True,
                text=True,
                timeout=5
            )
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:
                parts = lines[1].split()
                total = float(parts[1])
                used = float(parts[2])
                usage = (used / total) * 100
                return usage < threshold
            return True
        except Exception:
            return True
            
    def check_git_sync(self, max_age_minutes: int = 15) -> bool:
        """Check if git sync is recent."""
        try:
            result = subprocess.run(
                ['git', 'log', '-1', '--format=%ct'],
                cwd=str(self.vault_path),
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                last_commit_time = int(result.stdout.strip())
                current_time = time.time()
                age_minutes = (current_time - last_commit_time) / 60
                return age_minutes < max_age_minutes
            return True
        except Exception:
            return True
            
    def run_all_checks(self) -> dict:
        """Run all health checks and return results."""
        results = {}
        
        # Check each service
        for name, config in self.services.items():
            is_healthy = False
            
            if config.get('port'):
                is_healthy = self.check_port(config['port'])
            elif config.get('process'):
                is_healthy = self.check_process(config['process'])
                
            results[name] = {
                'healthy': is_healthy,
                'port': config.get('port'),
                'process': config.get('process')
            }
            
        # System checks
        results['disk_space'] = {
            'healthy': self.check_disk_space(),
            'type': 'system'
        }
        
        results['memory'] = {
            'healthy': self.check_memory(),
            'type': 'system'
        }
        
        results['git_sync'] = {
            'healthy': self.check_git_sync(),
            'type': 'sync'
        }
        
        return results


class AlertSender:
    """Sends email alerts when services are down."""
    
    def __init__(self):
        self.smtp_server = os.getenv('GMAIL_SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('GMAIL_SMTP_PORT', 587))
        self.sender_email = os.getenv('GMAIL_SENDER_EMAIL', '')
        self.sender_password = os.getenv('GMAIL_APP_PASSWORD', '')
        self.alert_email = os.getenv('ALERT_EMAIL', self.sender_email)
        
    def send_alert(self, subject: str, message: str, failed_services: list) -> bool:
        """
        Send email alert.
        
        Args:
            subject: Email subject
            message: Email body
            failed_services: List of failed service names
            
        Returns:
            True if sent successfully
        """
        if not self.sender_email or not self.sender_password:
            logger.warning("Email credentials not configured. Cannot send alert.")
            return False
            
        try:
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = self.alert_email
            msg['Subject'] = f"[ALERT] {subject}"
            
            body = f"""
Health Alert - Cloud Agent

Timestamp: {datetime.now().isoformat()}

Failed Services:
{chr(10).join(f'  - {s}' for s in failed_services)}

Details:
{message}

---
Cloud Agent Health Monitor
Platinum Tier
"""
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Alert sent to {self.alert_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send alert: {e}")
            return False


# Global instances
health_checker = HealthChecker()
alert_sender = AlertSender()
last_alert_time = None
ALERT_COOLDOWN_MINUTES = 15


def background_health_check():
    """Run health checks in background and update state."""
    global health_state, last_alert_time
    
    while True:
        try:
            # Run all checks
            results = health_checker.run_all_checks()
            
            # Update state
            health_state['last_check'] = datetime.now()
            health_state['services'] = results
            
            # Determine overall status
            failed_services = [
                name for name, info in results.items()
                if not info.get('healthy', True)
            ]
            
            if failed_services:
                health_state['status'] = 'unhealthy'
                
                # Send alert (with cooldown)
                now = datetime.now()
                if last_alert_time is None or (now - last_alert_time).total_seconds() > ALERT_COOLDOWN_MINUTES * 60:
                    message = f"Failed services: {', '.join(failed_services)}"
                    alert_sender.send_alert(
                        f"Cloud Agent Unhealthy - {len(failed_services)} services down",
                        message,
                        failed_services
                    )
                    last_alert_time = now
            else:
                health_state['status'] = 'healthy'
                
        except Exception as e:
            logger.error(f"Health check error: {e}")
            health_state['status'] = 'error'
            
        # Sleep 60 seconds
        time.sleep(60)


@app.route('/health', methods=['GET'])
def health_endpoint():
    """
    Health check endpoint.
    
    Returns:
        JSON with health status
    """
    return jsonify({
        'status': health_state['status'],
        'uptime': str(datetime.now() - health_state['uptime']),
        'last_check': health_state['last_check'].isoformat() if health_state['last_check'] else None,
        'services': health_state['services'],
        'version': health_state['version']
    })


@app.route('/health/summary', methods=['GET'])
def health_summary():
    """
    Simplified health summary endpoint.
    
    Returns:
        JSON with basic status
    """
    failed = [
        name for name, info in health_state['services'].items()
        if not info.get('healthy', True)
    ]
    
    return jsonify({
        'status': 'healthy' if not failed else 'unhealthy',
        'failed_services': failed,
        'failed_count': len(failed),
        'timestamp': datetime.now().isoformat()
    })


@app.route('/health/check', methods=['POST'])
def force_health_check():
    """
    Force immediate health check.
    
    Returns:
        JSON with fresh results
    """
    results = health_checker.run_all_checks()
    
    failed = [name for name, info in results.items() if not info.get('healthy', True)]
    
    return jsonify({
        'status': 'healthy' if not failed else 'unhealthy',
        'services': results,
        'failed_services': failed,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/', methods=['GET'])
def index():
    """Root endpoint with info."""
    return jsonify({
        'service': 'Cloud Agent Health Monitor',
        'version': health_state['version'],
        'endpoints': {
            '/health': 'Full health status',
            '/health/summary': 'Simplified health summary',
            '/health/check': 'Force health check (POST)'
        }
    })


def main():
    """Run health monitor."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Health Monitor - Platinum Tier')
    parser.add_argument('--vault', type=str, help='Vault path (default: VAULT_PATH env or cwd)')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host to bind (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind (default: 5000)')
    parser.add_argument('--debug', action='store_true', help='Run in debug mode')
    
    args = parser.parse_args()
    
    # Initialize health checker with vault path
    global health_checker
    health_checker = HealthChecker(vault_path=args.vault)
    
    # Start background health check thread
    check_thread = threading.Thread(target=background_health_check, daemon=True)
    check_thread.start()
    
    logger.info(f"Health Monitor starting on {args.host}:{args.port}")
    
    # Run Flask app
    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
