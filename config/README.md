# Configuration files

Configuration files from the project. The radio and session settings actually observed on the boards are summarised in [`uwb/radio-and-session-parameters.md`](uwb/radio-and-session-parameters.md).

## Serial port access

| File | What it is | Status |
|---|---|---|
| [`udev/99-uwb.rules`](udev/99-uwb.rules) | udev rule giving the dialout group access to every /dev/ttyACM* device. | Recommended during setup. Not confirmed as installed: on 28 May Jetson 1 still listed /dev/ttyACM0 as crw-rw---- root dialout, and 'sudo chmod 666' was the fix actually used. |

## SLAM and navigation (ROS 2 Humble)

| File | What it is | Status |
|---|---|---|
| [`slam_toolbox/mapper_params_online_async.yaml`](slam_toolbox/mapper_params_online_async.yaml) | Minimal slam_toolbox parameters for mapping with an odom frame. | Example given for the RF2O test. Whether this exact file was used was not noted. |
| [`slam_toolbox/slam_handheld.yaml`](slam_toolbox/slam_handheld.yaml) | slam_toolbox parameters for a hand-carried LiDAR (odom_frame = base_link). | Proposed. No run is recorded. |
| [`nav2/nav2_handheld.yaml`](nav2/nav2_handheld.yaml) | Minimal Nav2 parameters (planner, controller, costmaps fed by /scan) for bench validation. | Proposed. No run is recorded. |
