# Logs

Device and terminal output saved during the project, one file per test. Short labels such as `Pi1:` mark which device produced each part, and `# ----` separates pieces of output from the same test. Board serial numbers (`soc id`) have been removed.

## UWB, CLI firmware

| File | What it shows |
|---|---|
| [`uwb-cli/01_2026-04-21_journalctl_tags-timeout_anchors-dec-failed.log`](uwb-cli/01_2026-04-21_journalctl_tags-timeout_anchors-dec-failed.log) | journalctl of qorvo-live.service on pi1, pi2 (tags) and pi4, pi5, pi6 (anchors): RX_TIMEOUT and RX_MAC_IE_DEC_FAILED. |
| [`uwb-cli/02_cli-help-menu.log`](uwb-cli/02_cli-help-menu.log) | 'unknown command SET_ADDR' and the CLI HELP menu of the DW3_QM33_SDK FreeRTOS build. |
| [`uwb-cli/03_teraterm_lcfg-command-format.log`](uwb-cli/03_teraterm_lcfg-command-format.log) | Tera Term session with garbled input and the hint 'Accepted command format: LCFG -&lt;opt&gt;=VALUE'. |
| [`uwb-cli/04_lcfg-parameters_and_initf-options.log`](uwb-cli/04_lcfg-parameters_and_initf-options.log) | LCFG PARAM list, 'Unknown argument: ADDR', the INITF option help and the -MULTI command forms. |
| [`uwb-cli/05_responder-session-parameters_addr-0000.log`](uwb-cli/05_responder-session-parameters_addr-0000.log) | FiRa session parameters of a responder that kept address 0x0000 (UNICAST, SP3, channel 9). |
| [`uwb-cli/06_one-to-one_fail_run-1.log`](uwb-cli/06_one-to-one_fail_run-1.log) | 1:1 test, first scripts: tag RX_TIMEOUT; anchor alternating RX_MAC_IE_DEC_FAILED and RX_TIMEOUT. |
| [`uwb-cli/07_one-to-one_fail_run-2_sts-enabled.log`](uwb-cli/07_one-to-one_fail_run-2_sts-enabled.log) | 1:1 test with STS enabled on both: still failing. Shows PDOAMODE 0 on the tag and 1 on the anchor. |
| [`uwb-cli/08_one-to-one_SUCCESS.log`](uwb-cli/08_one-to-one_SUCCESS.log) | First successful ranging: tag 0x000B and anchor 0x0001, 151 to 160 cm. |
| [`uwb-cli/09_one-tag-four-anchors_only-anchor-1-answers.log`](uwb-cli/09_one-tag-four-anchors_only-anchor-1-answers.log) | 1 tag, 4 anchors, list written without brackets: DST_MAC_ADDRESS[0] only; anchors 2 to 4 time out. |
| [`uwb-cli/10_one-tag-four-anchors_SUCCESS.log`](uwb-cli/10_one-tag-four-anchors_SUCCESS.log) | n_measurements=4: distances to anchors 1 to 4 (about 146, 233, 330 and 222 cm). |
| [`uwb-cli/11_anchor-2_incompatible-mode.log`](uwb-cli/11_anchor-2_incompatible-mode.log) | Anchor 2 after power-up: 'STOPenough memory' and 'error incompatible mode' for every command. |
| [`uwb-cli/12_anchor-2_miniterm_and_rescue-attempts.log`](uwb-cli/12_anchor-2_miniterm_and_rescue-attempts.log) | Anchor 2 recovery attempts: miniterm session, rescue script outputs, the state after 'BOARD TRAPPED IN IDLE'. |
| [`uwb-cli/13_stacking-test_tag-1.log`](uwb-cli/13_stacking-test_tag-1.log) | Session-stacking test on tag 1: first RESPF goes ACTIVE, second RESPF returns 'error incompatible mode'. |
| [`uwb-cli/14_stacking-test_anchor-1.log`](uwb-cli/14_stacking-test_anchor-1.log) | The same test on anchor 1 with the same result. |

## UWB, UCI firmware: bring-up

