# Gmail OAuth Setup Guide - MCP Email Server

**Goal:** Setup Gmail OAuth for MCP Email Server to send real emails

---

## Step-by-Step Instructions

### Step 1: Google Cloud Console Setup

1. **Go to Google Cloud Console**
   - URL: https://console.cloud.google.com/
   - Login with your Gmail account

2. **Create New Project**
   ```
   Click "Select a project" → "New Project"
   Project name: MCP Email Server
   Click "Create"
   ```

3. **Enable Gmail API**
   ```
   Go to: APIs & Services → Library
   Search: "Gmail API"
   Click on "Gmail API"
   Click "Enable"
   ```

4. **Configure OAuth Consent Screen**
   ```
   Go to: APIs & Services → OAuth consent screen
   Select: "External"
   Click "Create"
   
   App name: MCP Email Server
   User support email: your-email@gmail.com
   Developer contact email: your-email@gmail.com
   Click "Save and Continue"
   
   Scopes: Skip this step (click Save and Continue)
   Test users: Add your Gmail address
   Click "Save and Continue"
   ```

5. **Create OAuth 2.0 Client ID**
   ```
   Go to: APIs & Services → Credentials
   Click: "+ CREATE CREDENTIALS" → "OAuth client ID"
   Application type: Desktop app
   Name: MCP Email Client
   Click "Create"
   ```

6. **Download Credentials**
   ```
   A popup will show "OAuth client created"
   Click "DOWNLOAD JSON"
   Save file as: credentials.json
   ```

---

### Step 2: Save Credentials File

1. **Move credentials.json** to project folder:
   ```
   D:\Fahad Project\AI-Driven\Personal-AI-Employee-Hackathon-0\Gold\credentials.json
   ```

2. **Verify file exists:**
   ```bash
   dir "D:\Fahad Project\AI-Driven\Personal-AI-Employee-Hackathon-0\Gold\credentials.json"
   ```

---

### Step 3: Run OAuth Setup Script

1. **Install required packages** (if not already installed):
   ```bash
   pip install google-auth google-auth-oauthlib google-api-python-client
   ```

2. **Run OAuth setup:**
   ```bash
   cd "D:\Fahad Project\AI-Driven\Personal-AI-Employee-Hackathon-0\Gold"
   python setup_gmail_oauth.py
   ```

3. **Complete Authentication:**
   ```
   - Browser window will open automatically
   - Login with your Gmail account
   - Click "Allow" to grant permissions
   - You'll see "Authentication successful!"
   - token.pickle file will be created
   ```

---

### Step 4: Verify Setup

1. **Check files exist:**
   ```bash
   dir credentials.json token.pickle
   ```

2. **Test Email MCP Server:**
   ```bash
   python mcp_email_server.py
   ```
   
   You should see:
   ```
   Gmail authentication successful!
   Gmail service initialized
   MCP Email Server running on http://localhost:8080
   ```

---

### Step 5: Send Test Email

#### Option A: Via MCP Server API

```bash
# Keep mcp_email_server.py running in one terminal

# In another terminal, send email:
curl -X POST http://localhost:8080/tools/send_email ^
  -H "Content-Type: application/json" ^
  -d "{\"to\": \"receiver@example.com\", \"subject\": \"Test Email\", \"body\": \"Hello from MCP Email Server!\"}"
```

#### Option B: Via Python Script

```python
import requests

response = requests.post('http://localhost:8080/tools/send_email', json={
    'to': 'receiver@example.com',
    'subject': 'Test Email from MCP',
    'body': 'This email was sent using MCP Email Server!'
})

print(response.json())
```

---

## Troubleshooting

### Error: "Credentials file not found"

**Solution:**
- Make sure `credentials.json` is in the Gold folder
- Check file name is exactly `credentials.json` (not `credentials (1).json`)

### Error: "Token expired"

**Solution:**
```bash
# Delete old token and re-authenticate
del token.pickle
python setup_gmail_oauth.py
```

### Error: "Gmail API not enabled"

**Solution:**
1. Go to https://console.cloud.google.com/apis/library/gmail.googleapis.com
2. Click "Enable"

### Error: "OAuth consent screen not configured"

**Solution:**
1. Go to https://console.cloud.google.com/apis/credentials/consent
2. Fill in required fields
3. Add your email as test user

### Browser Doesn't Open

**Solution:**
- Copy the URL shown in terminal and paste in browser manually
- Make sure popup blocker is disabled

---

## Security Notes

### Protect Your Credentials

1. **Never commit credentials to Git:**
   ```bash
   # Add to .gitignore
   echo "credentials.json" >> .gitignore
   echo "token.pickle" >> .gitignore
   ```

2. **Keep credentials.json private:**
   - Don't share this file
   - Store securely

3. **Use App Password for 2FA accounts:**
   - If you have 2-Factor Authentication enabled
   - Use App Password instead of regular password
   - Get it from: https://myaccount.google.com/apppasswords

---

## File Structure After Setup

```
Gold/
├── credentials.json          # OAuth credentials (keep private!)
├── token.pickle              # Auth token (auto-generated)
├── mcp_email_server.py       # Email MCP server
├── setup_gmail_oauth.py      # OAuth setup script
├── send_email_simple.py      # Simple SMTP email sender
└── Skills/
    └── weekly_ceo_briefing.py # CEO briefing skill
```

---

## Quick Reference Commands

```bash
# Setup OAuth (run once)
python setup_gmail_oauth.py

# Start Email MCP Server
python mcp_email_server.py

# Send test email via API
curl -X POST http://localhost:8080/tools/send_email ^
  -H "Content-Type: application/json" ^
  -d "{\"to\": \"test@example.com\", \"subject\": \"Hello\", \"body\": \"Test!\"}"

# Check server health
curl http://localhost:8080/health
```

---

## Next Steps After Setup

1. ✅ **Test email sending** to your own email first
2. ✅ **Add email to weekly briefing** workflow
3. ✅ **Configure approval workflow** for outgoing emails
4. ✅ **Setup Gmail watcher** for incoming emails

---

**Need Help?**
- Google Cloud Console: https://console.cloud.google.com/
- Gmail API Docs: https://developers.google.com/gmail/api
- OAuth Setup Guide: https://developers.google.com/identity/protocols/oauth2

---

*Guide created by AI Digital FTE Employee*
