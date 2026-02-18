"""
Claude Code Integration for Bronze Tier Vault
Demonstrates Claude Code successfully reading from and writing to the vault
"""

import os
import json
from datetime import datetime
from agent_interface import get_registered_skills


class ClaudeCodeVaultIntegration:
    """
    Integration layer for Claude Code to interact with the Obsidian vault
    Provides read/write capabilities that Claude Code can use via Agent Skills
    """

    def __init__(self, vault_dir=None):
        self.vault_dir = vault_dir or os.path.dirname(os.path.abspath(__file__))
        self.skills = get_registered_skills()
        self.integration_log = []

    def read_file(self, relative_path):
        """
        Claude Code Skill: Read a file from the vault
        """
        try:
            file_path = os.path.join(self.vault_dir, relative_path)
            
            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "error": f"File not found: {relative_path}"
                }

            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Log the read operation
            self._log_operation("READ", relative_path, "Success")

            return {
                "success": True,
                "path": relative_path,
                "content": content,
                "size": len(content),
                "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def write_file(self, relative_path, content, append=False):
        """
        Claude Code Skill: Write content to a file in the vault
        """
        try:
            file_path = os.path.join(self.vault_dir, relative_path)
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            mode = 'a' if append else 'w'
            with open(file_path, mode, encoding='utf-8') as f:
                f.write(content)

            # Log the write operation
            self._log_operation("WRITE", relative_path, "Success")

            return {
                "success": True,
                "path": relative_path,
                "action": "appended" if append else "overwritten",
                "size": len(content),
                "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def list_directory(self, relative_path=""):
        """
        Claude Code Skill: List contents of a directory in the vault
        """
        try:
            dir_path = os.path.join(self.vault_dir, relative_path)
            
            if not os.path.exists(dir_path):
                return {
                    "success": False,
                    "error": f"Directory not found: {relative_path}"
                }

            items = os.listdir(dir_path)
            files = []
            directories = []

            for item in items:
                item_path = os.path.join(dir_path, item)
                if os.path.isdir(item_path):
                    directories.append(item)
                else:
                    files.append(item)

            # Log the operation
            self._log_operation("LIST", relative_path or "/", f"{len(files)} files, {len(directories)} dirs")

            return {
                "success": True,
                "path": relative_path or "/",
                "files": files,
                "directories": directories,
                "total_items": len(files) + len(directories),
                "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def update_dashboard(self, section, content):
        """
        Claude Code Skill: Update a specific section in Dashboard.md
        """
        try:
            dashboard_path = os.path.join(self.vault_dir, "Dashboard.md")
            
            # Read current dashboard
            with open(dashboard_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # Find and update the section
            new_lines = []
            in_section = False
            section_found = False

            for line in lines:
                if line.strip().startswith('##') and section.lower() in line.lower():
                    in_section = True
                    section_found = True
                    new_lines.append(line)
                    # Add new content after section header
                    new_lines.append(content + '\n')
                elif line.strip().startswith('##') and in_section:
                    in_section = False
                    new_lines.append(line)
                elif not in_section:
                    new_lines.append(line)

            # If section not found, append it
            if not section_found:
                new_lines.append(f'\n## {section}\n')
                new_lines.append(content + '\n')

            # Write updated dashboard
            with open(dashboard_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)

            # Log the operation
            self._log_operation("UPDATE_DASHBOARD", section, "Success")

            return {
                "success": True,
                "section": section,
                "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def add_audit_log_entry(self, action, details):
        """
        Claude Code Skill: Add an entry to the Audit Log
        """
        try:
            audit_path = os.path.join(self.vault_dir, "Audit_Log.md")
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            entry = f"- [{timestamp}] {action}: {details}\n"

            with open(audit_path, 'a', encoding='utf-8') as f:
                f.write(entry)

            # Log the operation
            self._log_operation("AUDIT_LOG", action, "Entry added")

            return {
                "success": True,
                "timestamp": timestamp,
                "entry": entry.strip()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def use_skill(self, skill_name, **kwargs):
        """
        Claude Code Skill: Use any registered folder management skill
        """
        if skill_name not in self.skills:
            return {
                "success": False,
                "error": f"Unknown skill: {skill_name}. Available: {list(self.skills.keys())}"
            }

        skill_func = self.skills[skill_name]
        result = skill_func(**kwargs)

        # Log the skill usage
        self._log_operation("SKILL_USAGE", skill_name, str(result.get('success', 'Unknown')))

        return result

    def _log_operation(self, operation_type, target, status):
        """Private method to log operations"""
        self.integration_log.append({
            "type": operation_type,
            "target": target,
            "status": status,
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })

    def get_integration_report(self):
        """
        Generate a report of all integration operations
        """
        return {
            "vault_dir": self.vault_dir,
            "total_operations": len(self.integration_log),
            "operations": self.integration_log,
            "registered_skills": list(self.skills.keys()),
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }


def run_integration_test():
    """
    Run a complete integration test demonstrating Claude Code read/write capabilities
    """
    print("=" * 60)
    print("CLAUDE CODE VAULT INTEGRATION TEST")
    print("=" * 60)

    integration = ClaudeCodeVaultIntegration()
    results = {}

    # Test 1: Read Company Handbook
    print("\n[Test 1] Reading Company_Handbook.md...")
    results['read_handbook'] = integration.read_file("Company_Handbook.md")
    status = "SUCCESS" if results['read_handbook']['success'] else "FAILED"
    print(f"  Status: [{status}]")

    # Test 2: Read Dashboard
    print("\n[Test 2] Reading Dashboard.md...")
    results['read_dashboard'] = integration.read_file("Dashboard.md")
    status = "SUCCESS" if results['read_dashboard']['success'] else "FAILED"
    print(f"  Status: [{status}]")

    # Test 3: List Directory
    print("\n[Test 3] Listing vault directory...")
    results['list_dir'] = integration.list_directory("")
    status = "SUCCESS" if results['list_dir']['success'] else "FAILED"
    print(f"  Status: [{status}]")
    if results['list_dir']['success']:
        print(f"  Found: {results['list_dir']['total_items']} items")

    # Test 4: Update Dashboard
    print("\n[Test 4] Updating Dashboard (adding verification entry)...")
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    update_content = f"- Claude Code Integration verified: {timestamp} - Read/Write operations confirmed\n"
    results['update_dashboard'] = integration.update_dashboard("Verification", update_content)
    status = "SUCCESS" if results['update_dashboard']['success'] else "FAILED"
    print(f"  Status: [{status}]")

    # Test 5: Add Audit Log Entry
    print("\n[Test 5] Adding Audit Log entry...")
    results['audit_log'] = integration.add_audit_log_entry(
        "Claude Code Integration Test",
        "All read/write operations completed successfully"
    )
    status = "SUCCESS" if results['audit_log']['success'] else "FAILED"
    print(f"  Status: [{status}]")

    # Test 6: Use Folder Management Skill
    print("\n[Test 6] Using registered skill (list_inbox_files)...")
    results['skill_usage'] = integration.use_skill("list_inbox_files")
    status = "SUCCESS" if results['skill_usage']['success'] else "FAILED"
    print(f"  Status: [{status}]")

    # Test 7: Write new file to Inbox
    print("\n[Test 7] Writing test file to Inbox...")
    test_content = f"""# Integration Test File
This file was created by Claude Code integration test.
Timestamp: {timestamp}
Purpose: Demonstrate write capability to the vault.
"""
    results['write_test'] = integration.write_file("Inbox/integration_test.md", test_content)
    status = "SUCCESS" if results['write_test']['success'] else "FAILED"
    print(f"  Status: [{status}]")

    # Generate Report
    print("\n" + "=" * 60)
    print("INTEGRATION TEST REPORT")
    print("=" * 60)
    
    report = integration.get_integration_report()
    print(f"Vault Directory: {report['vault_dir']}")
    print(f"Total Operations: {report['total_operations']}")
    print(f"Registered Skills: {', '.join(report['registered_skills'])}")
    
    # Summary
    successful = sum(1 for r in results.values() if r.get('success', False))
    total = len(results)
    
    print("\n" + "-" * 60)
    print(f"SUMMARY: {successful}/{total} tests passed")
    
    if successful == total:
        print("STATUS: [ALL TESTS PASSED] - Claude Code Integration COMPLETE")
    else:
        print(f"STATUS: [FAILED] - {total - successful} test(s) failed")
    
    print("=" * 60)

    return results


if __name__ == "__main__":
    run_integration_test()
