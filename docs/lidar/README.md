# LiDAR: obstacle detection and SLAM

The LiDAR work ran in parallel with the UWB work during May 2026, on Jetson 1 with a SLAMTEC RPLIDAR A2M12 and ROS 2 Humble. The sensor was on the bench or carried by hand; there was no moving robot yet.

Three tasks were defined for the LiDAR:

| Task | Status |
|---|---|
| 1. 2D LiDAR SLAM mapping | Tried with `slam_toolbox`. Not finished: no odometry source without a moving base |
| 2. Real-time obstacle detection | **Reported working on the bench** |
| 3. UWB + LiDAR fusion for indoor localisation | Not started |

Task 2 is the one covered here. SLAM was assigned to another team; the SLAM attempts below were made on the same Jetson while the sensor was being set up.

## Setup that was used

| Item | Value |
|---|---|
| Computer | Jetson 1 (`jetson1@jetson1-desktop`), ROS 2 Humble |
| Workspace | `~/ros2_ws`, built with `colcon build --symlink-install` |
| Packages built in the workspace | `sllidar_ros2`, `rf2o_laser_odometry`, `lidar_obstacle_detector` |
| Driver, early May | `rplidar_ros` installed under `/opt/ros/humble`: `ros2 launch rplidar_ros view_rplidar_a2m12_launch.py` |
| Driver, from 22 May | `sllidar_ros2` built from source: `ros2 launch sllidar_ros2 view_sllidar_a2m12_launch.py` |
| Scan | Topic `/scan`, frame `laser`, 1800 points per turn, about 0.2° apart, range limit 16 m |

Run only one driver at a time. On 26 May both `/rplidar_node` and `/sllidar_node` were alive and `/scan` had two publishers.

## Obstacle detection

The node is [`code/lidar/lidar_obstacle_detector/obstacle_node.py`](../../code/lidar/lidar_obstacle_detector/obstacle_node.py).

What it does on every scan:

1. Takes the smallest valid range in four sectors: front (−30° to +30°), left (30° to 90°), right (−90° to −30°) and rear (150° to 180°).
2. Publishes a state on `/obstacle_state`:

   | State | Condition |
   |---|---|
   | `OBSTACLE_FRONT_CRITICAL` | Front closer than `safe_distance` (0.6 m) |
   | `OBSTACLE_FRONT_WARNING` | Front closer than `warn_distance` (1.0 m) |
   | `OBSTACLE_LEFT` / `OBSTACLE_RIGHT` | That side closer than 0.6 m |
   | `CLEAR` | None of the above |

3. Publishes a velocity command on `/cmd_vel`: stop and turn towards the freer side when critical, creep at 0.05 m/s when warning, otherwise forward at 0.2 m/s.

Both distances are ROS parameters (`safe_distance`, `warn_distance`).

### Building and running it

Create the package once:

```bash
cd ~/ros2_ws/src
ros2 pkg create lidar_obstacle_detector --build-type ament_python --dependencies rclpy sensor_msgs geometry_msgs std_msgs
# put obstacle_node.py in ~/ros2_ws/src/lidar_obstacle_detector/lidar_obstacle_detector/
# in setup.py, under entry_points -> console_scripts, add:
#   'obstacle_node = lidar_obstacle_detector.obstacle_node:main',
cd ~/ros2_ws
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash
```

Then, in separate terminals, each after `source /opt/ros/humble/setup.bash` and `source ~/ros2_ws/install/setup.bash`:

```bash
ros2 launch rplidar_ros view_rplidar_a2m12_launch.py     # the driver in use at the time
ros2 run lidar_obstacle_detector obstacle_node
ros2 topic echo /obstacle_state
```

### Result

It worked on the bench: "critical" when something is close, "warning" when it is a little further away. The node prints a line such as `F=2.14m  L=2.32m  R=2.19m  B=2.50m` for every scan. No terminal output of the node itself was saved.

### Review notes

From reading the code afterwards. None of these has been tested yet.

