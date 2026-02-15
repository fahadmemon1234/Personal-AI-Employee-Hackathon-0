import os
import shutil
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime


class BaseWatcher:
    """Base class for file system watchers"""
    
    def __init__(self, watch_dir, dest_dir):
        self.watch_dir = watch_dir
        self.dest_dir = dest_dir
        
    def process_file(self, file_path):
        """Process a file when it appears in the watched directory"""
        raise NotImplementedError("Subclasses must implement process_file method")
    
    def setup_directories(self):
        """Ensure required directories exist"""
        os.makedirs(self.watch_dir, exist_ok=True)
        os.makedirs(self.dest_dir, exist_ok=True)


class InboxWatcher(BaseWatcher):
    """Watches the Inbox folder and moves new files to Needs_Action"""
    
    def __init__(self, watch_dir="Inbox", dest_dir="Needs_Action"):
        super().__init__(watch_dir, dest_dir)
        self.setup_directories()
        
    def process_file(self, file_path):
        """Move the file to the Needs_Action directory"""
        filename = os.path.basename(file_path)
        dest_path = os.path.join(self.dest_dir, filename)
        
        # Handle duplicate filenames by adding timestamp
        if os.path.exists(dest_path):
            name, ext = os.path.splitext(filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            dest_path = os.path.join(self.dest_dir, f"{name}_{timestamp}{ext}")
        
        shutil.move(file_path, dest_path)
        print(f"[{datetime.now()}] Moved {filename} from {self.watch_dir} to {self.dest_dir}")
        
        # Log the action
        self.log_action(file_path, dest_path)
        
    def log_action(self, source_path, dest_path):
        """Log the file movement action"""
        log_entry = f"[{datetime.now()}] FILE_MOVED: {source_path} -> {dest_path}\n"
        
        with open("watcher_log.txt", "a") as log_file:
            log_file.write(log_entry)


class InboxHandler(FileSystemEventHandler):
    """Handles file system events for the Inbox directory"""
    
    def __init__(self, watcher):
        self.watcher = watcher
        
    def on_created(self, event):
        """Handle file creation events"""
        if not event.is_directory:
            print(f"[{datetime.now()}] New file detected: {event.src_path}")
            self.watcher.process_file(event.src_path)
            
    def on_moved(self, event):
        """Handle file move events"""
        if not event.is_directory:
            print(f"[{datetime.now()}] File moved into inbox: {event.src_path}")
            self.watcher.process_file(event.src_path)


def main():
    """Main function to start the watcher"""
    watcher = InboxWatcher(watch_dir="Inbox", dest_dir="Needs_Action")
    event_handler = InboxHandler(watcher)
    
    observer = Observer()
    observer.schedule(event_handler, path=watcher.watch_dir, recursive=False)
    
    print(f"[{datetime.now()}] Starting Inbox Watcher...")
    print(f"Monitoring: {watcher.watch_dir}")
    print(f"Moving files to: {watcher.dest_dir}")
    
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print(f"\n[{datetime.now()}] Stopping Inbox Watcher...")
    
    observer.join()
    print(f"[{datetime.now()}] Inbox Watcher stopped.")


if __name__ == "__main__":
    main()