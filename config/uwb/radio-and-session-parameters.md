# UWB radio and session parameters

The settings the boards reported about themselves, collected in one place so the configuration can be compared or reproduced.

There is no UWB configuration file in this project. Every board ran with the SDK defaults, plus the few options given on the command line. The "Notes" columns below add plain-language readings of the values; where a reading comes from general FiRa definitions rather than from the boards' own output, it is marked *(reading)*.

## In one sentence

Both firmwares ran the same profile: channel 9, preamble code 10, SP3 frames with a static STS, double-sided two-way ranging in deferred mode, 2400 RSTU slots, 25 slots per round, one round every 200 ms, session ID 42.

## What the project changed from the defaults

| Firmware | Change | Why |
|---|---|---|
| CLI | `LCFG -STSMODE=1` (default 0) | Without it `INITF` / `RESPF` return `error incompatible mode` |
| CLI | `LCFG -PDOAMODE=0` on the anchors (default 1) | Must match the tag |
| CLI | `-MULTI`, `-ADDR`, `-PADDR` on every `INITF` / `RESPF` | One-to-many mode and addresses |
| UCI | `--node onetomany`; `--mac 0x1` / `0x2` / `0x3` and `--controlee` on the anchors; `--dest-mac '[0x1,0x2,0x3]' --n_controlees 3` on the tags | One-to-many mode and addresses |
| UCI | `-t 3` on the tags | Bounded run that closes its session |

The tags on UCI firmware keep the default address (`0x0`) and the default session (42). Giving them `--mac 0x4` / `0x5` and `-s 1` / `2` broke ranging.

## CLI firmware: radio settings (`LCFG`)

As printed by a board with default settings and by tag 1 and anchor 1 after the changes:

| Parameter | Default | In the working setup | Notes |
|---|---|---|---|
| `CHAN` | 9 | 9 | UWB channel |
| `PAC` | 8 | 8 | |
| `PCODE` | 10 | 10 | Preamble code |
| `SFDTYPE` | 3 | 3 | |
| `DRATE` | 6810 | 6810 | Data rate in kbit/s |
| `PHRMODE` | 0 | 0 | |
| `PHRRATE` | 0 | 0 | |
| `STSMODE` | 0 | **1** | Changed by the project |
| `STSLEN` | 64 | 64 | |
| `PDOAMODE` | 1 | **0** | Changed by the project |
| `XTALTRIM` | 46 | 46 | As printed on the boards dumped |

## CLI firmware: session parameters

Printed after `INITF` / `RESPF`, by tag 1 and by anchor 1 in the run where the anchors had been given the tag's address.

| Parameter | Tag 1 | Anchor 1 | Notes |
|---|---|---|---|
| `SESSION_ID` | 42 | 42 | Default; `-ID` changes it |
| `CHANNEL_NUMBER` | 9 | 9 | |
| `DEVICE_ROLE` | INITIATOR | RESPONDER | |
| `RANGING_ROUND_USAGE` | DS_TWR_DEFERRED | DS_TWR_DEFERRED | Double-sided two-way ranging |
| `SLOT_DURATION [rstu]` | 2400 | 2400 | 2 ms *(reading: 1200 RSTU = 1 ms)* |
| `RANGING_DURATION [ms]` | 200 | 200 | One ranging block every 200 ms, so five rounds a second |
| `SLOTS_PER_RR` | 25 | 25 | 25 slots of 2 ms: a round takes up to 50 ms of each block *(reading)* |
| `MULTI_NODE_MODE` | ONE_TO_MANY | ONE_TO_MANY | `UNICAST` without `-MULTI` |
| `HOPPING_MODE` | Disabled | Disabled | |
| `RFRAME_CONFIG` | SP3 | SP3 | Frame type that carries an STS |
| `SFD_ID` | 2 | 2 | |
| `PREAMBLE_CODE_INDEX` | 10 | 10 | |
| `STATIC_STS_IV` | "01:02:03:04:05:06" | "01:02:03:04:05:06" | SDK default value |
| `VENDOR_ID` | "07:08" | "07:08" | SDK default value |
| `DEVICE_MAC_ADDRESS` | 0x000B | 0x0001 | From `-ADDR` (11 and 1) |
| `DST_MAC_ADDRESS` | `[0]: 0x0001` (up to `[3]: 0x0004` with four anchors) | 0x000B | From `-PADDR` |

