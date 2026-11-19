# ----------------------------------------------------------------------------
# UWB_V2X
# Status : Ran. Failed with 'Could not open port', before and after qorvo-live.service was disabled; a changed port number was suspected next.
# About  : Rescue for anchor 2: flood STOP while pressing SW1, then RESTORE and SAVE.
# ----------------------------------------------------------------------------
import serial, time

def main():
    print(">>> RESCUE SCRIPT RUNNING <<<")
    print("PRESS AND RELEASE THE SMALL RESET BUTTON (SW1) ON THE BOARD NOW!")

    try:
        with serial.Serial('/dev/ttyACM0', 115200, timeout=0.1) as ser:
            # Spam STOP incredibly fast to trap the boot sequence
            for _ in range(60):
                ser.write(b'\r\rSTOP\r')
                time.sleep(0.05)

            print("\nBoard trapped in IDLE state. Wiping corrupted memory...")
            time.sleep(1.0)

            # Now that the radio is off, RESTORE will work
            ser.write(b'RESTORE\r')
            time.sleep(1.0)

            ser.write(b'SAVE\r')
            time.sleep(1.0)

            print("Output from board:")
            print(ser.read(2000).decode('ascii', errors='ignore'))
            print("\nRescue Complete! The green LED should now be OFF or steady.")

    except serial.SerialException:
        print("Error: Could not open port. Make sure miniterm is closed!")

if __name__ == "__main__":
    main()
