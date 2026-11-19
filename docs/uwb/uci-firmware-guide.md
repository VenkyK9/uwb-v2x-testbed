# UCI firmware guide: the working setup

How to repeat the configuration that worked at the end of the project (on or after 28 May 2026): two tags on Jetson Orin Nanos, three anchors on Raspberry Pis, all six boards on Qorvo's UCI firmware.

This guide is assembled from the commands in the project's logs. Treat it as a summary of what worked, not as a tested installer.

## 1. What is involved

| Piece | Where it runs | Notes |
|---|---|---|
| UCI firmware `DWM3001CDK-DW3_QM33_SDK_UCI-FreeRTOS.hex` | All six DWM3001CDK boards | Reports uci / mac / phy version 2.0.0 |
| `uwb-qorvo-tools` (from `DW3_QM33_SDK_1.1.1`, folder `SDK\Tools`) | Copied to `~/uwb-qorvo-tools` on every host | Needs Python 3.9 or 3.10 |
| Python virtual environment | `~/uwb_venv` on every host | Holds `uwb-uci`, `uqt-utils`, `pyserial`, `colorama` |
| [`demo_runner.sh`](../../code/uwb-uci/demo_runner.sh) | `~/uwb-qorvo-tools/` on Jetson 1 | Makes the two tags take turns |

Hosts and roles are listed in [`../hardware.md`](../hardware.md).

## 2. Flash and calibrate the boards (once per board)

Done once per board from a Windows PC:

1. Connect the board's **J9** connector (J-Link) to the PC.
2. In SEGGER J-Flash Lite choose device `nRF52833_XXAA`, interface SWD, speed 4000 kHz, and program `DWM3001CDK-DW3_QM33_SDK_UCI-FreeRTOS.hex` from `SDK\Binaries\DWM3001CDK`.
3. Move the cable to **J20**. From the tools folder on the PC, load the calibration:

   ```powershell
   python load_cal.py -p COMXX -f calib_files\DWM3001CDK\dual-hoe_non_aoa.json
   ```

`dual-hoe_non_aoa.json` is the preset without angle of arrival, which matches this single-antenna board.

## 3. Prepare a Jetson (tag host)

Jetson 1 runs JetPack 6.2.2 (Ubuntu 22.04, Python 3.10), so the system Python fits the tools.

```bash
sudo apt install python3.10-venv python3-pip python3-dev -y
python3 -m venv ~/uwb_venv --system-site-packages
source ~/uwb_venv/bin/activate
```

Copy the tools folder from the PC that has the SDK. On Windows 10 this worked from Command Prompt, not PowerShell:

```bat
scp -r "D:\V2X\DW3_QM33_SDK_1.1.1\SDK\Tools\uwb-qorvo-tools" jetson1@<JETSON_IP>:~/
```

Install only the libraries needed for ranging:

```bash
cd ~/uwb-qorvo-tools
pip install pyserial pyqtgraph colorama toml
pip install ./lib/uwb-uci
pip install ./lib/uqt-utils
python3 -c "import uci; print('UCI import OK')"
```

Do not run `pip install -e .` here. It stops on `PySide2==5.15.2.1`, which has no build for these ARM boards and is only needed for the plotting tools. The price is that the short command `run_fira_twr` is not registered, so the scripts are called by path, as in every command below.

Jetson 2 received the same folder from Jetson 1 with `scp -r ~/uwb-qorvo-tools <user>@<jetson2-ip>:~/` and then needs the same venv and library steps.

If `apt` refuses to work because of a half-added ROS 2 repository (`Conflicting values set for option Signed-By`), remove `/etc/apt/sources.list.d/ros2.list` first.

## 4. Prepare a Raspberry Pi (anchor host)

The Pis printed `Python 3.13.5`, which the Qorvo library rejects (`requires a different Python: 3.13.5 not in '<3.11.0,>=3.9'`). Python 3.10 was built from source and the venv created with that interpreter explicitly:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y build-essential libssl-dev zlib1g-dev \
  libncurses5-dev libnss3-dev libreadline-dev libffi-dev \
  libsqlite3-dev wget libbz2-dev libexpat1-dev liblzma-dev \
  python3-pip curl

cd /tmp
wget https://www.python.org/ftp/python/3.10.16/Python-3.10.16.tgz
tar -xf Python-3.10.16.tgz
cd Python-3.10.16
./configure --enable-optimizations
make -j4                 # about 12 minutes on a Pi 4
sudo make altinstall
/usr/local/bin/python3.10 --version      # must print Python 3.10.16
```

Copy the tools from Jetson 1 (`scp -r ~/uwb-qorvo-tools pi1@<PI1_IP>:~/`), then:

```bash
/usr/local/bin/python3.10 -m venv ~/uwb_venv --without-pip
source ~/uwb_venv/bin/activate
python3 --version                        # must print 3.10.16
curl https://bootstrap.pypa.io/get-pip.py -o /tmp/get-pip.py
python3 /tmp/get-pip.py

