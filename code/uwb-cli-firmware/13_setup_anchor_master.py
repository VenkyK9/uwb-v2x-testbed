# ----------------------------------------------------------------------------
# UWB_V2X
# Status : Proposed once the correct firmware was reported installed. No run is recorded.
# About  : One anchor script for all Pis: set ANCHOR_ID, peers are tags [11,12].
# ----------------------------------------------------------------------------
import serial, time

# === CONFIGURATION ===
# CHANGE THIS NUMBER FOR EACH PI! (Use 1, 2, 3, or 4)
ANCHOR_ID = 1
# =====================

def main():
    print(f"Initializing Anchor {ANCHOR_ID}...")

    # Try to open the USB serial port
    try:
        ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
    except:
        print("Error: Could not open /dev/ttyACM0. Is the board plugged in?")
        return

    with ser:
        # 1. Wake up the board
        ser.write(b'\r\r')
        ser.flush()
        time.sleep(0.3)

        # 2. CLEAR THE GARBAGE BUFFER (Crucial to prevent 'STOPenough memory' bug)
        ser.reset_input_buffer()

        # 3. Force Idle State
        ser.write(b'STOP\r\n')
        ser.flush()
        time.sleep(0.5)

        # 4. Set Hardware Security Configs (Must match the Tags)
        ser.write(b'LCFG -STSMODE=1\r\n')
        ser.flush()
        time.sleep(0.5)

        ser.write(b'LCFG -PDOAMODE=0\r\n')
        ser.flush()
        time.sleep(0.5)

        # 5. Save the state
        ser.write(b'SAVE\r\n')
        ser.flush()
        time.sleep(0.5)

        # 6. Start Responder Mode and target both Bots (Tags 11 and 12)
        cmd = f'RESPF -MULTI -ADDR={ANCHOR_ID} -PADDR=[11,12]\r\n'
        ser.write(cmd.encode('ascii'))
        ser.flush()
        time.sleep(0.5)

        print(f"Success! Anchor {ANCHOR_ID} is now listening for Tags 11 and 12.\n")

        # 7. Listen and print incoming distance data
        while True:
            line = ser.readline().decode('ascii', errors='ignore')
            if line.strip():
                print(line.strip())

if __name__ == "__main__":
    main()
