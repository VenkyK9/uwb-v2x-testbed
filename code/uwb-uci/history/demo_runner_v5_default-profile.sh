#!/bin/bash
# ----------------------------------------------------------------------------
# UWB_V2X
# Status : Ran. Jetson 1 ranged with all three anchors; Jetson 2's turn got no further than 'Initializing session 42...' before the run was suspended.
# About  : Custom --mac and -s removed (default profile on both tags).
# ----------------------------------------------------------------------------

# ---> SET JETSON 2 IP HERE <---
JETSON2_USER_IP="jetson2@192.168.X.X"

echo "Starting Round-Robin UWB TWR..."

while true; do
    echo "--- Initiating TAG 1 (Jetson 1) ---"
    cd /home/jetson1/uwb-qorvo-tools
    source /home/jetson1/uwb_venv/bin/activate
    # Stripped out explicit mac/session to match the default profiles the anchors expect
    python3 scripts/fira/run_fira_twr/run_fira_twr.py -p /dev/ttyACM1 -t 3 --node onetomany --dest-mac '[0x1,0x2,0x3]' --n_controlees 3

    sleep 1

    echo "--- Initiating TAG 2 (Jetson 2) ---"
    ssh $JETSON2_USER_IP << 'EOF'
cd /home/jetson2/uwb-qorvo-tools
source /home/jetson2/uwb_venv/bin/activate
# Stripped out explicit mac/session to match the default profiles the anchors expect
python3 scripts/fira/run_fira_twr/run_fira_twr.py -p /dev/ttyACM2 -t 3 --node onetomany --dest-mac '[0x1,0x2,0x3]' --n_controlees 3
EOF

    sleep 1
done
