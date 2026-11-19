#!/usr/bin/env python3
# ----------------------------------------------------------------------------
# UWB_V2X
# Status : Proposed. No run is recorded.
# About  : Restart loop for a tag.
# ----------------------------------------------------------------------------
# tag_daemon.py
import subprocess
import sys
import time

def run_tag_session():
    """Run a single TAG ranging session, returns True on success, False on timeout"""
    try:
        subprocess.check_call([
            'python3', 'scripts/fira/run_fira_twr/run_fira_twr.py',
            '-t', '-1',
            '--node', 'onetomany',
            '--dest-mac', '[0x1,0x2,0x3]',
            '--n_controlees', '3'
        ])
        return True
    except subprocess.CalledProcessError as e:
        print(f"Session ended with error code {e.returncode}")
        return False

def main():
    restart_count = 0
    max_restarts = 100  # Unlimited for production

    print("Starting TAG daemon (max 100 restarts)")

    while restart_count < max_restarts:
        print(f"\n=== Starting session (attempt {restart_count + 1}) ===")
        success = run_tag_session()

        if success:
            print("Session completed successfully")
            restart_count += 1
            if restart_count >= max_restarts:
                print("Max restarts reached. Exiting cleanly.")
                sys.exit(0)
            print(f"Restarting in 2 seconds...")
            time.sleep(2)
        else:
            print(f"Session failed, restarting immediately...")
            restart_count += 1
            time.sleep(1)  # Brief delay before restart

if __name__ == '__main__':
    main()