## UCI firmware: session parameters

Printed by `run_fira_twr.py` on a tag when it configures its session (also in [`logs/uwb-uci/24_demo_both-tags-ok_then-unknown-port.log`](../../logs/uwb-uci/24_demo_both-tags-ok_then-unknown-port.log)). The session is announced as `Initializing session 42...`.

| Parameter (UCI tag) | Value | Notes |
|---|---|---|
| `DeviceType (0x0)` | 0x1 | Controller *(reading)* |
| `DeviceRole (0x11)` | 0x1 | Initiator *(reading)* |
| `MultiNodeMode (0x3)` | 0x1 | One-to-many *(reading)* |
| `RangingRoundUsage (0x1)` | 0x2 | DS-TWR, deferred *(reading; the CLI dump prints it in words)* |
| `DeviceMacAddress (0x6)` | 0x0 | Default. Both tags use it |
| `ChannelNumber (0x4)` | 0x9 | Channel 9 |
| `ScheduleMode (0x22)` | 0x1 | Time-scheduled *(reading)* |
| `StsConfig (0x2)` | 0x0 | Static STS *(reading)* |
| `RframeConfig (0x12)` | 0x3 | SP3 *(reading; matches the CLI dump)* |
| `ResultReportConfig (0x2e)` | 0xb | |
| `VendorId (0x27)` | 0x708 | The CLI dump shows the same as "07:08" |
| `StaticStsIv (0x28)` | 0x60504030201 | The CLI dump shows the same as "01:02:03:04:05:06" |
| `AoaResultReq (0xd)` | 0x1 | Angle results are requested; this board returns zeros (one antenna) |
| `UwbInitiationTime (0x2b)` | 0x0 | |
| `PreambleCodeIndex (0x14)` | 0xa | 10 |
| `SfdId (0x15)` | 0x2 | |
| `SlotDuration (0x8)` | 0x960 | 2400 RSTU |
| `RangingInterval (0x9)` | 0xc8 | 200 ms |
| `SlotsPerRr (0x1b)` | 0x19 | 25 |
| `MaxNumberOfMeasurements (0x32)` | 0x0 | No limit: runs until stopped *(reading)* |
| `HoppingMode (0x2c)` | 0x0 | Disabled |
| `RssiReporting (0x13)` | 0x0 | Off, which is why `rssi` prints as `-0.0 dBm` *(reading)* |
| `BlockStrideLength (0x2d)` | 0x0 | |
| `NumberOfControlees (0x5)` | 0x3 | From `--n_controlees 3` |
| `DstMacAddress (0x7)` | [1, 2, 3] | From `--dest-mac` |
| `KeyRotationRate (0x24)` | 0x0 | |
| `StsLength (0x35)` | 0x1 | 64 symbols *(reading; the CLI dump shows `STSLEN` 64)* |

No anchor-side dump of these parameters was saved. The anchors were started with `--mac 0x1`, `0x2`, `0x3` and `--controlee`, and report the device they range with as `mac address: 00:00`.

## Options the Qorvo tool offers and the project did not use

`run_fira_twr.py` can also set the channel (`-c`), the session (`-s`), round type (`--round`), STS type and length (`--sts`, `--sts-length`), slot and ranging spans, slots per round, hopping, RSSI reporting (`--en-rssi`) and more. The full usage text is in [`logs/uwb-uci/20_demo_attempt-1_session-id-rejected.log`](../../logs/uwb-uci/20_demo_attempt-1_session-id-rejected.log).

## Firmware identity

`get_device_info.py` on the tag boards:

| Field | Value |
|---|---|
| uci version, mac version, phy version | 2.0.0 |
| uci test version | 1.1.0 |
| QMF version | 1.1.0 |
| OEM version | 0.0.0 |
| device id | deca0302 |

## Calibration

Each board was loaded once with the SDK's `calib_files\DWM3001CDK\dual-hoe_non_aoa.json` using `load_cal.py`. The file itself is part of Qorvo's SDK and is not in this repository.
