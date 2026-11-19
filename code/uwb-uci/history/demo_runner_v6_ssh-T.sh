#!/bin/bash
# ----------------------------------------------------------------------------
# UWB_V2X
# Status : Ran. Both tags ranged; the second loop failed because the board came back on a different /dev/ttyACM number.
# About  : ssh -T so no pseudo-terminal is requested.
# ----------------------------------------------------------------------------

JETSON2_USER_IP="jetson2@192.168.X.X"

echo "Starting Round-Robin UWB TWR..."

while true; do
    echo "--- Initiating TAG 1 (Jetson 1) ---"
    cd /home/jetson1/uwb-qorvo-tools
    source /home/jetson1/uwb_venv/bin/activate
    python3 scripts/fira/run_fira_twr/run_fira_twr.py -p /dev/ttyACM1 -t 3 --node onetomany --dest-mac '[0x1,0x2,0x3]' --n_controlees 3

    sleep 1

    echo "--- Initiating TAG 2 (Jetson 2) ---"
    # Added -T to prevent the "Pseudo-terminal" hangup
    ssh -T $JETSON2_USER_IP << 'EOF'
cd /home/jetson2/uwb-qorvo-tools
source /home/jetson2/uwb_venv/bin/activate
python3 scripts/fira/run_fira_twr/run_fira_twr.py -p /dev/ttyACM2 -t 3 --node onetomany --dest-mac '[0x1,0x2,0x3]' --n_controlees 3
EOF

    sleep 1
done
