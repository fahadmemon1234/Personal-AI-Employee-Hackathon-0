# LinkedIn API Setup Guide

## Quick Start (Already have credentials in .env)

Agar aapke paas already credentials `.env` file mein hain, toh bas ye command run karein:

```bash
python linkedin_api_poster.py --authenticate
```

Ye automatically:
1. Browser open karega
2. LinkedIn authorization page par le jayega
3. Authorize karne ke baad code automatically capture ho jayega
4. Token aur Person URN `.env` file mein save ho jayega

## Step 1: Create LinkedIn Developer App

1. Go to [LinkedIn Developer Portal](https://www.linkedin.com/developers/apps)
2. Click **"Create app"** button
3. Fill in the required information:
   - **App Name**: Your app name (e.g., "AI Automation Poster")
   - **LinkedIn Page**: Select a company page (you must be admin of at least one page)
   - **App Logo**: Optional
   - **Privacy Policy URL**: Can use `https://example.com/privacy` for testing
   - **User Agreement URL**: Can use `https://example.com/terms` for testing
4. Click **"Create app**"

## Step 2: Configure Authentication

1. After creating the app, go to **"Auth"** tab
2. Note down your credentials:
   - **Client ID**
   - **Client Secret**
3. Under **"OAuth 2.0 Redirect URLs"**, add:
   ```
   http://localhost:8080/callback
   ```
4. Click **"Update"**

## Step 3: Request API Access

1. Go to **"Products"** tab
2. Enable the following APIs:
   - **Sign In with LinkedIn using OpenID Connect**
   - **Share on LinkedIn API** (w_member_social)
3. Click **"Request Access"** for each product
4. Fill in the use case description:
   ```
   This app will post AI automation updates and company news to LinkedIn on behalf of users.
   ```

## Step 4: Update .env File

Open `.env` file and update with your credentials:

```env
LINKEDIN_CLIENT_ID=your_client_id_here
LINKEDIN_CLIENT_SECRET=your_client_secret_here
LINKEDIN_REDIRECT_URI=http://localhost:8080/callback
LINKEDIN_ACCESS_TOKEN=
LINKEDIN_PERSON_URN=
```

## Step 5: Authenticate

1. Run the authentication command:
   ```bash
   python linkedin_api_poster.py --authenticate
   ```

2. The script will automatically:
   - Start a local server on `http://localhost:8080`
   - Open LinkedIn authorization page in your browser

3. Authorize the application on LinkedIn

4. After authorization, you'll be redirected to a success page

5. The script will automatically capture the authorization code and complete authentication

6. Token and Person URN will be saved to `.env` file

**Note:** If the browser doesn't open automatically, copy the URL shown in the terminal and open it manually.

## Step 6: Post to LinkedIn

### Option A: Post Pending Posts
```bash
python linkedin_api_poster.py
```
This will check `Pending_Approval/` folder for draft posts and ask for confirmation before posting.

### Option B: Post Direct Text
```bash
python linkedin_api_poster.py --post "Your post content here #AI #Automation"
```

## Usage with Existing Workflow

To integrate with your existing `linkedin_poster.py` workflow:

1. Create draft posts as usual:
   ```bash
   python linkedin_poster.py
   ```

2. Post to LinkedIn using the API poster:
   ```bash
   python linkedin_api_poster.py
   ```

## Troubleshooting

### "Failed to get person URN" or "ACCESS_DENIED"
- Your access token may be expired. Run: `python linkedin_api_poster.py --authenticate`
- Make sure you've requested access to "Share on LinkedIn API" in the Products tab

### "LINKEDIN_CLIENT_ID not found"
- Check that `.env` file exists and has the correct credentials

### "Invalid redirect_uri"
- Ensure `http://localhost:8080/callback` is added in your app's Auth settings

## API Limits

- **Posts per day**: 20 posts per user
- **Character limit**: 3,000 characters per post
- **Rate limit**: 500 requests per day

## Files Used

| File | Purpose |
|------|---------|
| `.env` | API credentials and tokens (already exists) |
| `linkedin_api_poster.py` | Main posting script |
| `linkedin_token.json` | Backup token file (auto-generated if needed) |
