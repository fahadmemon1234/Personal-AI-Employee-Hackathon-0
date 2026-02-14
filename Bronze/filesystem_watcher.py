import os
import time
import shutil
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class InboxHandler(FileSystemEventHandler):
    def __init__(self, inbox_dir, needs_action_dir):
        self.inbox_dir = inbox_dir
        self.needs_action_dir = needs_action_dir

    def on_created(self, event):
        if not event.is_directory:
            self.process_new_file(event.src_path)

    def on_moved(self, event):
        if not event.is_directory and event.event_type == 'created':
            self.process_new_file(event.dest_path)

    def process_new_file(self, file_path):
        """Process a new file by moving it to Needs_Action and creating metadata."""
        try:
            # Wait a moment to ensure file is completely written
            time.sleep(0.5)
            
            # Get the filename
            filename = os.path.basename(file_path)
            
            # Define destination path
            dest_path = os.path.join(self.needs_action_dir, filename)
            
            # Move the file to Needs_Action
            shutil.move(file_path, dest_path)
            
            # Create metadata file
            self.create_metadata_file(dest_path, filename)
            
            print(f"Moved {filename} to Needs_Action and created metadata.")
            
        except Exception as e:
            print(f"Error processing file {file_path}: {str(e)}")

    def create_metadata_file(self, file_path, original_filename):
        """Create a metadata file for the moved file."""
        # Create metadata content
        metadata_content = f"""# Metadata for {original_filename}

## File Information
- Original Location: Inbox
- Moved to: Needs_Action
- Date Processed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- File Size: {os.path.getsize(file_path)} bytes
- File Type: {os.path.splitext(original_filename)[1]}

## Action Required
- Review the file content
- Determine appropriate action
- Move to Done when completed
"""

        # Create metadata file with same name but .md extension
        base_name = os.path.splitext(original_filename)[0]
        metadata_filename = f"{base_name}_metadata.md"
        metadata_path = os.path.join(self.needs_action_dir, metadata_filename)
        
        # Write metadata file
        with open(metadata_path, 'w', encoding='utf-8') as f:
            f.write(metadata_content)


def start_watching(inbox_dir, needs_action_dir):
    """Start watching the inbox directory for new files."""
    event_handler = InboxHandler(inbox_dir, needs_action_dir)
    observer = Observer()
    observer.schedule(event_handler, inbox_dir, recursive=False)
    
    observer.start()
    print(f"Started watching {inbox_dir}")
    print(f"Files will be moved to {needs_action_dir}")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("File watcher stopped.")
    
    observer.join()


if __name__ == "__main__":
    # Define directory paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    INBOX_DIR = os.path.join(current_dir, "Inbox")
    NEEDS_ACTION_DIR = os.path.join(current_dir, "Needs_Action")
    
    # Create directories if they don't exist
    os.makedirs(INBOX_DIR, exist_ok=True)
    os.makedirs(NEEDS_ACTION_DIR, exist_ok=True)
    
    # Start watching
    start_watching(INBOX_DIR, NEEDS_ACTION_DIR)