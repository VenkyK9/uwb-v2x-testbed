# ----------------------------------------------------------------------------
# UWB_V2X
# Status : Ran. Failed with 'write failed: [Errno 5] Input/output error' when the board reset.
# About  : Rescue with automatic /dev/ttyACM* detection.
# ----------------------------------------------------------------------------
import serial, time, glob

def main():
    # 1. Auto-detect the active USB port
    ports = glob.glob('/dev/ttyACM*')

    if not ports:
        print("Error: The Pi doesn't see the board at all. Unplug and replug the USB!")
        return

    port = ports[0] # Grab the first available port (ACM0, ACM1, etc.)

    print(f">>> RESCUE SCRIPT RUNNING ON {port} <<<")
    print("PRESS AND RELEASE THE SMALL RESET BUTTON (SW1) ON THE BOARD NOW!")

    try:
        with serial.Serial(port, 115200, timeout=0.1) as ser:
            # 2. Spam STOP incredibly fast to trap the boot sequence
            for _ in range(60):
                ser.write(b'\r\rSTOP\r')
                time.sleep(0.05)

            print("\nBoard trapped in IDLE state. Wiping corrupted memory...")
            time.sleep(1.0)

            # 3. Restore and Save
            ser.write(b'RESTORE\r')
            time.sleep(1.0)

            ser.write(b'SAVE\r')
            time.sleep(1.0)

            print("Output from board:")
            print(ser.read(2000).decode('ascii', errors='ignore'))
            print("\nRescue Complete! The green LED should now be OFF or steady.")

    except Exception as e:
        print(f"Error: Could not open {port}. Details: {e}")

if __name__ == "__main__":
    main()
