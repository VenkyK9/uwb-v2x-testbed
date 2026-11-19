# ----------------------------------------------------------------------------
# UWB_V2X
# Status : Ran. Worked once the tag's list was written as -PADDR=[1,2,3,4] (1 tag with 4 anchors).
# About  : The same anchor script for anchor 2 (ADDR=2); anchors 3 and 4 differ only in ADDR.
# ----------------------------------------------------------------------------
import serial, time

def main():
    with serial.Serial('/dev/ttyACM0', 115200, timeout=1) as ser:
        ser.write(b'\r\r')
        time.sleep(0.5)
        ser.write(b'STOP\r')
        time.sleep(1.0)
        ser.write(b'LCFG -STSMODE=1\r')
        time.sleep(0.5)
        ser.write(b'LCFG -PDOAMODE=0\r')
        time.sleep(0.5)
        ser.write(b'SAVE\r')
        time.sleep(0.5)

        # NOTE: ADDR is 2 for Anchor 2
        ser.write(b'RESPF -MULTI -ADDR=2 -PADDR=11\r')
        print("Anchor 2 is starting. Waiting for Tag 11...")

        while True:
            line = ser.readline().decode('ascii', errors='ignore')
            if line:
                print(line.strip())

if __name__ == "__main__":
    main()
