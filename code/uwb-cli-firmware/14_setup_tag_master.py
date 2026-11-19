# ----------------------------------------------------------------------------
# UWB_V2X
# Status : Proposed once the correct firmware was reported installed. No run is recorded.
# About  : One tag script for both robots: set TAG_ID, peers are anchors [1,2,3,4].
# ----------------------------------------------------------------------------
import serial, time

# === CONFIGURATION ===
# CHANGE THIS NUMBER FOR EACH BOT! (Use 11 for Bot 1, 12 for Bot 2)
TAG_ID = 11
# =====================

def main():
    print(f"Initializing Tag {TAG_ID} on Mecanum Bot...")

    try:
        ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
    except:
        print("Error: Could not open /dev/ttyACM0. Is the board plugged in?")
        return

    with ser:
        ser.write(b'\r\r')
        ser.flush()
        time.sleep(0.3)

        ser.reset_input_buffer()

        ser.write(b'STOP\r\n')
        ser.flush()
        time.sleep(0.5)

        ser.write(b'LCFG -STSMODE=1\r\n')
        ser.flush()
        time.sleep(0.5)

        ser.write(b'LCFG -PDOAMODE=0\r\n')
        ser.flush()
        time.sleep(0.5)

        ser.write(b'SAVE\r\n')
        ser.flush()
        time.sleep(0.5)

        # Start Initiator Mode and ping all 4 Anchors
        cmd = f'INITF -MULTI -ADDR={TAG_ID} -PADDR=[1,2,3,4]\r\n'
        ser.write(cmd.encode('ascii'))
        ser.flush()
        time.sleep(0.5)

        print(f"Success! Tag {TAG_ID} is now pinging the Anchor network.\n")

        while True:
            line = ser.readline().decode('ascii', errors='ignore')
            if line.strip():
                print(line.strip())

if __name__ == "__main__":
    main()
