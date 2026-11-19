#!/bin/bash
# ----------------------------------------------------------------------------
# UWB_V2X
# Status : Ran (attempt 3). Anchors still reported RangingRxMacIeDecFailed (0x26).
# About  : No background jobs: -t 3 bounded runs, SSH heredoc, -s for the session, fixed ports.
# ----------------------------------------------------------------------------

# ---> SET JETSON 2 IP HERE <---
JETSON2_USER_IP="jetson2@192.168.X.X"

echo "Starting Round-Robin UWB TWR..."

while true; do
    echo "--- Initiating TAG 1 (Jetson 1) ---"
    cd /home/jetson1/uwb-qorvo-tools
    source /home/jetson1/uwb_venv/bin/activate
    # -t 3 tells Python to gracefully stop after 3 seconds without needing a keyboard hit
    python3 scripts/fira/run_fira_twr/run_fira_twr.py -p /dev/ttyACM1 -t 3 --node onetomany --mac 0x4 -s 1 --dest-mac '[0x1,0x2,0x3]' --n_controlees 3

    sleep 1

    echo "--- Initiating TAG 2 (Jetson 2) ---"
    # Using 'EOF' creates a safe tunnel so the single quotes survive the SSH transfer
    ssh $JETSON2_USER_IP << 'EOF'
cd /home/jetson2/uwb-qorvo-tools
source /home/jetson2/uwb_venv/bin/activate
python3 scripts/fira/run_fira_twr/run_fira_twr.py -p /dev/ttyACM2 -t 3 --node onetomany --mac 0x5 -s 2 --dest-mac '[0x1,0x2,0x3]' --n_controlees 3
EOF

    sleep 1
done
