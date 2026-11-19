#!/bin/bash
# ----------------------------------------------------------------------------
# UWB_V2X
# Status : Ran (attempt 1). Failed: run_fira_twr.py has no --session-id option. For attempt 2 only its two TAG_CMD lines were changed (-s 1 / -s 2 and a fixed port); that run ended in EOFError on the Jetson and RangingRxMacIeDecFailed (0x26) on the anchors.
# About  : Per-Jetson paths in the SSH command.
# ----------------------------------------------------------------------------

# Configuration
UWB_DIR="/home/jetson1/uwb-qorvo-tools"
VENV="source /home/jetson1/uwb_venv/bin/activate"

# The execution commands with unique MACs and Session IDs
TAG1_CMD="python3 scripts/fira/run_fira_twr/run_fira_twr.py -t -1 --node onetomany --mac 0x4 --session-id 1 --dest-mac '[0x1,0x2,0x3]' --n_controlees 3"
TAG2_CMD="python3 scripts/fira/run_fira_twr/run_fira_twr.py -t -1 --node onetomany --mac 0x5 --session-id 2 --dest-mac '[0x1,0x2,0x3]' --n_controlees 3"

# ---> CHANGE THIS LINE TO JETSON 2's EXACT IP <---
JETSON2_USER_IP="jetson2@192.168.X.X"

echo "Starting Round-Robin UWB TWR..."

while true; do
    echo "--- Initiating TAG 1 (Jetson 1) ---"
    bash -c "cd $UWB_DIR && $VENV && $TAG1_CMD" &
    TAG1_PID=$!
    sleep 3
    kill -2 $TAG1_PID
    wait $TAG1_PID 2>/dev/null
    sleep 1

    echo "--- Initiating TAG 2 (Jetson 2) ---"
    ssh $JETSON2_USER_IP "bash -c 'cd /home/jetson2/uwb-qorvo-tools && source /home/jetson2/uwb_venv/bin/activate && $TAG2_CMD'" &
    TAG2_PID=$!
    sleep 3
    kill -2 $TAG2_PID
    wait $TAG2_PID 2>/dev/null
    sleep 1
done
