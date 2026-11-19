# Code

The scripts written during the project. Each file starts with a short header saying what it is and what happened when it was run. Most are steps on the way; the versions that worked are marked, and the earlier ones are kept to show how the design got there.

## UWB on CLI firmware (INITF / RESPF over serial)

| File | What it is | Status |
|---|---|---|
| [`uwb-cli-firmware/00_qorvo_live_service_original.py`](uwb-cli-firmware/00_qorvo_live_service_original.py) | The first anchor script, run on each Pi by qorvo-live.service. | Superseded. Sends 'respf -multi -addr=N -paddr=[11,12]'. It came under suspicion because anchor 1 reported address 0x0000 instead of 0x0001. |
| [`uwb-cli-firmware/01_anchor_slow-send_revision.py`](uwb-cli-firmware/01_anchor_slow-send_revision.py) | Revision that sends one character at a time and drops -PADDR on the responder. | Proposed. No run is recorded; replaced by the short scripts below. |
| [`uwb-cli-firmware/02_qorvo_anchor_v1.py`](uwb-cli-firmware/02_qorvo_anchor_v1.py) | Minimal anchor: STOP, then RESPF -MULTI -ADDR=1. | Ran. Anchor showed address 0x0001 but logged RX_MAC_IE_DEC_FAILED. |
| [`uwb-cli-firmware/03_qorvo_tag_v1.py`](uwb-cli-firmware/03_qorvo_tag_v1.py) | Minimal tag: LCFG -STSMODE=1, then INITF -MULTI -ADDR=11 -PADDR=1. | Ran. Tag logged RX_TIMEOUT. |
| [`uwb-cli-firmware/04_qorvo_anchor_v2_sts.py`](uwb-cli-firmware/04_qorvo_anchor_v2_sts.py) | Anchor with LCFG -STSMODE=1 and SAVE before RESPF. | Ran. Same failure as v1 (the anchor still had no peer address). |
| [`uwb-cli-firmware/05_qorvo_tag_v2_sts.py`](uwb-cli-firmware/05_qorvo_tag_v2_sts.py) | Tag with LCFG -STSMODE=1 and SAVE before INITF. | Ran. This is the tag side of the first successful 1:1 ranging (with anchor v3). |
| [`uwb-cli-firmware/06_qorvo_anchor_v3_sts_pdoa_paddr.py`](uwb-cli-firmware/06_qorvo_anchor_v3_sts_pdoa_paddr.py) | Anchor with STS on, PDoA off and the tag's address as -PADDR=11. | Ran and worked: first successful 1:1 ranging (about 1.5 m). |
| [`uwb-cli-firmware/07_qorvo_anchor2_addr2.py`](uwb-cli-firmware/07_qorvo_anchor2_addr2.py) | The same anchor script for anchor 2 (ADDR=2); anchors 3 and 4 differ only in ADDR. | Ran. Worked once the tag's list was written as -PADDR=[1,2,3,4] (1 tag with 4 anchors). |
| [`uwb-cli-firmware/08_qorvo_tag2_one-to-many.py`](uwb-cli-firmware/08_qorvo_tag2_one-to-many.py) | Tag 2 (ADDR=12) polling anchors [1,2,3,4]. | Proposed for the second robot. No successful two-tag run on CLI firmware is recorded. |
| [`uwb-cli-firmware/09_qorvo_rescue_v1_reset-button.py`](uwb-cli-firmware/09_qorvo_rescue_v1_reset-button.py) | Rescue for anchor 2: flood STOP while pressing SW1, then RESTORE and SAVE. | Ran. Failed with 'Could not open port', before and after qorvo-live.service was disabled; a changed port number was suspected next. |
| [`uwb-cli-firmware/10_qorvo_rescue_v2_autodetect-port.py`](uwb-cli-firmware/10_qorvo_rescue_v2_autodetect-port.py) | Rescue with automatic /dev/ttyACM* detection. | Ran. Failed with 'write failed: [Errno 5] Input/output error' when the board reset. |
| [`uwb-cli-firmware/11_qorvo_rescue_v3_wait-for-usb.py`](uwb-cli-firmware/11_qorvo_rescue_v3_wait-for-usb.py) | Rescue that waits for the USB port to reappear and sends STOP at once. | Ran. Printed 'BOARD TRAPPED IN IDLE' but the board still refused commands; a full erase and reflash was the next step. |
| [`uwb-cli-firmware/12_qorvo_anchor2_buffer-flush.py`](uwb-cli-firmware/12_qorvo_anchor2_buffer-flush.py) | Anchor 2 script with flush, reset_input_buffer and CRLF line endings. | Ran. Did not recover anchor 2 ('still no luck'). |
| [`uwb-cli-firmware/13_setup_anchor_master.py`](uwb-cli-firmware/13_setup_anchor_master.py) | One anchor script for all Pis: set ANCHOR_ID, peers are tags [11,12]. | Proposed once the correct firmware was reported installed. No run is recorded. |
| [`uwb-cli-firmware/14_setup_tag_master.py`](uwb-cli-firmware/14_setup_tag_master.py) | One tag script for both robots: set TAG_ID, peers are anchors [1,2,3,4]. | Proposed once the correct firmware was reported installed. No run is recorded. |
| [`uwb-cli-firmware/15_alt_tag_threaded_responder-per-anchor.py`](uwb-cli-firmware/15_alt_tag_threaded_responder-per-anchor.py) | Alternative design: threaded reader; the TAG runs RESPF once per anchor. | Kept for comparison. The per-anchor loop cannot work: the firmware accepts one session at a time (see the stacking test). |
| [`uwb-cli-firmware/16_alt_anchor_threaded_initiator.py`](uwb-cli-firmware/16_alt_anchor_threaded_initiator.py) | Alternative design: threaded reader; the ANCHOR is the initiator polling tags [11,12]. | Kept for comparison. One test ranged anchor 1 to both tags this way (273 and 315 cm); that log is not included. |
| [`uwb-cli-firmware/17_master_tag_threaded.py`](uwb-cli-firmware/17_master_tag_threaded.py) | Merged version: threaded reader, tag as initiator with the bracketed anchor list. | Proposed. No run is recorded. |
| [`uwb-cli-firmware/18_master_anchor_threaded.py`](uwb-cli-firmware/18_master_anchor_threaded.py) | Merged version: threaded reader, anchor as responder to tags [11,12]. | Proposed. No run is recorded. |
| [`uwb-cli-firmware/19_timeslice_tag.py`](uwb-cli-firmware/19_timeslice_tag.py) | Tag for the time-slicing idea (unchanged initiator). | Proposed. No run is recorded; the project moved to UCI firmware instead. |
| [`uwb-cli-firmware/20_timeslice_anchor.py`](uwb-cli-firmware/20_timeslice_anchor.py) | Anchor that alternates every 2.5 s between tag 11 and tag 12 (STOP, RESPF, wait). | Proposed. No run is recorded; the project moved to UCI firmware instead. |
| [`uwb-cli-firmware/21_uci_raw-packet_sketch.py`](uwb-cli-firmware/21_uci_raw-packet_sketch.py) | Illustration of raw UCI packets over pyserial. | Sketch only. The app-config payload is a placeholder ('4103...'), so it cannot run as written. |