cd ~/uwb-qorvo-tools
pip install ./lib/uwb-uci
pip install ./lib/uqt-utils
pip install pyserial colorama
python3 -c "import uci; print('UCI import OK')"
```

Two traps met on the way: running `make` before `./configure`, and a venv whose `python3` still pointed at `/usr/bin/python3` (3.13). `ls -la ~/uwb_venv/bin/python3` shows which interpreter a venv uses.

## 5. Serial port access

The board appears as `/dev/ttyACM0` (or a higher number). A normal user cannot open it until one of these is done:

```bash
sudo chmod 666 /dev/ttyACM0                 # immediate, lost when the board is replugged
sudo usermod -a -G dialout $USER            # permanent, needs a new login
```

A udev rule that does this for every board is kept in [`config/udev/99-uwb.rules`](../../config/udev/99-uwb.rules). It was not confirmed as installed on the Jetsons; `chmod` is what the logs show being used.

## 6. Check that a board answers

```bash
cd ~/uwb-qorvo-tools
source ~/uwb_venv/bin/activate
ls /dev/ttyACM*
python3 scripts/device/get_device_info/get_device_info.py -p /dev/ttyACM0
```

A healthy board prints `status: Ok (0x0)`, `uci version: 2.0.0` and `device id: deca0302` ([log](../../logs/uwb-uci/04_jetson-1_get-device-info_ok.log)). `lsusb | grep -i nordic` shows whether the board is on the bus at all.

## 7. One tag and three anchors

Always start the anchors first.

On each Raspberry Pi, with its own address (`0x1`, `0x2`, `0x3`):

```bash
cd ~/uwb-qorvo-tools
source ~/uwb_venv/bin/activate
python3 scripts/fira/run_fira_twr/run_fira_twr.py -p $(ls /dev/ttyACM* | head -n 1) -t -1 --node onetomany --mac 0x1 --controlee
```

Wait about five seconds, then on the Jetson:

```bash
cd ~/uwb-qorvo-tools
source ~/uwb_venv/bin/activate
export UQT_PORT=/dev/ttyACM0
python3 scripts/fira/run_fira_twr/run_fira_twr.py -t -1 --node onetomany --dest-mac '[0x1,0x2,0x3]' --n_controlees 3
```

What the options mean:

| Option | Meaning |
|---|---|
| `-p PORT` or `UQT_PORT` | Serial port of the board |
| `-t -1` | Run until Enter is pressed. `-t 3` runs for three seconds and closes the session cleanly |
| `--node onetomany` | One controller ranging with several controlees |
| `--controlee` | This board answers (anchor). Without it the board is the controller and initiator (tag) |
| `--mac 0x1` | This board's own short address |
| `--dest-mac '[0x1,0x2,0x3]'`, `--n_controlees 3` | The anchors the tag ranges with |

`run_fira_twr.py -h` prints the full option list; the usage text also appears in [`logs/uwb-uci/20_demo_attempt-1_session-id-rejected.log`](../../logs/uwb-uci/20_demo_attempt-1_session-id-rejected.log). Result on the day: about 343, 436 and 466 cm to the three anchors (the log was not kept). Anchor output from a later one-tag run is in [`logs/uwb-uci/08_anchors_ranging-ok_one-tag.log`](../../logs/uwb-uci/08_anchors_ranging-ok_one-tag.log).

## 8. Two tags: the scheduler

Two tags started together do not both work: the second one gets `RangingRxTimeout (0x21)` on every measurement ([log](../../logs/uwb-uci/10_two-tags_jetson-2-all-timeouts.log)). The working answer is to let them take turns.

One-time setup on Jetson 1:

```bash
ssh-keygen -t rsa                      # accept the defaults
ssh-copy-id jetson2@<JETSON2_IP>       # asks for Jetson 2's password once
```

Save [`demo_runner.sh`](../../code/uwb-uci/demo_runner.sh) as `~/uwb-qorvo-tools/demo_runner.sh` on Jetson 1, put Jetson 2's user and address in `JETSON2_USER_IP`, and make it executable with `chmod +x ~/uwb-qorvo-tools/demo_runner.sh`.

Each run:

1. Start from a clean state: unplug all five UWB boards for ten seconds and plug them back in.
2. Start the three anchors as in section 7.
3. Wait about five seconds.
4. On Jetson 1: `~/uwb-qorvo-tools/demo_runner.sh`
5. Stop with **Ctrl+C** on Jetson 1, and stop each anchor with **Enter**, which closes its session cleanly.

For a quieter screen:

```bash
~/uwb-qorvo-tools/demo_runner.sh | grep --line-buffered -i "distance\|cm\|mac\|session\|initiating"
```

Why the script looks the way it does:

| Line in the script | Reason |
|---|---|
| `-t 3` | A bounded run ends with `Stopping ranging... Deinitializing session... Ok`, so the board accepts the next session without being unplugged |
| No `--mac`, no `-s` on the tags | With `--mac 0x4` / `0x5` and sessions 1 / 2 the anchors answered every frame with `RangingRxMacIeDecFailed (0x26)` |
| `ssh -T` with a heredoc | Without `-T`, SSH printed `Pseudo-terminal will not be allocated because stdin is not a terminal.` and Jetson 2's turn got no further than `Initializing session 42...` before the run was stopped. The likely cause was terminal allocation over SSH. With `-T`, both tags ranged |
| `J1_PORT=$(ls /dev/ttyACM* \| head -n 1)` | After every session the board comes back under the next `/dev/ttyACM` number |
| `sleep 1` between turns | Gap between the two tags. The anchors log `RangingRxTimeout` during it, which is expected |

Result: both Jetsons report `Ok (0x0)` with distances to all three anchors. The log of the run just before the port fix shows it most plainly: seven rounds on Jetson 1, then the first round on Jetson 2, each with anchors `00:01`, `00:02` and `00:03` answering ([log](../../logs/uwb-uci/24_demo_both-tags-ok_then-unknown-port.log)). The final run worked ([log](../../logs/uwb-uci/26_demo_FINAL_SUCCESS.log)). The six earlier versions of the script, each with the reason it was replaced, are in [`code/uwb-uci/history/`](../../code/README.md).

## 9. Reading the output

Each ranging round prints one block per anchor:

```text
# Measurement 3:
    status:             Ok (0x0)
    mac address:        00:03 hex
    is nlos meas:       Unsupported
    distance:           307.0 cm
    AoA azimuth:        0.0 deg
    ...
    slot in error:      0
    rssi:               -0.0 dBm
