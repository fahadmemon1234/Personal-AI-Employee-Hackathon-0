import os
from pathlib import Path

# Test if Audit_Log.md exists and has content
audit_log_path = Path("Audit_Log.md")

if audit_log_path.exists():
    print("Audit_Log.md exists!")
    with open(audit_log_path, 'r', encoding='utf-8') as f:
        content = f.read()
        print(f"Audit log has {len(content)} characters")
        if content:
            print("Last few lines of audit log:")
            lines = content.split('\n')[-5:]  # Get last 5 lines
            for line in lines:
                if line.strip():
                    print(f"  {line}")
else:
    print("Audit_Log.md does not exist yet")

# Check if the Plans directory was created
plans_dir = Path("Plans")
if plans_dir.exists():
    plan_files = list(plans_dir.glob("*.md"))
    print(f"\nPlans directory exists with {len(plan_files)} plan files")
else:
    print("\nPlans directory does not exist")

# Check if the Approved directory exists
approved_dir = Path("Approved")
if approved_dir.exists():
    approved_files = list(approved_dir.glob("*"))
    print(f"Approved directory exists with {len(approved_files)} files")
else:
    print("Approved directory does not exist")

# Check if the Posted directory exists  
posted_dir = Path("Posted")
if posted_dir.exists():
    posted_files = list(posted_dir.glob("*"))
    print(f"Posted directory exists with {len(posted_files)} files")
else:
    print("Posted directory does not exist")