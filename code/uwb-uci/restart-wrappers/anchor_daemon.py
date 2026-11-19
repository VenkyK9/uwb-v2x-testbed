#!/usr/bin/env python3
# ----------------------------------------------------------------------------
# UWB_V2X
# Status : Ran on the Pis (as anchor_daemon1/2/3.py). Restarts the process only; it cannot revive a board that stopped answering.
# About  : Restart loop for an anchor (python3 anchor_daemon.py 0x1).
# ----------------------------------------------------------------------------
# anchor_daemon.py
import subprocess
import sys
import time
import signal

print("anchor_daemon.py starting...")

def run_ranging_session(mac):
    """Run a single ranging session, returns True on success, False on timeout"""
    try:
        subprocess.check_call([
            'python3', 'scripts/fira/run_fira_twr/run_fira_twr.py',
            '-t', '-1',
            '--node', 'onetomany',
            '--mac', mac,
            '--controlee'
        ])
        return True
    except subprocess.CalledProcessError as e:
        print(f"Session ended with error code {e.returncode}")
        return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 anchor_daemon.py <mac>")
        print("Example: python3 anchor_daemon.py 0x1")
        sys.exit(1)

    mac = sys.argv[1]
    restart_count = 0
    max_restarts = 100  # Unlimited for production

    print(f"Starting anchor {mac} daemon (max {max_restarts} restarts)")

    while restart_count < max_restarts:
        print(f"\n=== Starting session (attempt {restart_count + 1}) ===")
        success = run_ranging_session(mac)

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
