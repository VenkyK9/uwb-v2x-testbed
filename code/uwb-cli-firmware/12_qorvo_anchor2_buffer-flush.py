# ----------------------------------------------------------------------------
# UWB_V2X
# Status : Ran. Did not recover anchor 2 ('still no luck').
# About  : Anchor 2 script with flush(), reset_input_buffer() and CRLF line endings.
# ----------------------------------------------------------------------------
import serial, time

def main():
    with serial.Serial('/dev/ttyACM0', 115200, timeout=1) as ser:
        # 1. Wake up the board
        ser.write(b'\r\r')
        ser.flush()
        time.sleep(0.3)

        # 2. CLEAR THE GARBAGE (This fixes the STOPenough memory bug)
        ser.reset_input_buffer()

        # 3. Force Idle State
        ser.write(b'STOP\r\n')
        ser.flush()
        time.sleep(0.5)

        # 4. Set Hardware Security Configs
        ser.write(b'LCFG -STSMODE=1\r\n')
        ser.flush()
        time.sleep(0.5)

        ser.write(b'LCFG -PDOAMODE=0\r\n')
        ser.flush()
        time.sleep(0.5)

        # 5. Save the state as you correctly identified
        ser.write(b'SAVE\r\n')
        ser.flush()
        time.sleep(0.5)

        # 6. Start the Anchor and target both Bots (Tags 11 and 12)
        print("Anchor 2 is starting. Waiting for Tags 11 and 12...")
        ser.write(b'RESPF -MULTI -ADDR=2 -PADDR=[11,12]\r\n')
        ser.flush()
        time.sleep(0.5)

        # 7. Listen for distances
        while True:
            line = ser.readline().decode('ascii', errors='ignore')
            if line:
                print(line.strip())

if __name__ == "__main__":
    main()
