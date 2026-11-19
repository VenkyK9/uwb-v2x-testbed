# ----------------------------------------------------------------------------
# UWB_V2X
# Status : Proposed for the second robot. No successful two-tag run on CLI firmware is recorded.
# About  : Tag 2 (ADDR=12) polling anchors [1,2,3,4].
# ----------------------------------------------------------------------------
import serial, time

def main():
    with serial.Serial('/dev/ttyACM0', 115200, timeout=1) as ser:
        ser.write(b'\r\r')
        time.sleep(0.5)
        ser.write(b'STOP\r')
        time.sleep(1.0)

        # FORCE STS MODE 1
        ser.write(b'LCFG -STSMODE=1\r')
        time.sleep(0.5)

        # FORCE PDoA MODE 0
        ser.write(b'LCFG -PDOAMODE=0\r')
        time.sleep(0.5)

        ser.write(b'SAVE\r')
        time.sleep(0.5)

        # Start Tag 2 and look for all 4 Anchors
        ser.write(b'INITF -MULTI -ADDR=12 -PADDR=[1,2,3,4]\r')
        print("Tag 2 (Bot 2) is now starting with STS Enabled...")

        while True:
            line = ser.readline().decode('ascii', errors='ignore')
            if line:
                print(line.strip())

if __name__ == "__main__":
    main()
