# Hardware

What the project used and what it planned to use, and the role each device played. "In use" means the device shows up in the logs or terminal prompts. "Planned" means it is named in the plans only.

## UWB boards

Six Qorvo DWM3001CDK development boards, intended as three tags (one per robot) and three fixed anchors.

| Item | Detail |
|---|---|
| Board | DWM3001CDK: DWM3001C module (DW3110 UWB transceiver + Nordic nRF52833 microcontroller) with an on-board J-Link |
| Antenna | One. The board measures distance only; the angle-of-arrival fields in the UCI output stay at zero |
| USB connector J9 | Goes to the on-board J-Link. Used for flashing firmware |
| USB connector J20 | Goes to the nRF52833. Used for everything else: the CLI console and the UCI link. Appears as `/dev/ttyACM*` on Linux and as a COM port on Windows |
| USB identity on Linux | `1915:520f Nordic Semiconductor ASA nRF52 USB Product` |
| Button SW1 | Hardware reset |
| LED D13 | Described as the DW3110 transmit/receive indicator. It blinked red while a tag could not start its session |
| Green LED | Steady on a healthy board; blinking on the anchor that refused every command. Blinking was read at the time as "radio active" |

Descriptions of where J9 and J20 sit on the board vary; go by the labels printed on the board.

Any board can be a tag or an anchor. The role comes from the command that starts it, not from the board. Each board reports a unique `soc id` through `get_device_info.py`, which is a reliable way to tell boards apart. The IDs are removed from the logs in this repository.

## Firmware and SDK

Both firmware images come from Qorvo's `DW3_QM33_SDK_1.1.1` (folder `SDK\Binaries\DWM3001CDK`). The Python tools are in `SDK\Tools\uwb-qorvo-tools`.

| | CLI firmware | UCI firmware |
|---|---|---|
| File | `DWM3001CDK-DW3_QM33_SDK_CLI-FreeRTOS.hex` | `DWM3001CDK-DW3_QM33_SDK_UCI-FreeRTOS.hex` |
| Used | April 2026 | From early May 2026, on all six boards |
| Driven by | Text commands on the serial console: `INITF`, `RESPF`, `LCFG`, `SAVE`, `STOP` | Qorvo's Python tools (`run_fira_twr.py` and others), which speak UCI over the same USB port |
| Identifies itself as | `DWM3001CDK - DW3_QM33_SDK - FreeRTOS` in the help banner | uci, mac and phy version 2.0.0; uci test version 1.1.0; QMF 1.1.0; device id `deca0302` |
| Flashing | J-Flash Lite through J9, device `nRF52833_xxAA`, SWD, 1000 kHz, Erase Chip, then Program Device | J-Flash Lite through J9, device `nRF52833_XXAA`, SWD, 4000 kHz, "Compare+Erase" |
| Calibration | None | Loaded through J20 with `python load_cal.py -p COMXX -f calib_files\DWM3001CDK\dual-hoe_non_aoa.json` (the non-AoA preset) |

Notes:

- Qorvo's download page only accepts a company or institution e-mail address.
- How to use each firmware: [`uwb/cli-firmware-guide.md`](uwb/cli-firmware-guide.md) and [`uwb/uci-firmware-guide.md`](uwb/uci-firmware-guide.md). The radio settings both report: [`../config/uwb/radio-and-session-parameters.md`](../config/uwb/radio-and-session-parameters.md).

## Computers

