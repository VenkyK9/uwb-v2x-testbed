# Decision log

What was decided during the project, what else was on the table, and the reason recorded at the time. "Status" says how far each decision was carried: **in use** means the working setup relies on it, **planned** means it was agreed but nothing in this repository implements it, **dropped** means it was tried or considered and set aside.

## System and software platform

| # | Decision | Alternatives | Reason given | Status |
|---|---|---|---|---|
| D1 | ROS 2 Humble on Ubuntu 22.04 (JetPack 6.2.2) | ROS 1 Noetic; ROS 2 Jazzy on Ubuntu 24.04 | ROS 1 is end-of-life and needs a single master, which is a poor fit for several robots. Jazzy needs Ubuntu 24.04, and JetPack for the Orin Nano was still on 22.04; the project could not wait for JetPack 7.2. | In use for the LiDAR work |
| D2 | One Jetson Orin Nano per robot, no Raspberry Pi on the robots; Pis only host the fixed anchors | A Pi on each robot as a second computer | A second computer adds power, space and network overhead and no capability the Jetson lacks. | In use (anchors on Pis, tags on Jetsons) |
| D3 | Teensy 4.1 as the low-level bridge between the Jetson and the Cytron MDDS30 motor driver, powered separately from the battery path | Teensy placed in the power path between battery and Jetson | The buck converter should power the Jetson directly; the Teensy isolates logic from motor-driver noise and takes velocity commands over USB. | Planned |
| D4 | UWB carries position only; bulk data (LiDAR scans, camera, maps) goes over 5 GHz Wi-Fi | Sending sensor data over the UWB link | UWB payloads are small and data traffic competes with the timing-critical ranging frames. | In use as a design rule |
| D5 | Navigation by sensor fusion: UWB for absolute position, LiDAR for obstacles, odometry for smooth motion, fused with an EKF (`robot_localization`) | Navigating on UWB alone | UWB cannot see untagged obstacles and jumps when line of sight is blocked. | Planned |
| D14 | Get UWB working first; leave ROS out of the UWB demo | Wrapping UWB in ROS 2 nodes straight away | A broken ROS apt source was blocking progress; later the demo only needed two tags and three anchors. | In use |

## UWB

| # | Decision | Alternatives | Reason given | Status |
|---|---|---|---|---|
| D6 | Qorvo DWM3001CDK boards (DW3110 + nRF52833) with `DW3_QM33_SDK_1.1.1` | Older DW1000-based boards | The boards were in hand from the start. The reasons given for the presentation: the DW3000 family works on channels 5 and 9, supports IEEE 802.15.4z with STS for secure ranging, and uses less power than the DW1000. | In use |
| D7 | Double-sided two-way ranging; tags initiate, anchors respond | TDoA with synchronised anchors; an anchor as the initiator with tags responding | TWR needs no clock synchronisation between anchors. With tags as initiators each robot gets its own distances. | In use |
| D8 | Target of 3 tags and 3 anchors; tests ran with 4 anchors + 2 tags (CLI) and 3 anchors + 2 tags (UCI) | | Three distances are needed to work out an (x, y) position. The demonstration was limited to two tags: "We just have to show 2 TAG 3 ANCHOR SETUP for now." | 2 tags + 3 anchors demonstrated |
| D9 | Start on the CLI firmware, then move every board to the UCI firmware | Starting on UCI | CLI output is readable and proved the radios before any host software existed. It was left when two tags were needed: one board runs one session and there is no session scheduling. | UCI in use; CLI retired |
| D10 | On CLI: STS on, PDoA off, `-MULTI` with explicit addresses, each anchor given the tag's address, anchor list in square brackets | Defaults; address commands that do not exist in this firmware | Found from the board's own help text and from comparing the session dumps of tag and anchor. | Worked for 1 tag + 4 anchors |
| D11 | No "stacked" sessions with unique IDs on the CLI firmware | One session per anchor on each tag, with unique session IDs | Tested by hand on a tag and on an anchor: the second `RESPF` returns `error incompatible mode`. | Dropped after the test |
| D12 | UCI firmware `DWM3001CDK-DW3_QM33_SDK_UCI-FreeRTOS.hex` on all six boards; calibration file `dual-hoe_non_aoa.json` | | The UCI build is scriptable from Python; the non-AoA calibration matches a single-antenna board. | In use |
| D13 | Run the Qorvo tools on Python 3.10 and install only the two core libraries, skipping the PySide2 GUI dependency | `pip install -e .` of the whole package | `uwb-uci` requires Python 3.9 or 3.10; PySide2 has no wheel for these ARM boards and is only needed for plots. | In use |
| D15 | Two tags by taking turns, scheduled from a script on Jetson 1 | Rewriting firmware for concurrent initiators; one anchor as initiator with all tags as responders | The failure was a scheduling problem. If the tags never transmit together they can share the profile the anchors already accept. | In use ([`demo_runner.sh`](../code/uwb-uci/demo_runner.sh)) |
| D16 | Both tags keep the default MAC address and session number | `--mac 0x4` / `0x5` with sessions 1 / 2 | With explicit values the anchors answered every frame with `RangingRxMacIeDecFailed (0x26)`. | In use |
| D17 | Each turn is a bounded run (`-t 3`) | Endless run (`-t -1`) stopped with `kill` | A bounded run lets the tool stop and de-initialise the session, so the board accepts the next one. | In use |
| D18 | Look up the serial port before every run | Fixed `/dev/ttyACM1` | The board re-enumerates after each session and Linux gives it the next free number. | In use |
| D19 | Not adopted: community (Uberi) firmware, per-port USB power switching, CLI firmware on the anchors only | | Considered as ways around the power-cycle problem. None was taken up; the demonstration ran with bounded runs instead. | Not adopted |

## LiDAR

| # | Decision | Alternatives | Reason given | Status |
|---|---|---|---|---|
| D20 | `sllidar_ros2` built from source, launched with `view_sllidar_a2m12_launch.py` | The `rplidar_ros` apt package | The apt package had no launch file by the name being used; `sllidar_ros2` ships one for the A2M12. | In use |
| D21 | Obstacle detection by sectors and thresholds: front, left, right, rear; stop under 0.6 m, slow under 1.0 m | Clustering (DBSCAN) of scan points into separate objects | The plan was to "start simple and scale up": thresholds first, clustering later. The node in use is the threshold stage. | Thresholds in use; clustering not started |
| D22 | `slam_toolbox` on the real sensor; no Gazebo for now | Cartographer, GMapping, Hector SLAM; simulation first in Gazebo Classic | `slam_toolbox` is the maintained choice on Humble. Gazebo Classic cannot be installed from apt on the Jetson and is end-of-life. | Attempted, not finished |
| D23 | RF2O laser odometry as a stand-in for wheel odometry while there is no moving base | Static `odom` transform; waiting for the robot | `slam_toolbox` needs an `odom -> base_link` source; RF2O estimates one from consecutive scans. | Unresolved (RF2O never received scans) |
| D24 | Browser view of `/scan` and `/map` through `rosbridge` or Foxglove, with Tailscale for remote access | Port forwarding | No ROS needed on the viewing device; no ports opened to the internet. | Proposed |

## Project housekeeping

| # | Decision | Reason given |
|---|---|---|
| D25 | Wheel and drive-train parts list accepted as mechanically compatible | Coupler, bearing housing, shaft, anti-slip coupling and 100 mm mecanum wheels fit the PGM45775 motor's 10 mm shaft; twelve of each for three robots. |
