#!/bin/bash
# ----------------------------------------------------------------------------
# UWB_V2X
# Status : Ran and worked: both Jetsons ranged to all three anchors in turn.
# About  : FINAL scheduler: tags take 3-second turns, default UWB profile, serial port found at run time.
# ----------------------------------------------------------------------------

JETSON2_USER_IP="jetson2@192.168.X.X"

echo "Starting Round-Robin UWB TWR..."

while true; do
    echo "--- Initiating TAG 1 (Jetson 1) ---"
    cd /home/jetson1/uwb-qorvo-tools
    source /home/jetson1/uwb_venv/bin/activate

    # Auto-detect the port in case Linux incremented it
    J1_PORT=$(ls /dev/ttyACM* | head -n 1)
    echo "Using Jetson 1 Port: $J1_PORT"

    python3 scripts/fira/run_fira_twr/run_fira_twr.py -p $J1_PORT -t 3 --node onetomany --dest-mac '[0x1,0x2,0x3]' --n_controlees 3

    sleep 1

    echo "--- Initiating TAG 2 (Jetson 2) ---"
    ssh -T $JETSON2_USER_IP << 'EOF'
cd /home/jetson2/uwb-qorvo-tools
source /home/jetson2/uwb_venv/bin/activate

# Auto-detect the port on Jetson 2
J2_PORT=$(ls /dev/ttyACM* | head -n 1)
echo "Using Jetson 2 Port: $J2_PORT"

python3 scripts/fira/run_fira_twr/run_fira_twr.py -p $J2_PORT -t 3 --node onetomany --dest-mac '[0x1,0x2,0x3]' --n_controlees 3
EOF

    sleep 1
done
