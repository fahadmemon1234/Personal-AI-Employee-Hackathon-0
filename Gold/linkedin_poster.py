import os
import json
import datetime
from pathlib import Path

class LinkedInPoster:
    def __init__(self):
        self.pending_approval_dir = Path("Pending_Approval")
        self.approved_dir = Path("Approved")
        self.dashboard_file = "Dashboard.md"
        self.company_handbook_rules = self.load_company_handbook_rules()

        # Create directories if they don't exist
        self.pending_approval_dir.mkdir(exist_ok=True)
        self.approved_dir.mkdir(exist_ok=True)

    def load_company_handbook_rules(self):
        """Load and validate LinkedIn posting rules from Company Handbook"""
        handbook_path = Path("Company_Handbook.md")
        rules = {
            "allowed_topics": [],
            "forbidden_topics": [],
            "tone_guidelines": "professional",
            "hashtag_policy": "#AI #Automation #Innovation",
            "content_length_limit": 3000  # LinkedIn's character limit
        }

        if handbook_path.exists():
            with open(handbook_path, 'r', encoding='utf-8') as f:
                handbook_content = f.read().lower()

            # Extract rules based on handbook content
            if "communication protocols" in handbook_content:
                rules["tone_guidelines"] = "professional and clear"
            if "efficiency" in handbook_content:
                rules["allowed_topics"].append("efficiency")
            if "automation" in handbook_content:
                rules["allowed_topics"].append("automation")
            if "ai" in handbook_content:
                rules["allowed_topics"].append("ai")
            if "machine learning" in handbook_content:
                rules["allowed_topics"].append("machine learning")

        return rules

    def validate_post_content(self, content):
        """Validate post content against Company Handbook Rules of Engagement"""
        errors = []

        # Check for sensitive information
        sensitive_patterns = ["password", "credit card", "ssn", "social security", "confidential"]
        for pattern in sensitive_patterns:
            if pattern.lower() in content.lower():
                errors.append(f"Post contains sensitive information: {pattern}")

        # Check content length
        if len(content) > self.company_handbook_rules["content_length_limit"]:
            errors.append(f"Post exceeds character limit ({len(content)}/{self.company_handbook_rules['content_length_limit']})")

        # Check for appropriate topics based on handbook
        content_lower = content.lower()
        has_allowed_topic = any(topic in content_lower for topic in self.company_handbook_rules["allowed_topics"])
        if not has_allowed_topic and len(self.company_handbook_rules["allowed_topics"]) > 0:
            errors.append(f"Post should include one of the allowed topics: {', '.join(self.company_handbook_rules['allowed_topics'])}")

        return errors

    def create_draft_post(self, content=None):
        """Create a draft LinkedIn post in Pending_Approval directory following Company Handbook rules"""
        if content is None:
            # Generate a sample AI services update following handbook guidelines
            today = datetime.datetime.now().strftime("%Y-%m-%d")
            content = f"Daily AI Services Update - {today}\n\nExciting developments in our AI solutions today! Our team is continuously improving our machine learning models and enhancing our automation capabilities following our core principles of efficiency and data integrity.\n\n#AI #Automation #Efficiency #Innovation"

        # Validate the content against handbook rules
        validation_errors = self.validate_post_content(content)
        if validation_errors:
            print("Validation errors found in LinkedIn post:")
            for error in validation_errors:
                print(f"  - {error}")
            print("Please revise the content to comply with Company Handbook rules.")
            return None

        # Create a unique filename for the draft
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"linkedin_post_{timestamp}.txt"
        filepath = self.pending_approval_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"Draft LinkedIn post created following Company Handbook rules: {filepath}")
        return filepath
    
    def execute_approved_post(self, post_file):
        """Execute the LinkedIn post after approval"""
        # Read the post content
        with open(post_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Re-validate the content against handbook rules before posting
        validation_errors = self.validate_post_content(content)
        if validation_errors:
            print("Validation errors found in approved LinkedIn post:")
            for error in validation_errors:
                print(f"  - {error}")
            print("This post does not comply with Company Handbook rules and will not be posted.")
            # Move to a rejected folder instead
            rejected_path = Path("Rejected") / post_file.name
            rejected_path.parent.mkdir(exist_ok=True)
            post_file.rename(rejected_path)
            print(f"Non-compliant post moved to: {rejected_path}")
            return False

        # In a real implementation, this would connect to LinkedIn API
        # For now, we'll simulate posting and log the activity
        print(f"Executing LinkedIn post: {content[:100]}...")

        # Log the post in Dashboard.md
        self.log_post_in_dashboard(content)

        # Move the file to archive after posting
        archive_path = Path("Posted") / post_file.name
        archive_path.parent.mkdir(exist_ok=True)
        post_file.rename(archive_path)

        print(f"LinkedIn post executed and archived: {archive_path}")
        return True
    
    def log_post_in_dashboard(self, content):
        """Log the LinkedIn post in Dashboard.md"""
        # Create dashboard entry
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"\n### LinkedIn Post - {timestamp}\n{content}\n\n---\n"
        
        # Append to Dashboard.md
        with open(self.dashboard_file, 'a', encoding='utf-8') as f:
            f.write(entry)
    
    def check_for_approved_posts(self):
        """Check for posts that have been approved and execute them"""
        approved_posts = list(self.approved_dir.glob("*.txt"))

        for post_file in approved_posts:
            print(f"Found approved post: {post_file}")
            success = self.execute_approved_post(post_file)
            if success:
                print(f"Successfully posted: {post_file.name}")
            else:
                print(f"Failed to post (validation error): {post_file.name}")
    
    def schedule_daily_post(self):
        """Schedule a daily LinkedIn post"""
        # Create a draft for today's post
        self.create_draft_post()


def main():
    poster = LinkedInPoster()
    
    # Check for any approved posts to execute
    poster.check_for_approved_posts()
    
    # Create a new daily draft post
    poster.schedule_daily_post()


if __name__ == "__main__":
    main()