- **The node drives.** It publishes `/cmd_vel` all the time, including 0.2 m/s forward when the way is clear. That is harmless on the bench. Once a motor controller listens to `/cmd_vel`, the robot will move as soon as the node starts.
- **Side states do not change the command.** `OBSTACLE_LEFT` and `OBSTACLE_RIGHT` fall through to the same forward command as `CLEAR`.
- **The rear sector covers one side only.** It reads 150° to 180°. The comment in the code mentions handling the wrap to −180°, but there is no such code, and the rear value is only logged.
- **The scan layout is hard-coded.** The node assumes the scan starts at −179° with 0.1996° per point, taken from the scan of 7 May. The scan captured on 22 May with the other driver starts at −180° with 0.2001° per point, so the sectors sit up to a degree off. The [first draft](../../code/lidar/lidar_obstacle_detector/obstacle_node_first-draft.py) computes indices from the values in each message and does not have this dependence.

## SLAM

What was tried, in order:

| Step | Outcome |
|---|---|
| Choice of `slam_toolbox` over Cartographer, GMapping and Hector SLAM | Recommended as the maintained option on Humble |
| Gazebo Classic for simulation first | Cannot be installed from apt on the Jetson; dropped ([log](../../logs/lidar/02_gazebo-classic_install-errors.log)) |
| Hand-carried LiDAR with RF2O laser odometry feeding `slam_toolbox` | Plan given; `rf2o_laser_odometry` built in the workspace |
| Starting the driver (22 May) | RViz could not open a display; the driver timed out; then the launch-file name was wrong. Fixed by moving to `sllidar_ros2` ([log](../../logs/lidar/03_2026-05-22_rplidar-launch_no-display_timeout.log)) |
| RF2O (22 May) | Printed `Waiting for laser_scans....` and never produced odometry. Topic name, TF and parameters were tried. Unresolved ([log](../../logs/lidar/04_2026-05-22_rf2o_waiting-for-laser-scans.log)) |
| `slam_toolbox` with its default parameters (26 May) | The node starts and a `/map` topic exists, but RViz reports a fixed-frame error and `ros2 topic echo` prints nothing for `/tf` and `/map` |
| TF check (26 May) | The tree holds only `base_link -> laser`. There is no `odom` frame, so the chain `map -> odom -> base_link -> laser` cannot form ([log](../../logs/lidar/05_2026-05-26_topics-nodes_and_tf-without-odom.log)) |

Where it stands: `slam_toolbox` needs something that publishes `odom -> base_link`. With no wheels that has to come from laser odometry (RF2O, which did not start), an IMU, or the robot base when it exists.

Two things were proposed and not yet run, both aimed at exactly this gap:

- [`config/slam_toolbox/slam_handheld.yaml`](../../config/slam_toolbox/slam_handheld.yaml) sets `odom_frame: base_link` so that `slam_toolbox` needs no separate odometry while the sensor is carried by hand. The launches on 26 May used the package defaults, without a parameter file.
- A temporary static transform, `ros2 run tf2_ros static_transform_publisher 0 0 0 0 0 0 odom base_link`, to confirm that the missing frame is the only blocker. It is a test, not a fix.

The static transform that was in use for the sensor itself is `ros2 run tf2_ros static_transform_publisher 0 0 0 0 0 0 base_link laser`.

### Start-up sequence given for a demo

The order used for a demo. It starts the LiDAR and SLAM; the obstacle node is started as shown earlier on this page.

```bash
# Terminal 1
cd ~/ros2_ws
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch sllidar_ros2 view_sllidar_a2m12_launch.py

# Terminal 2 (same cd and source lines first)
ros2 launch slam_toolbox online_async_launch.py
```

In RViz: fixed frame `map`, add LaserScan on `/scan`, Map on `/map`, and TF.

## Plans that were written down and not run

| Plan | Files |
|---|---|
| Whole stack before the robot arrives: handheld SLAM, Nav2 with costmaps fed by `/scan`, one launch file with `mode:=handheld` or `mode:=robot`, a validation checklist | [`slam_handheld.yaml`](../../config/slam_toolbox/slam_handheld.yaml), [`nav2_handheld.yaml`](../../config/nav2/nav2_handheld.yaml), [`bringup_launch_sketch.py`](../../code/lidar/launch/bringup_launch_sketch.py) |
| Live `/scan` and `/map` in a browser: `rosbridge_server` on port 9090 and a small page served on port 8000, or Foxglove; Tailscale for access from outside the network | [`webviz/index.html`](../../code/lidar/webviz/index.html) |
| Recording `/scan` to a rosbag so both teams can work without the sensor | |

## Related files

- All LiDAR logs: [`logs/`](../../logs/README.md)
- Errors L1 to L17 in [`../errors-and-fixes.md`](../errors-and-fixes.md#lidar-and-ros-2)