| Host (as in the terminal prompts) | Machine | Software | Role |
|---|---|---|---|
| `jetson1@jetson1-desktop` | NVIDIA Jetson Orin Nano 8 GB developer kit | JetPack 6.2.2, Ubuntu 22.04.5, Python 3.10, ROS 2 Humble; `~/uwb-qorvo-tools`, `~/uwb_venv`, `~/ros2_ws` | UWB tag 1 and the two-tag scheduler; all the LiDAR work |
| `jetson2@jetson2` | Jetson Orin Nano | `~/uwb-qorvo-tools` copied over from Jetson 1, `~/uwb_venv` | UWB tag 2 |
| Third Jetson | Planned, one per robot | | Tag 3 |
| `pi1@pi1`, `pi2@pi2`, `pi3@Pi3` | Raspberry Pi 4 | Pi OS shipping Python 3.13.5; Python 3.10.16 built from source for the Qorvo tools | May: anchors with MAC 0x1, 0x2, 0x3. April: see the table below |
| `pi4@pi4`, `pi5@pi5`, `pi6@pi6` | Raspberry Pi | pyserial scripts, `qorvo-live.service` | April only: anchors 1, 2, 3 |
| Windows 10 PC | | Tera Term 5, J-Flash Lite, the SDK and its Python tools | Flashing, manual CLI tests, and the first UCI anchor (on `COM18`) |

## Which host carried which UWB role

**April, CLI firmware** (addresses are the `-ADDR` values given on the command line):

| Role | Address | Host |
|---|---|---|
| Tag 1 | 11 (`0x000B`) | pi1 |
| Tag 2 | 12 (`0x000C`) | pi2 |
| Anchor 1 | 1 | pi4 |
| Anchor 2 | 2 | pi5 |
| Anchor 3 | 3 | pi6 |
| Anchor 4 | 4 | pi3 |

**May, UCI firmware:**

| Role | Address | Host |
|---|---|---|
| Tag 1 | Default (`0x0`) | Jetson 1 |
| Tag 2 | Default (`0x0`) | Jetson 2 |
| Anchor 1 | `0x1` | pi1 |
| Anchor 2 | `0x2` | pi2 |
| Anchor 3 | `0x3` | pi3 |

The first plan had a single Raspberry Pi as a hub for all three anchors. What was built is one Pi per anchor, each mounted with its board. A fixed mapping of the six physical boards to roles was proposed but not confirmed.

## Sensors

| Sensor | Detail | Status |
|---|---|---|
| SLAMTEC RPLIDAR A2M12 | 360° 2D LiDAR on USB. The driver reports 1800 points per turn, frame `laser`, range 0.15 to 16 m, about 0.085 s per scan | In use on Jetson 1 |
| Intel RealSense D435i | Depth camera | Planned; no use recorded |

## Robot base (planned)

Three mecanum-wheel robots. None has been assembled or driven yet.

| Part | Detail |
|---|---|
| Main computer | Jetson Orin Nano 8 GB, one per robot. No Raspberry Pi on the robots |
| Power | Buck converter from the battery to the Jetson. The battery is not specified |
| Motor driver | Cytron MDDS30 (dual channel, 30 A) |
| Low-level controller | Teensy 4.1 on USB: takes velocity commands from the Jetson, drives the MDDS30, reads encoders |
| Motors | PGM45775 planetary DC motors (10 mm shaft, as described in the parts check) |

Wheel assembly, twelve of each part for three robots with four wheels each:

| # | Part | Purpose |
|---|---|---|
| 1 | RDR jaw flexible coupler, D30 × L40, 10 × 10 mm | Motor shaft to MS shaft |
| 2 | EasyMech 6902 ZZ bearing housing and MS shaft | Chassis mount, carries the load |
| 3 | EasyMech anti-slip coupling, 10 mm (SKU 9210) | MS shaft to wheel |
| 4 | EasyMech universal bracket for PGM45775 | Motor mount |
| 5 | 100 mm mecanum wheels | Drive wheels |

A parts check found the set mechanically compatible, with one reminder: each robot needs two left-hand and two right-hand mecanum wheels.

## USB ports on the Jetson

The Jetson has four USB ports and the plan needs four devices: LiDAR, UWB board, depth camera and the motor controller. Three ways around this were discussed (a powered USB 3.0 hub, moving the UWB board to UART pins, or routing small sensors through the Teensy); none has been chosen yet.
