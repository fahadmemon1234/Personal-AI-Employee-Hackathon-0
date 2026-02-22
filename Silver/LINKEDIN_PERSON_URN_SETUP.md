# LinkedIn API Setup - Fix for Posting

## Problem
LinkedIn API requires a Person URN (like `urn:li:member:123456789`) to create posts.
The `w_member_social` scope is authorized, but we need to get your Person URN manually.

## Solution: Get Your Person URN

### Method 1: From LinkedIn Profile URL (Easiest)

1. Go to your LinkedIn profile: https://www.linkedin.com/in/your-username/
2. Right-click on your profile picture
3. Select "Copy image address"
4. The URL will look like: `https://media.licdn.com/dms/image/v2/D5603AQ.../profile-displayphoto-shrink_800_800/0/1234567890123?e=...&oid=123456789&type=3`
5. The `oid` number is NOT your URN

### Method 2: Using Browser DevTools

1. Go to https://www.linkedin.com/feed/
2. Press F12 to open DevTools
3. Go to Network tab
4. Create a post manually on LinkedIn
5. Look for a request to `api.linkedin.com/v2/ugcPosts`
6. Click on it and check the Request Payload
7. Your author URN will be in the payload like: `"author": "urn:li:member:123456789"`
8. Copy the number (e.g., `123456789`)

### Method 3: Using Email Endpoint (If Available)

Run this command:
```bash
python get_person_urn.py
```

## Update .env File

Once you have your Person URN (the number), update `.env`:

```env
LINKEDIN_PERSON_URN=123456789
```

## Then Run

```bash
python auto_linkedin_poster.py --post-now
```

## Alternative: Use Browser Automation

If API doesn't work, use browser-based posting:

```bash
python linkedin_browser_fallback.py
```

This will open a browser and post automatically using your logged-in session.
