#!/usr/bin/env python3
"""
Scheduler to run upload_shorts.py twice per day.
Runs at 9:00 AM and 9:00 PM (configurable).
"""

import os
import schedule
import time
import subprocess
from datetime import datetime

# Schedule times (24-hour format)
MORNING_TIME = "09:00"
EVENING_TIME = "21:00"


def run_upload_script():
    """Run the upload script."""
    print(f'\n[{datetime.now()}] Running scheduled upload...')
    try:
        result = subprocess.run(
            ['python3', 'upload_shorts.py'],
            cwd=os.path.dirname(os.path.abspath(__file__)),
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.stderr:
            print(f'Errors: {result.stderr}')
    except Exception as e:
        print(f'Error running upload script: {e}')


def main():
    """Set up and run the scheduler."""
    print('Setting up scheduler...')
    print(f'Uploads scheduled for: {MORNING_TIME} and {EVENING_TIME}')
    
    # Schedule twice daily
    schedule.every().day.at(MORNING_TIME).do(run_upload_script)
    schedule.every().day.at(EVENING_TIME).do(run_upload_script)
    
    print('Scheduler started. Press Ctrl+C to stop.')
    
    # Run immediately on start (optional)
    # run_upload_script()
    
    # Keep running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute


if __name__ == '__main__':
    import os
    main()

