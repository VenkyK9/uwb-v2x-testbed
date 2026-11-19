#!/usr/bin/env python3
# ----------------------------------------------------------------------------
# UWB_V2X
# Status : Proposed. No run is recorded; replaced by the short scripts below.
# About  : Revision that sends one character at a time and drops -PADDR on the responder.
# ----------------------------------------------------------------------------
import time, glob, sys, serial

BAUD = 115200
ROLE = "anchor"
ADDR = 1  # Change to 2 on PI5, 3 on PI6, 4 on PI7

def find_port():
    for path in sorted(glob.glob('/dev/ttyACM*')):
        try:
            s = serial.Serial(path, BAUD, timeout=1)
            s.close()
            return path
        except serial.SerialException:
            pass
    return None

def send_slow(ser, text, wait_after=1.0):
    # Sends character by character to prevent dropping (like Tera Term)
    for char in text:
        ser.write(char.encode('ascii'))
        ser.flush()
        time.sleep(0.01) # 10ms delay per char
    time.sleep(wait_after)

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

        # Wake up / clear prompt
        send_slow(ser, '\r\r', 0.5)
        ser.reset_input_buffer()

        # Ensure a clean slate
        print("Stopping previous sessions...", flush=True)
        send_slow(ser, 'STOP\r', 1.0)

        # Formulate the correct command (NO PADDR for Responders)
        cmd = f'RESPF -MULTI -ADDR={ADDR}\r'

        print(f"Sending: {cmd.strip()}", flush=True)
        send_slow(ser, cmd, 1.0)

        while True:
            raw_line = ser.readline()
            if raw_line:
                clean_text = clean_line(raw_line)
                if clean_text.strip():
                    print(clean_text, flush=True)

if __name__ == '__main__':
    main()
