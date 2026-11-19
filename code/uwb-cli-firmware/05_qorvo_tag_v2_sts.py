# ----------------------------------------------------------------------------
# UWB_V2X
# Status : Ran. This is the tag side of the first successful 1:1 ranging (with anchor v3).
# About  : Tag with LCFG -STSMODE=1 and SAVE before INITF.
# ----------------------------------------------------------------------------
import serial, time

def main():
    with serial.Serial('/dev/ttyACM0', 115200, timeout=1) as ser:
        ser.write(b'\r\r')
        time.sleep(0.5)
        ser.write(b'STOP\r')
        time.sleep(1.0)
        # FORCE STS MODE 1 (Must match Anchor)
        ser.write(b'LCFG -STSMODE=1\r')
        time.sleep(0.5)
        ser.write(b'SAVE\r')
        time.sleep(0.5)
        # Start the Tag and look for Anchor 1
        ser.write(b'INITF -MULTI -ADDR=11 -PADDR=1\r')
        print("Tag 1 is now starting with STS Enabled...")
        while True:
            line = ser.readline().decode('ascii', errors='ignore')
            if line:
                print(line.strip())

if __name__ == "__main__":
    main()
