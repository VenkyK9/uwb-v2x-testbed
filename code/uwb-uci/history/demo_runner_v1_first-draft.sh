#!/bin/bash
# ----------------------------------------------------------------------------
# UWB_V2X
# Status : Superseded before running (path ~/uwb-qorvo-tools/source does not exist).
# About  : First draft: background jobs + kill, explicit --mac and --session-id.
# ----------------------------------------------------------------------------

# Configuration
UWB_DIR="~/uwb-qorvo-tools/source"
VENV="source ~/uwb_venv/bin/activate"
TAG1_CMD="python3 scripts/fira/run_fira_twr/run_fira_twr.py -t -1 --node onetomany --mac 0x4 --session-id 1 --dest-mac '[0x1,0x2,0x3]' --n_controlees 3"
TAG2_CMD="python3 scripts/fira/run_fira_twr/run_fira_twr.py -t -1 --node onetomany --mac 0x5 --session-id 2 --dest-mac '[0x1,0x2,0x3]' --n_controlees 3"
JETSON2_USER_IP="user@<JETSON2_IP_ADDRESS>"

echo "Starting Round-Robin UWB TWR..."

while true; do
    echo "--- Initiating TAG 1 (Jetson 1) ---"
    # Run locally in background
    bash -c "cd $UWB_DIR && $VENV && $TAG1_CMD" &
    TAG1_PID=$!
    sleep 3
    kill -2 $TAG1_PID # Send SIGINT to stop cleanly
    wait $TAG1_PID 2>/dev/null
    sleep 1 # Buffer to let anchors reset

    echo "--- Initiating TAG 2 (Jetson 2) ---"
    # Run remotely via SSH in background
    ssh $JETSON2_USER_IP "bash -c 'cd $UWB_DIR && $VENV && $TAG2_CMD'" &
    TAG2_PID=$!
    sleep 3
    kill -2 $TAG2_PID
    wait $TAG2_PID 2>/dev/null
    sleep 1 # Buffer to let anchors reset
done
