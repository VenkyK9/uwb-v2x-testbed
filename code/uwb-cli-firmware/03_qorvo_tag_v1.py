# ----------------------------------------------------------------------------
# UWB_V2X
# Status : Ran. Tag logged RX_TIMEOUT.
# About  : Minimal tag: LCFG -STSMODE=1, then INITF -MULTI -ADDR=11 -PADDR=1.
# ----------------------------------------------------------------------------
import serial, time

def main():
    # 1. Open the connection to the Qorvo board
    with serial.Serial('/dev/ttyACM0', 115200, timeout=1) as ser:
        # 2. Wake up the board
        ser.write(b'\r\r')
        time.sleep(0.5)
        # 3. Stop any old sessions and clear memory
        ser.write(b'STOP\r')
        time.sleep(1.0)
        # 4. Enable STS Security (To fix the DEC_FAILED error)
        ser.write(b'LCFG -STSMODE=1\r')
        time.sleep(0.5)
        # 5. Start the Tag (Address 11) and point to Anchor 1
        ser.write(b'INITF -MULTI -ADDR=11 -PADDR=1\r')
        print("Tag 1 is now initiating ranging with Anchor 1...")

        # 6. Print the results
        while True:
            line = ser.readline().decode('ascii', errors='ignore')
            if line:
                print(line.strip())

if __name__ == "__main__":
    main()
