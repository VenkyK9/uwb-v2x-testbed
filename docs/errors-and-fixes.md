# Errors and fixes

The errors met during the project, grouped by phase: what was seen, what it turned out to be, what fixed it. The list was checked against every error, failure and warning line in the project's logs. "Cause" is the diagnosis reached at the time; where that diagnosis was never confirmed, the entry says so. Log files are in [`logs/`](../logs/README.md).

Contents: [UWB on CLI firmware](#uwb-on-cli-firmware) · [UWB on UCI firmware: host setup](#uwb-on-uci-firmware-host-setup) · [UWB on UCI firmware: ranging](#uwb-on-uci-firmware-ranging) · [The two-tag scheduler](#the-two-tag-scheduler) · [LiDAR and ROS 2](#lidar-and-ros-2) · [Patterns worth remembering](#patterns-worth-remembering)

## UWB on CLI firmware

<a name="c1"></a>

### C1. Tags time out and anchors cannot decode

- **Seen:** Tags print `status="RX_TIMEOUT"`; anchors print `status="RX_MAC_IE_DEC_FAILED"` with `mac_address=0x0000`
- **Cause:** Three things at once. The anchor had not been given the tag's address, so its STS setup did not match (`DST_MAC_ADDRESS: 0x0000` on the anchor, `0x0001` on the tag). `PDOAMODE` was 1 on the anchor and 0 on the tag. STS mode had to be on for both.
- **Fix:** Anchor: `LCFG -STSMODE=1`, `LCFG -PDOAMODE=0`, `SAVE`, `RESPF -MULTI -ADDR=1 -PADDR=11`. Tag: `LCFG -STSMODE=1`, `SAVE`, `INITF -MULTI -ADDR=11 -PADDR=1`.
- **Logs:** [success log](../logs/uwb-cli/08_one-to-one_SUCCESS.log)

<a name="c2"></a>

### C2. Commands that do not exist

- **Seen:** `set_addr 0x0001` returns `error unknown command "SET_ADDR"`
- **Cause:** The command does not exist in this firmware, and neither do `set_role`, `set_dest_addr`, `set_sts_key`, `set_panid` or `add_controlee`, which came with it. None of them is in the board's command list; the syntax was guessed.
- **Fix:** `HELP` lists the real commands: `STOP`, `INITF`, `RESPF`, `LCFG`, `SAVE`, `RESTORE`, `SETAPP`, `DECAID` and a few more.

<a name="c3"></a>

### C3. `LCFG` rejects the address

- **Seen:** `Incorrect command format ... Accepted command format: LCFG -<opt>=VALUE`, then `Unknown argument: ADDR=0X0001`
- **Cause:** `LCFG` takes `-NAME=VALUE`, and the address is not one of its parameters (`CHAN`, `PAC`, `PCODE`, `SFDTYPE`, `DRATE`, `PHRMODE`, `PHRRATE`, `STSMODE`, `STSLEN`, `PDOAMODE`, `XTALTRIM`).
- **Fix:** Pass the address to `INITF` / `RESPF` with `-ADDR=`.

<a name="c4"></a>

### C4. `-ADDR` is ignored without `-MULTI`

- **Seen:** `RESPF -ADDR=0x0001` runs but the dump still shows `DEVICE_MAC_ADDRESS: 0x0000`, `MULTI_NODE_MODE: UNICAST`
- **Cause:** `-ADDR` is only honoured in one-to-many mode.
- **Fix:** Add `-MULTI`: `RESPF -MULTI -ADDR=1`.

<a name="c5"></a>

### C5. `error incompatible mode` when starting a session

- **Seen:** `error incompatible mode` on `INITF -MULTI ...`; red LED D13 blinking
- **Cause:** `STSMODE` was 0 while the FiRa session uses an SP3 frame, which carries an STS.
- **Fix:** `LCFG -STSMODE=1`, `SAVE`, power-cycle.

<a name="c6"></a>

### C6. Characters lost in Tera Term

- **Seen:** Tera Term shows `error unknown command: "LCF"` and fragments of the board's own output echoed back as commands
- **Cause:** Not established. Dropped characters on the serial link were suspected.
- **Fix:** A transmit delay of 5 to 10 ms per character was suggested in Tera Term; later scripts add short pauses between commands.

<a name="c7"></a>

### C7. Only the first of four anchors answers

- **Seen:** One tag, four anchors: only anchor 1 answers; the tag's dump lists `DST_MAC_ADDRESS[0]` only
- **Cause:** The list was written `-PADDR=1,2,3,4`. The parser stops at the first comma.
- **Fix:** `-PADDR=[1,2,3,4]`, as the `INITF` help text shows.

<a name="c8"></a>

### C8. Anchor 2 refuses every command after power-up

- **Seen:** Anchor 2 after power-up: `STOPenough memory`, then `error incompatible mode` for `LCFG`, `SAVE`, `RESPF`; LED blinking instead of steady
- **Cause:** The board started a session by itself at power-up, so every configuration command arrived while it was active. Thought to be a bad saved configuration.
- **Fix:** Nothing over serial worked (see [C9](#c9) to [C11](#c11)). The way out was a full erase and reflash with J-Flash Lite: device `nRF52833_xxAA`, SWD, **Erase Chip**, then program. After that the board accepted commands again. No later CLI run with anchor 2 was logged.

<a name="c9"></a>

### C9. minicom is not installed

- **Seen:** `sudo: minicom: command not found`
- **Cause:** Not installed on Pi OS.
- **Fix:** `python3 -m serial.tools.miniterm /dev/ttyACM0 115200` (comes with pyserial; exit with Ctrl+]).

<a name="c10"></a>

### C10. Rescue script cannot open the port

- **Seen:** Rescue script: `Error: Could not open port. Make sure miniterm is closed!`, once before and twice after the background service was stopped
- **Cause:** Two diagnoses in a row. First: `qorvo-live.service` was still enabled on that Pi and restarted its script every time Python was killed, holding the port. The error stayed after the service was disabled. Second: the board had come back under another `/dev/ttyACM` number while the script had `/dev/ttyACM0` fixed.
- **Fix:** `sudo systemctl stop qorvo-live.service` and `sudo systemctl disable qorvo-live.service` on every Pi, then a rescue script that looks the port up. That version opened the port and ran into [C11](#c11).

<a name="c11"></a>

### C11. Rescue scripts do not bring the board back

- **Seen:** Rescue script: `write failed: [Errno 5] Input/output error`; later `*** GOT IT! BOARD TRAPPED IN IDLE ***` yet the board still refuses commands
- **Cause:** Pressing reset drops the USB port mid-write. Catching the board at boot did not clear whatever made it start by itself.
- **Fix:** None; led to the reflash in [C8](#c8).

<a name="c12"></a>

### C12. A second session on one board is refused

- **Seen:** A second `RESPF ... -ID=102` while the first session is active returns `error incompatible mode` (same on an anchor)
- **Cause:** The CLI firmware runs one ranging session at a time.
- **Fix:** No fix on CLI. This result is why the project moved to UCI.
- **Logs:** [tag log](../logs/uwb-cli/13_stacking-test_tag-1.log), [anchor log](../logs/uwb-cli/14_stacking-test_anchor-1.log)

<a name="c13"></a>

### C13. Qorvo's download page rejects a personal e-mail address

- **Seen:** Qorvo's download page rejects a personal e-mail address
- **Cause:** The portal accepts company or institution addresses only.
- **Fix:** Use an institutional address or ask Qorvo support. The SDK was obtained afterwards.

<a name="c14"></a>

### C14. Errors from the first setup, before 21 April

- **Seen:** Notes from the first setup list `unknown argument 2`, `error incompatible mode` and `fira_helper_add_controlee failed` for the multi-peer commands tried then
- **Cause:** According to those notes: address lists written in forms the parser rejects, and sessions restarted over and over by the service.
- **Fix:** The bracket form in [C7](#c7), and one clean start per board.

<a name="c15"></a>

### C15. Garbage instead of a prompt in miniterm

- **Seen:** miniterm on anchor 2 shows no prompt, then `error unknown command: "␃␃␘␚Q"`
- **Cause:** Part of [C8](#c8): the board was not sitting at its idle console.
- **Fix:** See [C8](#c8).

<a name="c16"></a>

### C16. Traceback ending in `KeyboardInterrupt`

- **Seen:** Script logs end with `^CTraceback (most recent call last): ... KeyboardInterrupt`
- **Cause:** Not a fault: the script was stopped with Ctrl+C.
- **Fix:** None.

## UWB on UCI firmware: host setup

<a name="u1"></a>

### U1. Virtual environment cannot be created

- **Seen:** `The virtual environment was not created successfully because ensurepip is not available`
- **Cause:** `python3.10-venv` not installed on the Jetson.
- **Fix:** `sudo apt install python3.10-venv python3-pip python3-dev`, delete the half-made venv, create it again.

<a name="u2"></a>

### U2. `apt` stops on the ROS 2 repository entry

- **Seen:** `E: Conflicting values set for option Signed-By regarding source http://packages.ros.org/ros2/ubuntu/ jammy` and `E: The list of sources could not be read.`
- **Cause:** A half-finished ROS 2 repository entry with a conflicting key. It blocks every `apt` command.
- **Fix:** `sudo rm /etc/apt/sources.list.d/ros2.list`, `sudo rm -f /usr/share/keyrings/ros-archive-keyring.gpg`, `sudo apt update`.

<a name="u3"></a>

### U3. `source` used on the venv folder

- **Seen:** `bash: source: /home/jetson1/uwb_venv: is a directory`
- **Cause:** Sourced the folder instead of the activate script.
- **Fix:** `source ~/uwb_venv/bin/activate`

<a name="u4"></a>

### U4. `scp` not recognised in PowerShell

- **Seen:** PowerShell on Windows 10: `scp : The term 'scp' is not recognized` although OpenSSH Client is installed
- **Cause:** `scp.exe` not on the PATH of that shell.
- **Fix:** Run it from `cmd`, or call `C:\Windows\System32\OpenSSH\scp.exe` by its full path.

<a name="u5"></a>

### U5. `pip install -e .` fails on PySide2

- **Seen:** `pip install -e .` ends with `No matching distribution found for PySide2==5.15.2.1` (Jetson and Pi)
- **Cause:** PySide2 has no wheel for these ARM boards. It is only needed for the plotting tools.
- **Fix:** `pip install ./lib/uwb-uci ./lib/uqt-utils pyserial colorama` and start the scripts by path.

<a name="u6"></a>

### U6. `run_fira_twr: command not found`

- **Seen:** `run_fira_twr: command not found`
- **Cause:** The console command is only registered by the full package install, which [U5](#u5) skips.
- **Fix:** `python3 scripts/fira/run_fira_twr/run_fira_twr.py ...`

<a name="u7"></a>

### U7. Permission denied on the serial port

- **Seen:** `PermissionError: [Errno 13] Permission denied: '/dev/ttyACM0'`
- **Cause:** The user is not allowed to open the serial device.
- **Fix:** Immediately: `sudo chmod 666 /dev/ttyACM0`. Permanently: add the user to `dialout` and install [`99-uwb.rules`](../config/udev/99-uwb.rules).

<a name="u8"></a>

### U8. Three slips while fixing the port permission

- **Seen:** `chmod: cannot access '/dev/ttyACMO'`; `usermod` prints its usage; `nano: command not found`
- **Cause:** Letter O typed for zero; `$J1` typed for `$USER`; nano is not part of the minimal Jetson image.
- **Fix:** Use Tab completion for device names; `sudo apt install nano`.

<a name="u9"></a>

### U9. A script path that does not exist (Windows)

- **Seen:** Windows: `can't open file '...\scripts\fira\fira_twr\fira_twr.py'`
- **Cause:** That path was a guess. The script is `scripts\fira\run_fira_twr\run_fira_twr.py`.
- **Fix:** List the folder first; set the port with `$env:UQT_PORT = "COM18"`.

<a name="u10"></a>

### U10. Python 3.13 rejected by the Qorvo library (Raspberry Pi)

- **Seen:** Raspberry Pi: `Package 'uwb-uci' requires a different Python: 3.13.5 not in '<3.11.0,>=3.9'`
- **Cause:** Pi OS ships Python 3.13; the Qorvo library supports 3.9 and 3.10 only.
- **Fix:** Build Python 3.10.16 from source with `make altinstall`.

<a name="u11"></a>

### U11. `make` run before `./configure`

- **Seen:** `make: *** No targets specified and no makefile found`
- **Cause:** `./configure` was skipped.
- **Fix:** `./configure --enable-optimizations`, then `make -j4`, then `sudo make altinstall`.

<a name="u12"></a>

### U12. Virtual environment still on Python 3.13

- **Seen:** The new venv still reports Python 3.13.5; `uwb_venv/bin/python3 -> /usr/bin/python3`
- **Cause:** The venv was made by the wrong interpreter, and the source-built 3.10 lacks `ensurepip`.
- **Fix:** `/usr/local/bin/python3.10 -m venv ~/uwb_venv --without-pip`, activate, then `curl https://bootstrap.pypa.io/get-pip.py -o /tmp/get-pip.py` and `python3 /tmp/get-pip.py`.

<a name="u13"></a>

### U13. Script run from the wrong folder

- **Seen:** `python3: can't open file '/home/jetson1/scripts/device/...'`
- **Cause:** Command run from the home folder.
- **Fix:** `cd ~/uwb-qorvo-tools` first.

<a name="u14"></a>

### U14. `get_mac_address.py` does not exist

- **Seen:** `can't open file '.../get_mac_address/get_mac_address.py'`
- **Cause:** That script does not exist in the SDK.
- **Fix:** Check what exists before running: [folder listing](../logs/uwb-uci/05_windows_script-folder-listing.log).

<a name="u15"></a>

### U15. No `.py` files directly in `scripts/`

- **Seen:** `ls: cannot access '.../uwb-qorvo-tools/scripts/*.py': No such file or directory`
- **Cause:** The scripts are not directly in `scripts/`; they sit in the subfolders `device`, `fira`, `qorvo` and `utils`
- **Fix:** Call them by their full path, for example `scripts/fira/run_fira_twr/run_fira_twr.py`

<a name="u16"></a>

### U16. `dmesg` needs root

- **Seen:** `dmesg: read kernel buffer failed: Operation not permitted`
- **Cause:** Reading the kernel log needs root on this Ubuntu.
- **Fix:** `sudo dmesg | tail -20`

<a name="u17"></a>

### U17. Follow-on `AttributeError` after the permission error

- **Seen:** `AttributeError: 'UartTransport' object has no attribute 'serial'` directly after the permission error in [U7](#u7)
- **Cause:** Follow-on message: the port was never opened, so the clean-up code had nothing to close.
- **Fix:** Fix [U7](#u7).

<a name="u18"></a>

### U18. Wrong interpreter path, and a venv that was just deleted

- **Seen:** `-bash: /usr/local/lib/python3.10: Is a directory`, then `-bash: /home/pi3/uwb_venv/bin/activate: No such file or directory`
- **Cause:** The interpreter is `/usr/local/bin/python3.10` (`lib` is its library folder), and the venv had just been deleted.
- **Fix:** Recreate the venv with `/usr/local/bin/python3.10 -m venv ~/uwb_venv --without-pip`

<a name="u19"></a>

### U19. `LS` typed in capitals

- **Seen:** `-bash: LS: command not found`
- **Cause:** Commands are case-sensitive.
- **Fix:** `ls`

<a name="u20"></a>

### U20. PowerShell `cd` into the folder it is already in

- **Seen:** PowerShell: `cd : Cannot find path '...\uwb-qorvo-tools\V2X\DW3_QM33_SDK_1.1.1\...' because it does not exist`
- **Cause:** The shell was already in that folder, so the relative path was appended to it.
- **Fix:** Nothing to do; carry on from the current folder.

## UWB on UCI firmware: ranging

<a name="r1"></a>

### R1. Leftover sessions report timeouts and 65535 cm

- **Seen:** Extra session handles reporting `RangingRxTimeout (0x21)` and 65535 cm beside the one that works
- **Cause:** Sessions left open by earlier runs on the same board. 65535 cm is the "no measurement" value.
- **Fix:** `reset_device.py`, or unplug and replug the board, before a new test.

<a name="r2"></a>

### R2. Board stops answering: `TimeoutError (0x3)`

- **Seen:** `UciComError.TimeoutError (0x3): No response from the device (4s timeout)` at "Initializing session 42" or from `reset_device.py`
- **Cause:** The board stops answering UCI after a session that did not end cleanly, or after sitting idle. Nothing tried from software brought it back; the reset button (SW1) is the quicker alternative to unplugging.
- **Fix:** Unplug for about 10 seconds, replug, confirm with `get_device_info.py`. Prevented later by bounded runs ([S5](#s5)).

<a name="r3"></a>

### R3. `UnknownPort (0x1)`

- **Seen:** `UciComError.UnknownPort (0x1): "/dev/ttyACM0" is not supported`
- **Cause:** Nothing at that path: board unplugged, or back under another number.
- **Fix:** `ls /dev/ttyACM*`, then use the number shown.

<a name="r4"></a>

### R4. Second tag gets only timeouts

- **Seen:** A second tag started while the first is ranging gets `RangingRxTimeout (0x21)`, 65535 cm, `slot in error: 2, 3, 4` on every measurement
- **Cause:** Both tags act as initiators toward the same anchors with the same default profile and collide. The SDK script gives no way to coordinate them.
- **Fix:** Let the tags take turns: see [the two-tag scheduler](#the-two-tag-scheduler).
- **Logs:** [log](../logs/uwb-uci/10_two-tags_jetson-2-all-timeouts.log)

<a name="r5"></a>

### R5. Anchors show every tag as `00:00` (open)

- **Seen:** Anchors print `mac address: 00:00 hex` for the device they range with
- **Cause:** Both tags run with the default device address `0x0` (see the [session dump](../config/uwb/radio-and-session-parameters.md)). An anchor cannot tell the tags apart; each tag does know which anchor a distance belongs to.
- **Fix:** None needed for ranging. To be solved before anchors are used to tell robots apart.

<a name="r6"></a>

### R6. Angle-of-arrival fields are all zero

- **Seen:** All AoA fields read 0.0 and `is nlos meas: Unsupported`
- **Cause:** The DWM3001CDK has one antenna; angle of arrival needs two.
- **Fix:** Ignore. Position comes from three distances.

<a name="r7"></a>

### R7. A single `RangingRxPhyDecFailed (0x22)`

- **Seen:** A single `RangingRxPhyDecFailed (0x22)` in a run of good measurements
- **Cause:** One frame not decoded; the next round was fine.
- **Fix:** None.

## The two-tag scheduler

The sequence of attempts at running two tags. Script versions are in [`code/uwb-uci/history/`](../code/README.md).

<a name="s1"></a>

### S1. A path that does not exist in the first script

- **Seen:** `cd: /home/jetson1/uwb-qorvo-tools/source: No such file or directory`
- **Cause:** A path that does not exist.
- **Fix:** Scripts run from `~/uwb-qorvo-tools`.

<a name="s2"></a>

### S2. `--session-id` is not an option

- **Seen:** `run_fira_twr.py: error: unrecognized arguments: --session-id 1`; `kill: (6711) - No such process`; anchors show 65535 cm
- **Cause:** The option does not exist, so the tags never started.
- **Fix:** The session option is `-s`.
- **Logs:** [attempt 1](../logs/uwb-uci/20_demo_attempt-1_session-id-rejected.log)

<a name="s3"></a>

### S3. `EOFError` in a background job

- **Seen:** `EOFError: EOF when reading a line` at `input("Press <RETURN> to stop\n")`
- **Cause:** Run with `-t -1` in the background, the script waits for a key press it can never get.
- **Fix:** Run for a fixed time: `-t 3`. No background jobs, no `kill`.

<a name="s4"></a>

### S4. Anchors reject every frame: `RangingRxMacIeDecFailed (0x26)`

- **Seen:** Anchors: `RangingRxMacIeDecFailed (0x26)` on every frame, with and without the SSH quoting fix
- **Cause:** Tags started with `--mac 0x4` / `0x5` and `-s 1` / `2`, anchors with their defaults. The first guess (SSH stripping quotes) was wrong: the error stayed after the heredoc.
- **Fix:** Remove `--mac` and `-s` from the tag commands.
- **Logs:** [attempt 2](../logs/uwb-uci/21_demo_attempt-2_eoferror_mac-ie-dec-failed.log), [attempt 3](../logs/uwb-uci/22_demo_attempt-3_mac-ie-dec-failed.log)

<a name="s5"></a>

### S5. Boards need a power-cycle after every stop

- **Seen:** Boards need a power-cycle after every stop
- **Cause:** An interrupted script never sends the stop and de-initialise commands; the board stays in its active session.
- **Fix:** The same `-t 3`: the tool prints `Stopping ranging... Deinitializing session... Ok` and the board accepts the next session.

<a name="s6"></a>

### S6. SSH turn for Jetson 2 never completes

- **Seen:** On Jetson 2's turn: `Pseudo-terminal will not be allocated because stdin is not a terminal.`, the login banner, `Initializing session 42...`, then `^Z` and `[5]+ Stopped ~/uwb-qorvo-tools/demo_runner.sh`
- **Cause:** Most likely, SSH hung over terminal allocation when it was given its commands through a heredoc. The log itself shows the run being suspended with Ctrl+Z just after Jetson 2 began to initialise, so what would have happened next is not known.
- **Fix:** `ssh -T`. In the next run both tags ranged.

<a name="s7"></a>

### S7. Serial port number changes after every session

- **Seen:** Second loop: `UciComError.UnknownPort (0x1): "/dev/ttyACM1" is not supported`; `ls` now shows `/dev/ttyACM2`; a Pi reached `/dev/ttyACM9`
- **Cause:** After each session the board re-enumerates and Linux assigns the next number.
- **Fix:** `J1_PORT=$(ls /dev/ttyACM* | head -n 1)` before each run, on both Jetsons. Keep other USB serial devices unplugged.

<a name="s8"></a>

### S8. Anchors time out between turns (expected)

- **Seen:** Anchors log `RangingRxTimeout` between the tags' turns
- **Cause:** Expected: for about a second nobody is talking to them.
- **Fix:** None.

<a name="s9"></a>

### S9. nano missing on Jetson 2

- **Seen:** `-bash: nano: command not found` on Jetson 2 while creating the script
- **Cause:** nano is not installed there. The script also belongs on Jetson 1, which does the scheduling.
- **Fix:** Create the script on Jetson 1 (`sudo apt install nano -y` if needed).

## LiDAR and ROS 2

<a name="l1"></a>

### L1. Package folder does not exist

- **Seen:** `cd ~/ros2_ws/src/lidar_obstacle_detector/...: No such file or directory`
- **Cause:** The package had never been created; the node file was in the home folder.
- **Fix:** `ros2 pkg create lidar_obstacle_detector --build-type ament_python --dependencies rclpy sensor_msgs geometry_msgs std_msgs`, move the node into the package, add the entry point to `setup.py`, `colcon build`.

<a name="l2"></a>

### L2. `ros2 pkg create` asks for a package name

- **Seen:** `ros2 pkg create`: package name required
- **Cause:** The name was missing from the end of a command split over several lines.
- **Fix:** Type the command on one line with the name first.

<a name="l3"></a>

### L3. Gazebo Classic cannot be installed

- **Seen:** `ros-humble-gazebo-dev : Depends: gazebo but it is not installable`; `Package 'gazebo' has no installation candidate`
- **Cause:** Gazebo Classic packages are not available for the Jetson's Ubuntu 22.04 arm64 setup, and Gazebo Classic is end-of-life.
- **Fix:** Skip simulation; run SLAM on the real sensor.
- **Logs:** [log](../logs/lidar/02_gazebo-classic_install-errors.log)

<a name="l4"></a>

### L4. RViz has no display, then the driver times out

- **Seen:** `qt.qpa.xcb: could not connect to display` (rviz2), then `SL_RESULT_OPERATION_TIMEOUT` from the driver
- **Cause:** The `view_...` launch file also starts RViz, and the shell it was run from had no display to open it on (probably an SSH or headless login). The timeout was put down to port, baud rate, power or a second process on the port.
- **Fix:** Run the launch from the Jetson's own desktop; replug the LiDAR; make sure only one driver is running. When RViz still cannot find a display with a monitor attached, try `export DISPLAY=:0`, or `ssh -X` for a remote shell.

<a name="l5"></a>

### L5. `rplidar.launch.py` not found

- **Seen:** `file 'rplidar.launch.py' was not found in the share directory of package 'rplidar_ros'`
- **Cause:** The apt package has no launch file of that name.
- **Fix:** Build `sllidar_ros2` in the workspace and use `ros2 launch sllidar_ros2 view_sllidar_a2m12_launch.py`.

<a name="l6"></a>

### L6. RF2O waits for scans without end (open)

- **Seen:** RF2O prints `Waiting for laser_scans....` without end
- **Cause:** At one point the LiDAR was not spinning. Beyond that, never resolved: topic name (`/laser_scan` by default), TF and start-up parameters were all tried.
- **Fix:** Open.
- **Logs:** [log](../logs/lidar/04_2026-05-22_rf2o_waiting-for-laser-scans.log)

<a name="l7"></a>

### L7. Empty parameter on the command line

- **Seen:** `Couldn't parse parameter override rule: '-p init_pose_from_topic:='`
- **Cause:** An empty string cannot be passed that way on the command line.
- **Fix:** Leave the parameter out.

<a name="l8"></a>

### L8. Two LiDAR drivers at once

- **Seen:** `ros2 topic info /scan` shows two publishers; both `/rplidar_node` and `/sllidar_node` appear in node lists
- **Cause:** Two LiDAR drivers running at once.
- **Fix:** Stop one; keep a single source of `/scan`.

<a name="l9"></a>

### L9. No `odom` frame (open)

- **Seen:** `tf2_echo odom base_link`: `Invalid frame ID "odom" ... frame does not exist`; `view_frames` shows only `base_link -> laser`
- **Cause:** Nothing publishes odometry: there are no wheels yet. `slam_toolbox` expects `map -> odom -> base_link -> laser`.
- **Fix:** Open. Options discussed: laser odometry (RF2O), an IMU, or waiting for the robot base.
- **Logs:** [log](../logs/lidar/05_2026-05-26_topics-nodes_and_tf-without-odom.log)

<a name="l10"></a>

### L10. RViz "Global Status: Error" (open)

- **Seen:** RViz "Global Status: Error" ("fixed frame error"); no map shown
- **Cause:** The fixed frame `map` does not exist until SLAM publishes it, and the TF chain was incomplete.

<a name="l11"></a>

### L11. `/scan` is not published

- **Seen:** `WARNING: topic [/scan] does not appear to be published yet` and `Could not determine the type for the passed topic`
- **Cause:** No LiDAR driver was running at that moment.
- **Fix:** Start the driver and check `ros2 topic list` first.

<a name="l12"></a>

### L12. RF2O node not found

- **Seen:** `Unable to find node '/CLaserOdometry2DNode'`
- **Cause:** RF2O had exited; `ros2 node list` shows only the driver and two static transform publishers.
- **Fix:** Restart RF2O. Its start-up problem was never resolved ([L6](#l6)).

<a name="l13"></a>

### L13. `/async_slam_toolbox_node` not found

- **Seen:** `Unable to find node '/async_slam_toolbox_node'`
- **Cause:** The node is named `/slam_toolbox` in this launch.
- **Fix:** `ros2 node info /slam_toolbox`

<a name="l14"></a>

### L14. "Old-style arguments are deprecated" warning

- **Seen:** `[WARN] Old-style arguments are deprecated; see --help for new-style arguments` from `static_transform_publisher`
- **Cause:** Harmless. The next lines show the transform being published.
- **Fix:** None.

<a name="l15"></a>

### L15. FastDDS shared-memory error; `ros2 topic echo` prints nothing (open)

- **Seen:** `[RTPS_TRANSPORT_SHM Error] Failed init_port fastrtps_port7425: open_and_lock_file failed` on `ros2 topic echo /tf --once`; later `echo` prints nothing at all
- **Cause:** Diagnosed as a FastDDS shared-memory transport problem.
- **Fix:** Suggested: switch to CycloneDDS (see [L16](#l16)) or disable shared memory. Not confirmed. The checks moved to `ros2 topic info` and the TF tools, which worked.

<a name="l16"></a>

### L16. CycloneDDS selected but not installed

- **Seen:** `Error getting RMW implementation identifier / RMW implementation not installed (expected identifier of 'rmw_cyclonedds_cpp')`
- **Cause:** `RMW_IMPLEMENTATION=rmw_cyclonedds_cpp` had been exported in that terminal, but the package is not installed.
- **Fix:** `sudo apt install ros-humble-rmw-cyclonedds-cpp`, or `unset RMW_IMPLEMENTATION` to return to the default. Which one was used was not noted.

<a name="l17"></a>

### L17. `ros2 lifecycle set` answers "Node not found"

- **Seen:** `ros2 lifecycle set /rplidar_node shutdown` answers `Node not found`
- **Cause:** The driver is not a lifecycle node.
- **Fix:** Ctrl+C in the terminal that launched it, or `pkill -f rplidar`

## Patterns worth remembering

Noticed while going back through the logs. These are observations, not confirmed conclusions.

- **Ctrl+Z is not Ctrl+C.** Most runs in the logs end with `^Z` and a line such as `[14]+ Stopped ~/uwb-qorvo-tools/demo_runner.sh`. Ctrl+Z suspends a program; it does not end it. The suspended copy keeps its serial port open and never sends the UWB stop command. Job numbers climb to 14 on Jetson 1, and a Pi's port number to `/dev/ttyACM9`. This fits the "board stops answering" and "port number keeps rising" symptoms ([R2](#r2), [S7](#s7)) and is worth ruling out first: stop with Enter (for a `-t -1` run) or Ctrl+C, and bring back any paused copy with `fg` to stop it properly (`jobs` lists them).
- **Start the listeners first.** On both firmwares the anchors must be running before a tag starts, or the first rounds time out.
- **Compare the two ends.** The decisive step in April was putting the tag's and the anchor's parameter dumps side by side.
- **Check what exists before running it.** Several dead ends came from commands and file names that were never real: `set_addr`, `fira_twr.py`, `rplidar.launch.py`, `get_mac_address.py`, `--session-id`. The board's `HELP`, a script's `--help` and a folder listing settled each one.
