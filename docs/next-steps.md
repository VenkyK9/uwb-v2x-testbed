# Next steps

What is still open. The first two sections come from the project plan; the last two are suggestions, not decisions.

## Where the project stands

- Two tags (Jetson 1 and Jetson 2) range in turn with three anchors (Pi 1 to 3) on UCI firmware.
- The output is distances in centimetres on a terminal. Nothing computes a position yet.
- The LiDAR obstacle-detection node was reported working on the bench. SLAM is blocked on odometry.
- No robot has been assembled or driven yet.
- For the demonstration the ROS 2 work was set aside, to show two tags with three anchors first.

## Planned, in order

| # | Step | Status |
|---|---|---|
| 1 | Three tags with three anchors (the stated first goal, before any position work) | Two of three tags done |
| 2 | Trilateration: three distances plus the anchor positions give (x, y) for each tag | Not started |
| 3 | A ROS 2 node on each Jetson that publishes the UWB position | Not started |
| 4 | Run the UWB client as a service on each robot's Jetson | Not started |
| 5 | Sensor fusion with `robot_localization` (EKF): UWB position, LiDAR odometry, wheel odometry | Not started |
| 6 | Robot base: Teensy 4.1 reading encoders and driving the MDDS30, mecanum kinematics, `/cmd_vel` from the Jetson | Not started |
| 7 | Connect the obstacle node's `/cmd_vel` to the base | Not started |
| 8 | SLAM with `slam_toolbox`, then Nav2 | Blocked on an odometry source |
| 9 | Depth camera (D435i) for obstacles the 2D LiDAR cannot see | Not started |
| 10 | Fleet: copy the working setup to robots 2 and 3, one ROS namespace per robot, a dedicated 5 GHz network | Not started |
| 11 | V2X logic: robots share positions and detected obstacles; virtual lanes and collision zones | Not started |

## Open technical questions

| Question | Where it stands |
|---|---|
| Third tag | Not yet added. The scheduler has two turns; a third Jetson would need a third |
| Anchor positions | Trilateration needs each anchor's coordinates. Placement advice was given (corners of the area, raised, clear line of sight); no measured positions are recorded |
| Where the position is computed | First plan: on a central Pi that hears all anchors. With tags as initiators each Jetson already holds its own three distances |
| Gaps in the data | A tag only ranges during its own three-second turn. Whatever consumes the distances has to cope with the pauses. An earlier discussion expected an EKF with wheel odometry and an IMU to bridge blind spots of about three seconds |
| Telling tags apart | Both tags use address `0x0`; the anchors cannot tell which robot they are ranging with |
| Boards that stop answering | Solved for the tags with bounded runs. Anchors still run without a time limit and were unplugged when they hung. A USB hub with per-port power switching and a modified firmware were discussed |
| Odometry for SLAM without wheels | RF2O never started producing output. The handheld `slam_toolbox` parameters were proposed and not tried |
| USB ports on the Jetson | Four ports, four devices planned. Hub, UART or Teensy bridge: not decided |
| Data between robots | Decided: not over UWB. Wi-Fi carries sensor data; UWB is for position only |

## Things worth checking on the hardware

Suggestions; none of these has been tested yet.

1. **Ctrl+Z in the logs.** Many runs end with `^Z` and `Stopped`, which suspends a program without closing its serial port or its UWB session. It would be worth repeating a stop-and-restart test with clean stops only (Enter for the `-t -1` anchors, Ctrl+C elsewhere) before concluding that a board needs unplugging. Details under "Patterns worth remembering" in [`errors-and-fixes.md`](errors-and-fixes.md#patterns-worth-remembering).
2. **The udev rule.** [`config/udev/99-uwb.rules`](../config/udev/99-uwb.rules) was recommended, but on 28 May Jetson 1 still showed the port as `crw-rw---- root dialout` and `chmod` was used. Installing the rule on every host would remove a repeated manual step.
3. **Port detection.** `ls /dev/ttyACM* | head -n 1` picks the first serial device of any kind. A udev symlink for the Qorvo board (USB ID `1915:520f`) would make the choice exact.
4. **The obstacle node publishes `/cmd_vel` all the time.** Before a motor controller listens to that topic, decide whether the node should drive the robot or only report. See the review notes in [`lidar/README.md`](lidar/README.md).

## Not in this repository yet

- The scripts as they exist on the devices today: `demo_runner.sh` on Jetson 1, the anchor commands on the Pis, and the `lidar_obstacle_detector` package with its `setup.py` and `package.xml`.
- Photos or video of the setup and the demonstration.
- Measured anchor positions and a sketch of the test area.
- A wiring diagram for the robot base, once it exists.

Qorvo's SDK, firmware images and calibration files are not included: they come under Qorvo's own licence and are downloaded from Qorvo.
