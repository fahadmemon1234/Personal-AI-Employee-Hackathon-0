"""
Agent Interface for Bronze Tier Workspace Management
Registers folder management tasks as official Agent Skills
"""

import os
import json
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class FolderManagementSkills:
    """
    Class containing folder management skills for the AI agent
    """
    
    def __init__(self, base_dir=None):
        self.base_dir = base_dir or os.path.dirname(os.path.abspath(__file__))
        self.inbox_dir = os.path.join(self.base_dir, "Inbox")
        self.needs_action_dir = os.path.join(self.base_dir, "Needs_Action")
        self.done_dir = os.path.join(self.base_dir, "Done")
        
        # Create directories if they don't exist
        for directory in [self.inbox_dir, self.needs_action_dir, self.done_dir]:
            os.makedirs(directory, exist_ok=True)
    
    def move_file_to_needs_action(self, file_path):
        """
        Skill: Move a file from any location to Needs_Action folder
        """
        try:
            filename = os.path.basename(file_path)
            dest_path = os.path.join(self.needs_action_dir, filename)
            os.rename(file_path, dest_path)
            
            # Create metadata
            self._create_file_metadata(dest_path, filename, "Moved to Needs_Action")
            
            return {
                "success": True,
                "message": f"File {filename} moved to Needs_Action",
                "destination": dest_path
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error moving file: {str(e)}"
            }
    
    def move_file_to_done(self, file_path):
        """
        Skill: Move a file from Needs_Action to Done folder
        """
        try:
            filename = os.path.basename(file_path)
            dest_path = os.path.join(self.done_dir, filename)
            os.rename(file_path, dest_path)
            
            # Create completion metadata
            self._create_file_metadata(dest_path, filename, "Completed and moved to Done")
            
            return {
                "success": True,
                "message": f"File {filename} moved to Done",
                "destination": dest_path
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error moving file to Done: {str(e)}"
            }
    
    def list_inbox_files(self):
        """
        Skill: List all files in the Inbox folder
        """
        try:
            files = os.listdir(self.inbox_dir)
            return {
                "success": True,
                "files": files,
                "count": len(files)
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error listing Inbox files: {str(e)}"
            }
    
    def list_needs_action_files(self):
        """
        Skill: List all files in the Needs_Action folder
        """
        try:
            files = os.listdir(self.needs_action_dir)
            return {
                "success": True,
                "files": files,
                "count": len(files)
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error listing Needs_Action files: {str(e)}"
            }
    
    def list_done_files(self):
        """
        Skill: List all files in the Done folder
        """
        try:
            files = os.listdir(self.done_dir)
            return {
                "success": True,
                "files": files,
                "count": len(files)
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error listing Done files: {str(e)}"
            }
    
    def _create_file_metadata(self, file_path, original_filename, action_taken):
        """
        Private method to create metadata for processed files
        """
        metadata_content = f"""# Metadata for {original_filename}

## Processing Information
- Action Taken: {action_taken}
- Date Processed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- File Size: {os.path.getsize(file_path)} bytes
- File Type: {os.path.splitext(original_filename)[1]}
"""

        # Create metadata file with same name but .md extension
        base_name = os.path.splitext(original_filename)[0]
        metadata_filename = f"{base_name}_metadata.md"
        metadata_path = os.path.join(
            os.path.dirname(file_path), 
            metadata_filename
        )
        
        # Write metadata file
        with open(metadata_path, 'w', encoding='utf-8') as f:
            f.write(metadata_content)


# Initialize the skills module
folder_skills = FolderManagementSkills()


def get_registered_skills():
    """
    Returns a dictionary of all registered folder management skills
    """
    return {
        "move_file_to_needs_action": folder_skills.move_file_to_needs_action,
        "move_file_to_done": folder_skills.move_file_to_done,
        "list_inbox_files": folder_skills.list_inbox_files,
        "list_needs_action_files": folder_skills.list_needs_action_files,
        "list_done_files": folder_skills.list_done_files
    }


if __name__ == "__main__":
    print("Folder Management Skills registered and ready!")
    print("Available skills:")
    for skill_name in get_registered_skills().keys():
        print(f"- {skill_name}")