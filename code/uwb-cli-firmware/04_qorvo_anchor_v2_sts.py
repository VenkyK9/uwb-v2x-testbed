# ----------------------------------------------------------------------------
# UWB_V2X
# Status : Ran. Same failure as v1 (the anchor still had no peer address).
# About  : Anchor with LCFG -STSMODE=1 and SAVE before RESPF.
# ----------------------------------------------------------------------------
import serial, time

def main():
    with serial.Serial('/dev/ttyACM0', 115200, timeout=1) as ser:
        ser.write(b'\r\r')
        time.sleep(0.5)
        ser.write(b'STOP\r')
        time.sleep(1.0)
        # FORCE STS MODE 1 (This fixes the DEC_FAILED error)
        ser.write(b'LCFG -STSMODE=1\r')
        time.sleep(0.5)
        ser.write(b'SAVE\r')
        time.sleep(0.5)
        # Start the Anchor
        ser.write(b'RESPF -MULTI -ADDR=1\r')
        print("Anchor 1 is now starting with STS Enabled...")
        while True:
            line = ser.readline().decode('ascii', errors='ignore')
            if line:
                print(line.strip())

if __name__ == "__main__":
    main()
