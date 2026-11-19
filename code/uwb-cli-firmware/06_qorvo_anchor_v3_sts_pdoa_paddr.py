# ----------------------------------------------------------------------------
# UWB_V2X
# Status : Ran and worked: first successful 1:1 ranging (about 1.5 m).
# About  : Anchor with STS on, PDoA off and the tag's address as -PADDR=11.
# ----------------------------------------------------------------------------
import serial, time

def main():
    with serial.Serial('/dev/ttyACM0', 115200, timeout=1) as ser:
        ser.write(b'\r\r')
        time.sleep(0.5)
        ser.write(b'STOP\r')
        time.sleep(1.0)

        # 1. Force STS Mode On
        ser.write(b'LCFG -STSMODE=1\r')
        time.sleep(0.5)

        # 2. Force PDoA Mode Off (To match the Tag)
        ser.write(b'LCFG -PDOAMODE=0\r')
        time.sleep(0.5)

        ser.write(b'SAVE\r')
        time.sleep(0.5)

        # 3. ADD PADDR=11 so the Anchor knows the Tag's address for decryption
        ser.write(b'RESPF -MULTI -ADDR=1 -PADDR=11\r')
        print("Anchor 1 is starting. Waiting for Tag 11...")

        while True:
            line = ser.readline().decode('ascii', errors='ignore')
            if line:
                print(line.strip())

if __name__ == "__main__":
    main()
