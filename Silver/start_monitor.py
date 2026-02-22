"""
Start LinkedIn Auto-Poster Monitor
Simple wrapper to start the monitoring process
"""

from auto_linkedin_poster import AutoLinkedInPoster
import sys

def main():
    print("="*60)
    print("  LinkedIn Auto-Poster Monitor")
    print("="*60)
    
    poster = AutoLinkedInPoster()
    
    # Show status
    print("\nCurrent Status:")
    print(f"   Access Token: {'OK' if poster.access_token else 'Missing/Expired'}")
    print(f"   Person URN: {poster.person_urn if poster.person_urn else 'Not set'}")
    
    pending = list(poster.pending_dir.glob("linkedin_post_*.txt"))
    print(f"   Pending Posts: {len(pending)}")
    
    approval = poster.has_approval()
    print(f"   Approval Status: {'Approved (ready to post)' if approval else 'Waiting for approval'}")
    
    print("\n" + "="*60)
    print("Starting monitor... Press Ctrl+C to stop\n")
    
    # Start monitoring (30 second intervals)
    poster.monitor(check_interval=30)

if __name__ == "__main__":
    main()
