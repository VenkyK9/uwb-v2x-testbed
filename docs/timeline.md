# Timeline

Dates come from timestamps in the logs and from the project notes. Where a step has no timestamp of its own it is placed between the dated events around it. Times are as printed by the devices.

| When | What happened |
|---|---|
| 16 Apr 2026 | Study of the theory: why UWB took 12 years to reach phones, how it works, what STS is, why BLE cannot do the same. |
| 21 Apr 2026, about 20:10 to 20:21 | CLI firmware on the boards, started on each Raspberry Pi by a `qorvo-live.service`. Tags (pi1, pi2) log `RX_TIMEOUT`; anchors (pi4, pi5, pi6) log `RX_MAC_IE_DEC_FAILED`. |
| 21 to 27 Apr | Start over from a clean state. The earlier setup is reviewed to see what had been configured. |
| | The real command syntax is found from the board's own help output: no `SET_ADDR`; the address is an argument of `INITF` / `RESPF`. |
| | Address only takes effect with `-MULTI`; `error incompatible mode` cured by enabling STS. Manual 1:1 ranging works in a terminal. |
| | Scripted 1:1 on two Pis keeps failing until the cause is found: the anchor was not told the tag's address, and the PDoA modes differed. |
| | **First scripted success: 1 tag and 1 anchor, about 1.5 m.** |
| | Four anchors: only anchor 1 answers until the list is written `-PADDR=[1,2,3,4]`. **1 tag ranges with 4 anchors.** |
| | Adding tag 2: anchor 2 comes up refusing every command. Three rescue scripts fail. The way out is a full erase and reflash. |
| | Test of several sessions on one board ("stacking"): the second `RESPF` is refused. The CLI firmware runs one session at a time. |
| 27 Apr 2026 | Decision to move every board to the UCI firmware. |
| Early May | All six boards flashed with UCI firmware and calibrated. Jetson 1 prepared (venv, tools, serial access). **1 tag and 1 anchor range at about 92 cm**, anchor on a Windows PC (the log was not kept). |
| 4 May 2026, about 02:00 | Raspberry Pi 3 prepared: Python 3.10 built from source because Pi OS ships 3.13. Pi 1 and Pi 2 follow. |
| After 4 May | **1 tag ranges with 3 anchors** (about 343, 436 and 466 cm; the log was not kept). |
| 7 May 2026, 10:46 | RPLIDAR A2M12 publishing `/scan` on Jetson 1. The obstacle-detection node is written from this scan and reported working. |
| 22 May 2026, 14:49 to 15:34 | SLAM attempts: RViz cannot open a display, the driver times out, RF2O waits for scans. |
| 26 May 2026, 15:14 | The TF tree holds only `base_link -> laser`; there is no `odom` frame, so `slam_toolbox` cannot complete its chain. |
| About 28 May 2026 | Two Jetsons, three Pis, UCI firmware. Started together, Jetson 1 ranges and Jetson 2 gets only timeouts. Boards stop answering after a session and need unplugging. |
| On or after 28 May | The time-slicing scheduler: three failed attempts, then **both tags ranging in turn**. These logs carry clock times but no dates. |
| After that | Project presentation and written report. |
| June 2026 | End of the project. |

## Phases at a glance

1. **CLI firmware (April).** Text commands over serial. Good for proving the radios work; cannot serve two tags.
2. **UCI firmware bring-up (early May).** Qorvo's Python tools on Jetson and Pi. One tag with three anchors works.
3. **LiDAR (May, in parallel).** Obstacle detection done; SLAM blocked on odometry.
4. **Two tags (from 28 May).** Collisions, then the scheduler that makes them take turns.
