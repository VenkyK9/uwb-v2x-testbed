#!/usr/bin/env python3
# ----------------------------------------------------------------------------
# UWB_V2X
# Status : Proposed. No run is recorded. Review note: it passes env={'UQT_PORT': port} only, which removes PATH and the rest of the environment from the child process.
# About  : Wrapper that restarts run_fira_twr.py for an anchor when it exits with an error.
# ----------------------------------------------------------------------------
# anchor_continuous.py
import subprocess
import time
import sys

def run_anchor(mac, port, max_restarts=10):
    restart_count = 0

    while restart_count < max_restarts:
        try:
            print(f"Starting anchor {mac} on {port}... (attempt {restart_count+1})")
            subprocess.check_call([
                'python3', 'scripts/fira/run_fira_twr/run_fira_twr.py',
                '-t', '-1',
                '--node', 'onetomany',
                '--mac', mac,
                '--controlee'
            ], env={'UQT_PORT': port})
        except subprocess.CalledProcessError as e:
            print(f"Session ended with error: {e}")
            restart_count += 1
            if restart_count >= max_restarts:
                print("Max restarts reached. Exiting.")
                return
            print(f"Restarting in 2 seconds... ({restart_count})")
            time.sleep(2)
        except KeyboardInterrupt:
            print("Stopped by user")
            return

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python3 anchor_continuous.py <mac> <port>")
        print("Example: python3 anchor_continuous.py 0x1 /dev/ttyACM1")
        sys.exit(1)

    mac = sys.argv[1]
    port = sys.argv[2]
    run_anchor(mac, port)
