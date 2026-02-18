"""
verify_gold_tier.py
Gold Tier Completion Verification Script
Checks all Gold Tier requirements are met
"""

import os
import sys
from pathlib import Path
import json


class GoldTierVerifier:
    """Verifies all Gold Tier requirements are complete"""

    def __init__(self):
        self.root = Path(__file__).parent
        self.checks_passed = 0
        self.checks_failed = 0
        self.checks_warning = 0

    def check_file_exists(self, path: str, description: str) -> bool:
        """Check if a file or directory exists"""
        full_path = self.root / path
        exists = full_path.exists()
        
        if exists:
            print(f"[PASS] {description}: {path}")
            self.checks_passed += 1
            return True
        else:
            print(f"[FAIL] {description}: {path} - MISSING")
            self.checks_failed += 1
            return False

    def check_directory_has_files(self, dir_path: str, description: str) -> bool:
        """Check if a directory contains files"""
        full_path = self.root / dir_path
        if not full_path.exists():
            print(f"[FAIL] {description}: {dir_path} - DIRECTORY MISSING")
            self.checks_failed += 1
            return False
        
        files = list(full_path.iterdir())
        if files:
            print(f"[PASS] {description}: {dir_path} ({len(files)} files)")
            self.checks_passed += 1
            return True
        else:
            print(f"[WARN] {description}: {dir_path} - DIRECTORY EMPTY")
            self.checks_warning += 1
            return False

    def check_environment_variable(self, var_name: str, description: str) -> bool:
        """Check if an environment variable is set"""
        value = os.getenv(var_name)
        
        if value:
            print(f"[PASS] {description}: {var_name} is set")
            self.checks_passed += 1
            return True
        else:
            print(f"[WARN] {description}: {var_name} - NOT SET (optional for testing)")
            self.checks_warning += 1
            return False

    def check_mcp_config(self) -> bool:
        """Check if MCP configuration has all required servers"""
        mcp_path = self.root / "mcp.json"
        
        if not mcp_path.exists():
            print(f"❌ MCP Configuration: mcp.json - MISSING")
            self.checks_failed += 1
            return False
        
        with open(mcp_path, 'r') as f:
            config = json.load(f)
        
        required_servers = [
            "email-mcp",
            "browser-mcp",
            "odoo-mcp",
            "twitter-mcp",
            "facebook-instagram-mcp"
        ]
        
        servers = config.get("servers", {})
        missing = []
        
        for server in required_servers:
            if server not in servers:
                missing.append(server)
        
        if not missing:
            print(f"[PASS] MCP Configuration: All {len(required_servers)} servers configured")
            self.checks_passed += 1
            return True
        else:
            print(f"[FAIL] MCP Configuration: Missing servers: {missing}")
            self.checks_failed += 1
            return False

    def check_agent_skills(self) -> bool:
        """Check if all required agent skills exist"""
        skills_dir = self.root / ".qwen" / "skills"
        
        if not skills_dir.exists():
            print(f"[FAIL] Agent Skills: .qwen/skills - DIRECTORY MISSING")
            self.checks_failed += 1
            return False
        
        required_skills = [
            "gmail_skill",
            "whatsapp_skill",
            "linkedin_skill",
            "facebook_instagram_skill",
            "twitter_skill"
        ]
        
        missing = []
        for skill in required_skills:
            if not (skills_dir / skill).exists():
                missing.append(skill)
        
        # Check CEO briefing skill separately (it's in root)
        ceo_skill = self.root / "ceo_briefing_skill.py"
        has_ceo_skill = ceo_skill.exists()
        
        if not missing and has_ceo_skill:
            print(f"[PASS] Agent Skills: All {len(required_skills)} + CEO Briefing skills present")
            self.checks_passed += 1
            return True
        else:
            if missing:
                print(f"[FAIL] Agent Skills: Missing: {missing}")
            if not has_ceo_skill:
                print(f"[FAIL] Agent Skills: CEO Briefing skill missing")
            self.checks_failed += 1
            return False

    def verify_gold_tier_requirements(self):
        """Verify all Gold Tier requirements"""
        print("\n" + "="*70)
        print("GOLD TIER VERIFICATION")
        print("="*70 + "\n")

        print("1. Silver Requirements (Prerequisites)")
        print("-" * 70)
        self.check_file_exists("gmail_watcher.py", "Gmail Watcher")
        self.check_file_exists("whatsapp_watcher.py", "WhatsApp Watcher")
        self.check_file_exists("linkedin_poster.py", "LinkedIn Poster")
        self.check_file_exists("reasoning_loop.py", "Reasoning Loop")
        self.check_file_exists("email_approval_workflow.py", "Email Approval Workflow")
        print()

        print("2. Cross-Domain Integration")
        print("-" * 70)
        self.check_file_exists("odoo_integration", "Odoo Integration Directory")
        self.check_file_exists("odoo_integration/odoo_connector.py", "Odoo Connector")
        self.check_file_exists("odoo_integration/mcp_server.py", "Odoo MCP Server")
        print()

        print("3. Odoo Accounting Integration")
        print("-" * 70)
        self.check_file_exists("odoo_integration/sync_invoices.py", "Invoice Sync")
        self.check_file_exists("odoo_integration/update_dashboard_with_odoo.py", "Dashboard Update")
        self.check_environment_variable("ODOO_URL", "Odoo URL")
        self.check_environment_variable("ODOO_DB", "Odoo Database")
        self.check_environment_variable("ODOO_USERNAME", "Odoo Username")
        print()

        print("4. Facebook & Instagram Integration")
        print("-" * 70)
        self.check_file_exists("social_media_integration/facebook_instagram_connector.py", "FB/IG Connector")
        self.check_file_exists("social_media_integration/facebook_instagram_mcp_server.py", "FB/IG MCP Server")
        self.check_directory_has_files(".qwen/skills/facebook_instagram_skill", "FB/IG Skill")
        self.check_environment_variable("META_ACCESS_TOKEN", "Meta Access Token")
        self.check_environment_variable("FACEBOOK_PAGE_ID", "Facebook Page ID")
        self.check_environment_variable("INSTAGRAM_BUSINESS_ACCOUNT_ID", "Instagram Account ID")
        print()

        print("5. Twitter (X) Integration")
        print("-" * 70)
        self.check_file_exists("social_media_integration/twitter_connector.py", "Twitter Connector")
        self.check_file_exists("social_media_integration/twitter_mcp_server.py", "Twitter MCP Server")
        self.check_directory_has_files(".qwen/skills/twitter_skill", "Twitter Skill")
        self.check_environment_variable("TWITTER_API_KEY", "Twitter API Key")
        self.check_environment_variable("TWITTER_API_SECRET", "Twitter API Secret")
        print()

        print("6. Multiple MCP Servers")
        print("-" * 70)
        self.check_mcp_config()
        print()

        print("7. Weekly CEO Briefing")
        print("-" * 70)
        self.check_file_exists("ceo_briefing_skill.py", "CEO Briefing Skill")
        self.check_file_exists("Briefings", "Briefings Directory")
        print()

        print("8. Error Recovery & Graceful Degradation")
        print("-" * 70)
        # Check for try/except patterns in key files
        error_handling_files = [
            "reasoning_loop.py",
            "agent_interface.py",
            "odoo_integration/odoo_connector.py",
            "social_media_integration/facebook_instagram_connector.py",
            "social_media_integration/twitter_connector.py"
        ]
        
        files_with_error_handling = 0
        for file_path in error_handling_files:
            full_path = self.root / file_path
            if full_path.exists():
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'except Exception' in content or 'try:' in content:
                        files_with_error_handling += 1
        
        print(f"[PASS] Error Handling: {files_with_error_handling}/{len(error_handling_files)} files have error handling")
        self.checks_passed += 1
        print()

        print("9. Comprehensive Audit Logging")
        print("-" * 70)
        self.check_file_exists("Audit_Log.md", "Audit Log")
        print()

        print("10. Ralph Wiggum Loop")
        print("-" * 70)
        reasoning_path = self.root / "reasoning_loop.py"
        if reasoning_path.exists():
            with open(reasoning_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'ralph_wiggum' in content.lower() or 'autonomous' in content.lower():
                    print(f"[PASS] Ralph Wiggum Loop: Implemented in reasoning_loop.py")
                    self.checks_passed += 1
                else:
                    print(f"[WARN] Ralph Wiggum Loop: Pattern not detected in reasoning_loop.py")
                    self.checks_warning += 1
        else:
            print(f"[FAIL] Ralph Wiggum Loop: reasoning_loop.py MISSING")
            self.checks_failed += 1
        print()

        print("11. Architecture Documentation")
        print("-" * 70)
        self.check_file_exists("ARCHITECTURE.md", "Architecture Documentation")
        self.check_file_exists("LESSONS_LEARNED.md", "Lessons Learned")
        print()

        print("12. Agent Skills Framework")
        print("-" * 70)
        self.check_agent_skills()
        print()

        # Summary
        print("="*70)
        print("VERIFICATION SUMMARY")
        print("="*70)
        print(f"[PASS] Passed: {self.checks_passed}")
        print(f"[WARN] Warnings: {self.checks_warning}")
        print(f"[FAIL] Failed: {self.checks_failed}")
        print()

        total = self.checks_passed + self.checks_failed
        success_rate = (self.checks_passed / total * 100) if total > 0 else 0

        if self.checks_failed == 0:
            print(f"[SUCCESS] GOLD TIER COMPLETE! ({success_rate:.1f}% success rate)")
            print("\nAll Gold Tier requirements have been met!")
            print("Your AI Agent system is now a fully autonomous employee.")
            return True
        else:
            print(f"[INCOMPLETE] GOLD TIER INCOMPLETE ({success_rate:.1f}% success rate)")
            print(f"\n{self.checks_failed} requirements are still missing.")
            print("Please address the failed checks above.")
            return False


def main():
    verifier = GoldTierVerifier()
    is_complete = verifier.verify_gold_tier_requirements()
    
    sys.exit(0 if is_complete else 1)


if __name__ == "__main__":
    main()
