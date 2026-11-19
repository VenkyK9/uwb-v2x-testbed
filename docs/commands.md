# Command reference

The commands in use at the end of the project, on one page. Each one is explained in the guide named in its heading. Replace addresses in angle brackets with your own.

## UWB on UCI firmware ([guide](uwb/uci-firmware-guide.md))

Every UWB command is run from the tools folder with the virtual environment active:

```bash
cd ~/uwb-qorvo-tools
source ~/uwb_venv/bin/activate
```

| Task | Command |
|---|---|
| Is the board on USB? | `lsusb \| grep -i nordic` |
| Which serial port? | `ls /dev/ttyACM*` |
| Open the port for this session | `sudo chmod 666 /dev/ttyACM0` |
| Does the board answer? | `python3 scripts/device/get_device_info/get_device_info.py -p /dev/ttyACM0` |
| Clear leftover sessions on a board | `python3 scripts/device/reset_device/reset_device.py -p /dev/ttyACM0` |
| Start anchor 1 (use `0x2`, `0x3` on the others) | `python3 scripts/fira/run_fira_twr/run_fira_twr.py -p $(ls /dev/ttyACM* \| head -n 1) -t -1 --node onetomany --mac 0x1 --controlee` |
| Start one tag by hand | `python3 scripts/fira/run_fira_twr/run_fira_twr.py -t -1 --node onetomany --dest-mac '[0x1,0x2,0x3]' --n_controlees 3` (with `export UQT_PORT=/dev/ttyACM0` first) |
| Run both tags in turn (on Jetson 1) | `~/uwb-qorvo-tools/demo_runner.sh` |
| Stop | Enter for a `-t -1` run (the tool's own clean stop), Ctrl+C otherwise; never Ctrl+Z, which only pauses the program and leaves its session open |
| Board does not answer (`TimeoutError (0x3)`) | Unplug its USB cable for ten seconds, plug it back in, check the port again |

Order for a run: unplug all UWB boards for ten seconds, start the anchors, wait about five seconds, then start the tags.

To show only the useful lines of the scheduler's output:

```bash
~/uwb-qorvo-tools/demo_runner.sh | grep --line-buffered -i "distance\|cm\|mac\|session\|initiating"
```

## UWB on CLI firmware ([guide](uwb/cli-firmware-guide.md))

| Task | Command |
|---|---|
| Open the console on a Pi | `python3 -m serial.tools.miniterm /dev/ttyACM0 115200` (exit with Ctrl+]) |
| List the commands | `HELP` |
| Show radio settings | `LCFG` |
| Anchor 1 | `STOP`, `LCFG -STSMODE=1`, `LCFG -PDOAMODE=0`, `SAVE`, `RESPF -MULTI -ADDR=1 -PADDR=11` |
| Tag 11 with four anchors | `STOP`, `LCFG -STSMODE=1`, `SAVE`, `INITF -MULTI -ADDR=11 -PADDR=[1,2,3,4]` |
| Stop a leftover service that holds the port | `sudo systemctl stop qorvo-live.service`, `sudo systemctl disable qorvo-live.service` |

## LiDAR and ROS 2 ([guide](lidar/README.md))

In every terminal first:

```bash
cd ~/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
```

| Task | Command |
|---|---|
| Start the LiDAR (with RViz) | `ros2 launch sllidar_ros2 view_sllidar_a2m12_launch.py` |
| Is the scan arriving? | `ros2 topic echo /scan --once` |
| Start obstacle detection | `ros2 run lidar_obstacle_detector obstacle_node` |
| Watch its output | `ros2 topic echo /obstacle_state` |
| Rebuild the obstacle package | `colcon build --symlink-install --packages-select lidar_obstacle_detector` |
| Tell ROS where the LiDAR sits | `ros2 run tf2_ros static_transform_publisher 0 0 0 0 0 0 base_link laser` |
| Start SLAM | `ros2 launch slam_toolbox online_async_launch.py` |
| Who publishes what? | `ros2 node list`, `ros2 topic info /scan` |
| Look at the TF tree | `ros2 run tf2_tools view_frames`, `ros2 run tf2_ros tf2_echo odom base_link` |
| Stop the LiDAR driver | Ctrl+C in its terminal. For a leftover `rplidar_ros` process, `pkill -f rplidar` |
