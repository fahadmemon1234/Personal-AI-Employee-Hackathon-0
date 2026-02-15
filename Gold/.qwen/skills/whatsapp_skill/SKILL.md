# WhatsApp Watcher Skill

This skill monitors WhatsApp for new messages and processes them according to business rules.

## Purpose
- Monitor WhatsApp for new messages
- Categorize messages based on content and sender
- Move important messages to Needs_Action folder for processing
- Support human-in-the-loop approval workflow

## Functionality
- Connects to WhatsApp using appropriate API or interface
- Watches for new messages in specified chats
- Analyzes message content to determine priority
- Creates files in Needs_Action directory for important messages
- Implements approval workflow via Pending_Approval and Approved directories

## Configuration
Requires valid WhatsApp Business API credentials or appropriate connection setup.

## Usage
This skill is automatically invoked by the watcher system when WhatsApp message processing is needed.