## UWB on UCI firmware (run_fira_twr.py)

| File | What it is | Status |
|---|---|---|
| [`uwb-uci/demo_runner.sh`](uwb-uci/demo_runner.sh) | FINAL scheduler: tags take 3-second turns, default UWB profile, serial port found at run time. | Ran and worked: both Jetsons ranged to all three anchors in turn. |
| [`uwb-uci/history/demo_runner_v1_first-draft.sh`](uwb-uci/history/demo_runner_v1_first-draft.sh) | First draft: background jobs + kill, explicit --mac and --session-id. | Superseded before running (path ~/uwb-qorvo-tools/source does not exist). |
| [`uwb-uci/history/demo_runner_v2_paths-fixed.sh`](uwb-uci/history/demo_runner_v2_paths-fixed.sh) | Paths corrected for jetson1. | Superseded by v3 (Jetson 2 needs its own paths). |
| [`uwb-uci/history/demo_runner_v3_attempt-1.sh`](uwb-uci/history/demo_runner_v3_attempt-1.sh) | Per-Jetson paths in the SSH command. | Ran (attempt 1). Failed: run_fira_twr.py has no --session-id option. For attempt 2 only its two TAG_CMD lines were changed (-s 1 / -s 2 and a fixed port); that run ended in EOFError on the Jetson and RangingRxMacIeDecFailed (0x26) on the anchors. |
| [`uwb-uci/history/demo_runner_v4_attempt-3_heredoc.sh`](uwb-uci/history/demo_runner_v4_attempt-3_heredoc.sh) | No background jobs: -t 3 bounded runs, SSH heredoc, -s for the session, fixed ports. | Ran (attempt 3). Anchors still reported RangingRxMacIeDecFailed (0x26). |
| [`uwb-uci/history/demo_runner_v5_default-profile.sh`](uwb-uci/history/demo_runner_v5_default-profile.sh) | Custom --mac and -s removed (default profile on both tags). | Ran. Jetson 1 ranged with all three anchors; Jetson 2's turn got no further than 'Initializing session 42...' before the run was suspended. |
| [`uwb-uci/history/demo_runner_v6_ssh-T.sh`](uwb-uci/history/demo_runner_v6_ssh-T.sh) | ssh -T so no pseudo-terminal is requested. | Ran. Both tags ranged; the second loop failed because the board came back on a different /dev/ttyACM number. |
| [`uwb-uci/restart-wrappers/anchor_continuous.py`](uwb-uci/restart-wrappers/anchor_continuous.py) | Wrapper that restarts run_fira_twr.py for an anchor when it exits with an error. | Proposed. No run is recorded. Review note: it passes env={'UQT_PORT': port} only, which removes PATH and the rest of the environment from the child process. |
| [`uwb-uci/restart-wrappers/anchor_daemon.py`](uwb-uci/restart-wrappers/anchor_daemon.py) | Restart loop for an anchor (python3 anchor_daemon.py 0x1). | Ran on the Pis (as anchor_daemon1/2/3.py). Restarts the process only; it cannot revive a board that stopped answering. |
| [`uwb-uci/restart-wrappers/tag_daemon.py`](uwb-uci/restart-wrappers/tag_daemon.py) | Restart loop for a tag. | Proposed. No run is recorded. |

## LiDAR on ROS 2 Humble

| File | What it is | Status |
|---|---|---|
| [`lidar/lidar_obstacle_detector/obstacle_node.py`](lidar/lidar_obstacle_detector/obstacle_node.py) | Obstacle node tuned to the A2M12 scan (1800 beams): front/left/right/rear sectors, /obstacle_state and /cmd_vel. | Worked on the bench: 'critical' when something is close, 'warning' a little further away. No output of the node itself was saved. |
| [`lidar/lidar_obstacle_detector/obstacle_node_first-draft.py`](lidar/lidar_obstacle_detector/obstacle_node_first-draft.py) | First draft that derives sector indices from angle_min / angle_increment. | Superseded by the tuned node. |
| [`lidar/launch/bringup_launch_sketch.py`](lidar/launch/bringup_launch_sketch.py) | Outline of one bring-up launch file with mode:=handheld\|robot. | Pseudocode (imports are incomplete). Not runnable as written. |
| [`lidar/webviz/index.html`](lidar/webviz/index.html) | Browser page (roslibjs + ros2djs) showing /scan and /map through rosbridge. | Proposed. No run is recorded. |
