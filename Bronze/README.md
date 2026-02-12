# AI Agent Bronze Tier Implementation

Congratulations! You've reached the Bronze Tier of your AI Agent system. This implementation includes:

## Components

### 1. Dashboard (Dashboard.md)
- Shows bank balances and tasks
- Provides quick access to important functions
- Tracks system status and activity

### 2. Company Handbook (Company_Handbook.md)
- Contains "Rules of Engagement"
- Outlines operational guidelines
- Defines decision matrix and emergency procedures

### 3. Inbox Watcher Script (watcher.py)
- Monitors the `/Inbox` folder for new files
- Automatically moves new files to `/Needs_Action` folder
- Logs all actions for audit trail
- Built using the BaseWatcher pattern

## Setup Instructions

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the watcher script:
   ```bash
   python watcher.py
   ```

3. Place files in the `Inbox` folder to be automatically processed

## Directory Structure
```
├── Dashboard.md          # Main dashboard showing status and tasks
├── Company_Handbook.md   # Rules of engagement and operational guidelines
├── watcher.py           # Python script that monitors Inbox folder
├── requirements.txt     # Dependencies
├── Inbox/              # Folder monitored by the watcher
├── Needs_Action/       # Destination for files moved by watcher
└── watcher_log.txt     # Log of all file movements
```

## Usage

1. Place any files you want processed in the `Inbox` folder
2. The watcher will automatically move them to `Needs_Action`
3. Check `watcher_log.txt` for a record of all actions
4. Update `Dashboard.md` with current information as needed

## Agent Skill Implementation

The system is designed to proactively read from and write to your vault (the current directory):

- **Reading**: The watcher monitors the Inbox folder continuously
- **Writing**: Files are moved to Needs_Action, logs are written, and dashboards can be updated
- **Automation**: The system operates independently once started