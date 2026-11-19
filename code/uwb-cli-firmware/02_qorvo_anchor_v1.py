# ----------------------------------------------------------------------------
# UWB_V2X
# Status : Ran. Anchor showed address 0x0001 but logged RX_MAC_IE_DEC_FAILED.
# About  : Minimal anchor: STOP, then RESPF -MULTI -ADDR=1.
# ----------------------------------------------------------------------------
import serial, time

def main():
    # 1. Open the connection to the Qorvo board
    with serial.Serial('/dev/ttyACM0', 115200, timeout=1) as ser:
        # 2. Wake it up
        ser.write(b'\r\r')
        time.sleep(0.5)
        # 3. Stop any old sessions
        ser.write(b'STOP\r')
        time.sleep(1.0)
        # 4. Set the Anchor ID to 1 and start
        ser.write(b'RESPF -MULTI -ADDR=1\r')
        print("Anchor 1 is now starting...")

        # 5. Listen for data forever
        while True:
            line = ser.readline().decode('ascii', errors='ignore')
            if line:
                print(line.strip())

if __name__ == "__main__":
    main()