| File | What it shows |
|---|---|
| [`uwb-uci/01_jetson_venv_and_ros-apt-keyring-conflict.log`](uwb-uci/01_jetson_venv_and_ros-apt-keyring-conflict.log) | python3 -m venv fails (ensurepip missing); apt stops on a conflicting Signed-By entry for the ROS 2 repository. |
| [`uwb-uci/02_jetson_pip-install_pyside2-missing.log`](uwb-uci/02_jetson_pip-install_pyside2-missing.log) | 'pip install -e .' on the Jetson: no PySide2==5.15.2.1 wheel for this platform. |
| [`uwb-uci/03_jetson_permission-denied_ttyACM0.log`](uwb-uci/03_jetson_permission-denied_ttyACM0.log) | get_device_info.py: [Errno 13] Permission denied on /dev/ttyACM0. |
| [`uwb-uci/04_jetson-1_get-device-info_ok.log`](uwb-uci/04_jetson-1_get-device-info_ok.log) | get_device_info on the Jetson 1 tag board: status Ok, UCI 2.0.0, device id deca0302. |
| [`uwb-uci/05_windows_script-folder-listing.log`](uwb-uci/05_windows_script-folder-listing.log) | Folder listing of uwb-qorvo-tools/scripts on the Windows PC (which scripts exist). |
| [`uwb-uci/06_pi3_python-3.13_rejected_and_venv-symlinks.log`](uwb-uci/06_pi3_python-3.13_rejected_and_venv-symlinks.log) | Pi 3: uwb-uci requires Python &gt;=3.9,&lt;3.11; make without configure; a venv that still points at Python 3.13. |
| [`uwb-uci/07_two-tags_timeouts-permissions-unknown-port.log`](uwb-uci/07_two-tags_timeouts-permissions-unknown-port.log) | First two-tag session: TimeoutError (0x3) on Jetson 1, permission error on Jetson 2, UnknownPort on the Pis. |
| [`uwb-uci/08_anchors_ranging-ok_one-tag.log`](uwb-uci/08_anchors_ranging-ok_one-tag.log) | Pi 1 to 3 anchor output while one tag ranges: Ok at 281 to 288, 222 to 228 and 287 to 288 cm. |
| [`uwb-uci/09_jetson-1_usb-check_and_device-info.log`](uwb-uci/09_jetson-1_usb-check_and_device-info.log) | Jetson 1 not answering, lsusb (Nordic 1915:520f), wrong working directory, then device info Ok. |
| [`uwb-uci/10_two-tags_jetson-2-all-timeouts.log`](uwb-uci/10_two-tags_jetson-2-all-timeouts.log) | Both tags started together: Jetson 1 gets 330 / 219 / 362 cm; Jetson 2 gets RangingRxTimeout with slot errors. |
| [`uwb-uci/11_jetson-2_device-info_ok.log`](uwb-uci/11_jetson-2_device-info_ok.log) | Jetson 2 tag board: lsusb and get_device_info Ok on /dev/ttyACM1. |

## UWB, UCI firmware: time-slicing scheduler

| File | What it shows |
|---|---|
| [`uwb-uci/20_demo_attempt-1_session-id-rejected.log`](uwb-uci/20_demo_attempt-1_session-id-rejected.log) | Attempt 1: run_fira_twr.py prints its usage ('unrecognized arguments: --session-id'); anchors show 65535 cm. |
| [`uwb-uci/21_demo_attempt-2_eoferror_mac-ie-dec-failed.log`](uwb-uci/21_demo_attempt-2_eoferror_mac-ie-dec-failed.log) | Attempt 2: EOFError at 'Press &lt;RETURN&gt; to stop' in a background job; anchors RangingRxMacIeDecFailed (0x26). |
| [`uwb-uci/22_demo_attempt-3_mac-ie-dec-failed.log`](uwb-uci/22_demo_attempt-3_mac-ie-dec-failed.log) | Attempt 3: tags with explicit MAC and session; anchors still 0x26. |
| [`uwb-uci/23_demo_jetson-1-ok_ssh-stall.log`](uwb-uci/23_demo_jetson-1-ok_ssh-stall.log) | Default profile: Jetson 1 ranges (about 343 to 412 cm); on Jetson 2's turn SSH prints 'Pseudo-terminal will not be allocated' and the run is suspended at 'Initializing session 42...'. |
| [`uwb-uci/24_demo_both-tags-ok_then-unknown-port.log`](uwb-uci/24_demo_both-tags-ok_then-unknown-port.log) | ssh -T: both tags range; includes the UCI session configuration dump; second loop hits UnknownPort /dev/ttyACM1. |
| [`uwb-uci/25_pi-1_no-response-from-device.log`](uwb-uci/25_pi-1_no-response-from-device.log) | Pi 1 after many restarts: port at /dev/ttyACM9 and TimeoutError (0x3). |
| [`uwb-uci/26_demo_FINAL_SUCCESS.log`](uwb-uci/26_demo_FINAL_SUCCESS.log) | Final scheduler: continuous Ok measurements from both tags (one RangingRxPhyDecFailed). |

## LiDAR / ROS 2

| File | What it shows |
|---|---|
| [`lidar/01_2026-05-07_scan-topic_three-messages.log`](lidar/01_2026-05-07_scan-topic_three-messages.log) | Three /scan messages from the A2M12 (frame 'laser', 0.15 to 16 m, ranges about 2.1 to 2.6 m). |
| [`lidar/02_gazebo-classic_install-errors.log`](lidar/02_gazebo-classic_install-errors.log) | apt cannot install ros-humble-gazebo-* / gazebo / libgazebo-dev on the Jetson. |
| [`lidar/03_2026-05-22_rplidar-launch_no-display_timeout.log`](lidar/03_2026-05-22_rplidar-launch_no-display_timeout.log) | view_rplidar_a2m12_launch.py: rviz2 cannot open a display; the driver ends with SL_RESULT_OPERATION_TIMEOUT. |
| [`lidar/04_2026-05-22_rf2o_waiting-for-laser-scans.log`](lidar/04_2026-05-22_rf2o_waiting-for-laser-scans.log) | RF2O laser odometry: endless 'Waiting for laser_scans....'; parameter override parse error. |
| [`lidar/05_2026-05-26_topics-nodes_and_tf-without-odom.log`](lidar/05_2026-05-26_topics-nodes_and_tf-without-odom.log) | Topic and node list with two LiDAR drivers running; view_frames shows only base_link -&gt; laser, no odom. |
