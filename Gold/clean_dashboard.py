#!/usr/bin/env python3
"""
Script to clean up the Dashboard.md file by removing duplicate entries
in the 'Current Active Plans' section.
"""

import re
from pathlib import Path

def clean_dashboard_duplicates():
    dashboard_path = Path("Dashboard.md")
    
    # Read the dashboard content
    with open(dashboard_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split content into parts: before, active plans section, and after
    parts = content.split('## Current Active Plans')
    
    if len(parts) < 2:
        print("No 'Current Active Plans' section found.")
        return
    
    # Keep the part before the active plans section
    result_parts = [parts[0]]
    
    # Process the active plans section and everything after
    active_plans_and_rest = '## Current Active Plans' + '## Current Active Plans'.join(parts[1:])
    
    # Find the end of the active plans section (before the next heading)
    lines = active_plans_and_rest.split('\n')
    
    new_lines = []
    active_plans_lines = []
    in_active_plans_section = True
    plan_links_seen = set()
    
    for line in lines:
        # Check if we're moving to a new section
        if line.strip().startswith('## ') and not line.strip().startswith('## Current Active Plans'):
            in_active_plans_section = False
        
        if in_active_plans_section and '- [' in line and '](' in line:
            # This is a plan link line, check if it's a duplicate
            if line.strip() in plan_links_seen:
                print(f"Removing duplicate: {line.strip()}")
                continue  # Skip this duplicate line
            else:
                plan_links_seen.add(line.strip())
                active_plans_lines.append(line)
        else:
            if in_active_plans_section and line.strip() == '':
                # Keep empty lines within the active plans section
                active_plans_lines.append(line)
            else:
                # We've exited the active plans section, add remaining lines
                if not in_active_plans_section:
                    active_plans_lines.append(line)
    
    # Reconstruct the content
    result_parts.append('## Current Active Plans\n')
    result_parts.extend(active_plans_lines)
    
    # Join everything back together
    new_content = ''.join(result_parts)
    
    # Write the cleaned content back to the file
    with open(dashboard_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"Dashboard cleaned. Removed duplicate entries from 'Current Active Plans' section.")

if __name__ == "__main__":
    clean_dashboard_duplicates()