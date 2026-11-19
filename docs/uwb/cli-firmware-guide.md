# CLI firmware guide: the first approach

The CLI firmware (`DWM3001CDK-DW3_QM33_SDK_CLI-FreeRTOS.hex`) gives each board a text console on its J20 USB port at 115200 baud. Ranging is started by typing commands, or by a short Python script that types them. The project used it in April 2026, got one tag ranging with four anchors, and left it when a second tag was needed.

It is still the quickest way to check that two boards can range at all: no Python packages, only a serial terminal. Everything below comes from the project's own logs.

## 1. Opening the console

| Host | Tool | Notes |
|---|---|---|
| Windows | Tera Term 5, 115200 baud | Turn on local echo. A transmit delay of 10 ms per character was advised when characters went missing |
| Raspberry Pi | `python3 -m serial.tools.miniterm /dev/ttyACM0 115200` | Comes with pyserial. Exit with Ctrl+] |
| Raspberry Pi | `sudo minicom -D /dev/ttyACM0 -b 115200` | Needs `sudo apt install minicom` first. Exit with Ctrl+A, Z, X |

Press Enter a few times to wake the console (its prompt is `dwm>`). Only one program can hold the port: stop any script or service using it first (section 7).

## 2. Commands this firmware has

The board's own `HELP` output ([log](../../logs/uwb-cli/02_cli-help-menu.log)):

```text
---       Anytime commands       ---
HELP      ?         STOP      THREAD
STAT
---    Application selection     ---
LISTENER  RESPF     INITF
---      IDLE time commands      ---
UART      CALKEY    LISTCAL
---       Service commands       ---
RESTORE   DIAG      LCFG      DECAID
SAVE      SETAPP    GETOTP
---       LISTENER Options       ---
LSTAT
```

| Command | Use in this project |
|---|---|
| `STOP` | End the running application and return to idle |
| `INITF [options]` | Start as initiator (tag) |
| `RESPF [options]` | Start as responder (anchor) |
| `LCFG` | Print the radio settings. `LCFG -NAME=VALUE` changes one |
| `SAVE` | Store the current settings on the board |
| `RESTORE` | Used to return the stored settings to a clean state before a fresh attempt |
| `SETAPP` | Chooses an application to start at power-up. Not needed for manual tests. The Tera Term logs show the board printing `SETAPP: INVALID APPLICATION` during the first attempts |

There is no `set_addr`, `set_role`, `set_dest_addr`, `set_sts_key`, `set_panid` or `add_controlee`; the early advice that used them was guessed syntax. `LCFG` insists on the form `LCFG -<opt>=VALUE`.

Options of `INITF`, as printed by the board; `RESPF` takes the same style of options:

```text
-CHAN=9       --> Channel number
-PRFSET=BPRF4 --> PRF set
-PCODE=10     --> Preamble code index
-SLOT=2400    --> Slot duration [RSTU]
-BLOCK=200    --> Block duration [ms]
-ROUND=25     --> Round duration [slots]
-RRU=DSTWR    --> Ranging round usage
-ID=42        --> Session ID
-VUPPER=01:02:03:04:05:06:07:08   --> vUpper64
-MULTI        --> Activate one-to-many mode
-HOP          --> Activate round hopping
-ADDR=0       --> Device own address (Initiator address)
-PADDR=1      --> 1st Responder address
   or to set multiple responders:
-PADDR=[1,2,.,.,n]  --> to set n Responder addresses (for one-to-many)
```

## 3. The commands that worked

Start the anchors first, then the tag.

**Each anchor** (address 1 shown; use 2, 3, 4 for the others):

```text
STOP
LCFG -STSMODE=1
LCFG -PDOAMODE=0
SAVE
RESPF -MULTI -ADDR=1 -PADDR=11
```

**The tag** (address 11), one anchor:

```text
STOP
LCFG -STSMODE=1
SAVE
INITF -MULTI -ADDR=11 -PADDR=1
```

**The tag with four anchors**:

```text
INITF -MULTI -ADDR=11 -PADDR=[1,2,3,4]
```

The scripts that send exactly these lines from a Raspberry Pi are [`05_qorvo_tag_v2_sts.py`](../../code/uwb-cli-firmware/05_qorvo_tag_v2_sts.py), [`06_qorvo_anchor_v3_sts_pdoa_paddr.py`](../../code/uwb-cli-firmware/06_qorvo_anchor_v3_sts_pdoa_paddr.py) and [`07_qorvo_anchor2_addr2.py`](../../code/uwb-cli-firmware/07_qorvo_anchor2_addr2.py). They open `/dev/ttyACM0`, send two carriage returns, then each command with a short pause, and print whatever the board returns.

## 4. What the output looks like

After `INITF` or `RESPF` the board prints its session parameters, then status changes, then one line per ranging round:

```text
SESSION_STATUS_NTF: {state="ACTIVE", reason="State change with session management commands"}
SESSION_INFO_NTF: {session_handle=1, sequence_number=351, block_index=351, n_measurements=4
 [mac_address=0x0001, status="SUCCESS", distance[cm]=146];
 [mac_address=0x0002, status="SUCCESS", distance[cm]=233];
 [mac_address=0x0003, status="SUCCESS", distance[cm]=330];
 [mac_address=0x0004, status="SUCCESS", distance[cm]=222]}
```

| Status | Meaning in these tests |
|---|---|
| `SUCCESS` | Distance measured |
| `RX_TIMEOUT` | The tag heard no reply. Seen whenever the anchors rejected or never received its frames |
| `RX_MAC_IE_DEC_FAILED` | The anchor received a frame it could not accept. Seen while the anchor did not have the tag's address or the settings differed |

Check the parameter block before anything else: `DEVICE_MAC_ADDRESS` and `DST_MAC_ADDRESS` show whether the addresses were taken. The full parameter list is in [`config/uwb/radio-and-session-parameters.md`](../../config/uwb/radio-and-session-parameters.md).

## 5. Rules learned the hard way

| Rule | What happens otherwise |
|---|---|
| The address is an option of `INITF` / `RESPF`, not an `LCFG` setting | `Unknown argument: ADDR=0X0001` |
| `-ADDR` only takes effect together with `-MULTI` | The dump still shows `DEVICE_MAC_ADDRESS: 0x0000` and `MULTI_NODE_MODE: UNICAST` |
| STS must be on: `LCFG -STSMODE=1`, then `SAVE` | `error incompatible mode` when starting, red LED D13 blinking |
| Every anchor needs the tag's address: `-PADDR=11` | Anchor logs `RX_MAC_IE_DEC_FAILED`, tag logs `RX_TIMEOUT` |
| `PDOAMODE` must be the same on both ends (0 here) | Same symptoms as above |
| A list of addresses needs square brackets: `-PADDR=[1,2,3,4]` | Only the first address is used; the dump shows `DST_MAC_ADDRESS[0]` alone |
| Start anchors before tags | The tag's first rounds time out |
| One board runs one session | A second `RESPF` or `INITF` is refused with `error incompatible mode` |

## 6. Why it stopped here

The goal was two tags (later three), each measuring its distance to every anchor. On this firmware a board runs a single ranging session. A manual test on a tag and on an anchor showed that a second session with its own ID is refused ([tag log](../../logs/uwb-cli/13_stacking-test_tag-1.log), [anchor log](../../logs/uwb-cli/14_stacking-test_anchor-1.log)).

Two things did work, or might have:

- **Roles the other way round.** One test had anchor 1 as initiator ranging with both tags as responders (273 and 315 cm). One anchor can therefore see two tags, but each tag then has a single distance, which is not enough for a position.
- **Taking turns.** Anchors that switch between tag 11 and tag 12 every 2.5 seconds were drafted ([`19_timeslice_tag.py`](../../code/uwb-cli-firmware/19_timeslice_tag.py), [`20_timeslice_anchor.py`](../../code/uwb-cli-firmware/20_timeslice_anchor.py)) but never run: the project moved to UCI firmware first.

The decision was to move every board to the UCI firmware. The same turn-taking idea, done on the tags instead of the anchors, is what solved the problem there: see [`uci-firmware-guide.md`](uci-firmware-guide.md).

## 7. When a board will not listen

Problems met with anchor 2 on pi5, and what was tried ([log](../../logs/uwb-cli/12_anchor-2_miniterm_and_rescue-attempts.log)):

1. **Free the serial port.** A leftover `qorvo-live.service` restarted its script every time it was killed and held the port. Stopping it was necessary but did not clear the error by itself; the board had also moved to another port number:

   ```bash
   sudo systemctl stop qorvo-live.service
   sudo systemctl disable qorvo-live.service
   sudo pkill -9 -f python
   ```

2. **Reset the stored settings by hand** in miniterm: `STOP`, `RESTORE`, `SAVE`. On this board `STOP` answered `ok`, but `RESTORE` and `SAVE` came back with `error incompatible mode`.
3. **Rescue scripts** that send `STOP` the moment the board boots: [`09`](../../code/uwb-cli-firmware/09_qorvo_rescue_v1_reset-button.py), [`10`](../../code/uwb-cli-firmware/10_qorvo_rescue_v2_autodetect-port.py), [`11`](../../code/uwb-cli-firmware/11_qorvo_rescue_v3_wait-for-usb.py). None brought the board back.
4. **Erase and reflash**: cable on **J9**, SEGGER J-Flash Lite, device `nRF52833_xxAA`, interface SWD, speed 1000 kHz, **Erase Chip**, then program the CLI `.hex` and move the cable back to **J20**. After that the board accepted commands again. An earlier lock-up after a `SETAPP` command had already needed the same full erase and reflash.

The firmware comes from Qorvo's SDK download, which needs a company or institution e-mail address.

## 8. Related files

- All CLI scripts with their status: [`code/`](../../code/README.md)
- CLI logs: [`logs/`](../../logs/README.md)