```

| Field or value | Meaning |
|---|---|
| `status: Ok (0x0)` | Valid measurement |
| `distance: 65535.0 cm` | No measurement (the largest 16-bit value) |
| `RangingRxTimeout (0x21)` | Nothing heard in that slot |
| `RangingRxPhyDecFailed (0x22)` | A frame arrived but could not be decoded. One of these in a long run is nothing to act on |
| `RangingRxMacIeDecFailed (0x26)` | The anchor received a frame and rejected it. Seen on every frame while the tags were given their own MAC and session number |
| `mac address` | The other end of the measurement. On an anchor this reads `00:00` for both tags |
| AoA fields, `is nlos meas` | Always zero or "Unsupported" on this board: one antenna |
| `UciComError.TimeoutError (0x3)` | The board is not answering the host. Unplug it for ten seconds |
| `UciComError.UnknownPort (0x1)` | No board at that port name. Check `ls /dev/ttyACM*` |

The complete list of errors is in [`../errors-and-fixes.md`](../errors-and-fixes.md).

## 10. Known limits

- **A stopped board may need unplugging.** If a ranging script is interrupted before it closes its session, the board can stop answering (`TimeoutError (0x3)`) until it is unplugged for about ten seconds. Bounded runs (`-t 3`) avoid this for the tags. The anchors still run with `-t -1`.
- **Stop with Enter or Ctrl+C, never Ctrl+Z.** Enter is the clean stop for a `-t -1` run. Ctrl+Z only suspends the program, which keeps the serial port and leaves the session open. See "Patterns worth remembering" in [`../errors-and-fixes.md`](../errors-and-fixes.md#patterns-worth-remembering).
- **Tags are not ranging all the time.** Each tag ranges for three seconds, then waits while the other has its turn.
- **Both tags use address `0x0` and session 42.** A tag knows which anchor each distance belongs to, but an anchor cannot tell the tags apart except by whose turn it is.
- **Port detection takes the first `/dev/ttyACM*`.** Keep other USB serial devices off the Jetsons while the scheduler runs.
- **No positions yet.** The output is three distances per tag. Turning them into (x, y), publishing in ROS 2 and adding the third tag are listed in [`../next-steps.md`](../next-steps.md).

Ideas that were discussed for the unplugging problem and not adopted: a USB hub with per-port power switching (`uhubctl`), a community firmware build, and wrapper scripts that restart the tool ([`code/uwb-uci/restart-wrappers/`](../../code/README.md)). The wrappers restart the program only; they cannot revive a board that has stopped answering.

## 11. Related files

- Session parameters as printed by the tag: [`config/uwb/radio-and-session-parameters.md`](../../config/uwb/radio-and-session-parameters.md)
- All UCI logs: [`logs/`](../../logs/README.md)
