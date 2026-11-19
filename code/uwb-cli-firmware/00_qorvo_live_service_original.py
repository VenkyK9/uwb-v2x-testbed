#!/usr/bin/env python3
# ----------------------------------------------------------------------------
# UWB_V2X
# Status : Superseded. Sends 'respf -multi -addr=N -paddr=[11,12]'. It came under suspicion because anchor 1 reported address 0x0000 instead of 0x0001.
# About  : The first anchor script, run on each Pi by qorvo-live.service.
# ----------------------------------------------------------------------------
import time, glob, sys, serial

BAUD = 115200
ROLE = "anchor"
ADDR = 1  # REMEMBER TO CHANGE THIS TO 2 ON PI5 AND 3 ON PI6!
PEERS = [11, 12]  # These are the Tag addresses!

def find_port():
    for path in sorted(glob.glob('/dev/ttyACM*')):
        try:
            s = serial.Serial(path, BAUD, timeout=1)
            s.close()
            return path
        except serial.SerialException:
            pass
    return None

def send(ser, text, wait=0.5):
    ser.write(text.encode('ascii'))
    ser.flush()
    time.sleep(wait)

def clean_line(raw_bytes):
    return ''.join(chr(b) for b in raw_bytes if 32 <= b <= 126 or b == 9)

def main():
    port = None
    for _ in range(30):
        port = find_port()
        if port:
            break
        time.sleep(1)
    if not port:
        print("Error: Qorvo board not found.", flush=True)
        sys.exit(1)

    print(f"Anchor {ADDR} found board on {port}", flush=True)
    with serial.Serial(port, BAUD, timeout=1) as ser:
        time.sleep(2)
        send(ser, '\r\r', 0.3)
        ser.reset_input_buffer()
        send(ser, 'STOP\r\n', 0.5)

        # Add paddr to the anchor command so it accepts the tags!
        peers_str = str(PEERS).replace(' ', '')
        cmd = f'respf -multi -addr={ADDR} -paddr={peers_str}\r\n'

        print(f"Sending: {cmd.strip()}", flush=True)
        send(ser, cmd, 1.0)

        while True:
            raw_line = ser.readline()
            if raw_line:
                clean_text = clean_line(raw_line)
                if clean_text.strip():
                    print(clean_text, flush=True)

if __name__ == '__main__':
    main()
