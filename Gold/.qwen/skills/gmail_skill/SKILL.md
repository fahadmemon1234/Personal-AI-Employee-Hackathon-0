# Gmail Watcher Skill

This skill monitors Gmail for new emails and processes them according to business rules.

## Purpose
- Monitor Gmail inbox for new messages
- Categorize emails based on content and sender
- Move important emails to Needs_Action folder for processing
- Support human-in-the-loop approval workflow

## Functionality
- Connects to Gmail using OAuth2 credentials
- Watches for new emails in specified folders
- Analyzes email content to determine priority
- Creates files in Needs_Action directory for important messages
- Implements approval workflow via Pending_Approval and Approved directories

## Configuration
Requires valid Gmail credentials in credentials.json and token.pickle files.

## Usage
This skill is automatically invoked by the watcher system when email processing is needed.