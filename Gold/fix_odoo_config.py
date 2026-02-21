"""
Fix Odoo configuration in .env file
"""

with open('.env', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace Odoo configuration
old_config = """# ------------------------------------------------------------
# ODOO INTEGRATION (Accounting/ERP)
# ------------------------------------------------------------
ODOO_URL=https://fahadmemon.odoo.com
ODOO_DB=fahadmemon  # Try: fahadmemon or fahadmemon131@gmail.com
ODOO_USERNAME=fahadmemon131@gmail.com
# ODOO_PASSWORD=memonggc1235#Q
ODOO_PASSWORD=60c5a71fd69880c3fe70ed3608456376a0f2d05a"""

new_config = """# ------------------------------------------------------------
# ODOO INTEGRATION (Accounting/ERP)
# ------------------------------------------------------------
# IMPORTANT: For Odoo.com, database name is usually your email address
# If authentication fails, try different database name
ODOO_URL=https://fahadmemon.odoo.com
ODOO_DB=fahadmemon131@gmail.com
ODOO_USERNAME=fahadmemon131@gmail.com
# Use your Odoo password OR API key
# To get API key: Odoo Settings -> My Profile -> Odoo API Key
ODOO_PASSWORD=memonggc1235#Q"""

content = content.replace(old_config, new_config)

with open('.env', 'w', encoding='utf-8') as f:
    f.write(content)

print("[OK] Odoo configuration updated!")
print("\nChanges:")
print("  - ODOO_DB changed to: fahadmemon131@gmail.com")
print("  - ODOO_PASSWORD changed to: memonggc1235#Q")
print("\nTest with: python -c \"from odoo_integration.odoo_connector import get_odoo_connection; print('OK' if get_odoo_connection() else 'FAIL')\"")
