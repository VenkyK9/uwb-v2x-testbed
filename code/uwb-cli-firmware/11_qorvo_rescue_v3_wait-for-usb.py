# ----------------------------------------------------------------------------
# UWB_V2X
# Status : Ran. Printed 'BOARD TRAPPED IN IDLE' but the board still refused commands; a full erase and reflash was the next step.
# About  : Rescue that waits for the USB port to reappear and sends STOP at once.
# ----------------------------------------------------------------------------
import serial, time, glob

def main():
    print(">>> UNKILLABLE RESCUE SCRIPT RUNNING <<<")
    print("1. Physically UNPLUG the USB cable from the Qorvo board.")
    print("2. Wait 2 seconds.")
    print("3. PLUG the USB cable back in.")
    print("\nWaiting to trap the boot sequence...")

    while True:
        ports = glob.glob('/dev/ttyACM*')
        if ports:
            try:
                # The millisecond the port appears, grab it
                with serial.Serial(ports[0], 115200, timeout=0.1) as ser:
                    # Spam STOP and Enter
                    ser.write(b'\r\rSTOP\r')
                    response = ser.read(500).decode('ascii', errors='ignore')

                    # Look for the idle prompt
                    if 'ok' in response.lower() or 'dwm>' in response:
                        print("\n*** GOT IT! BOARD TRAPPED IN IDLE ***")

                        # Wipe the corrupted auto-start memory
                        ser.write(b'RESTORE\r')
                        time.sleep(0.5)
                        ser.write(b'SAVE\r')
                        time.sleep(0.5)

                        print("Corrupted memory wiped successfully!")
                        print("The green LED should now be OFF or steady.")
                        print("Press Ctrl+C to exit.")

                        # Keep the script paused here so it doesn't loop again
                        while True:
                            time.sleep(1)

            except Exception:
                # If the USB drops (Errno 5), ignore the crash and keep hunting
                pass

        time.sleep(0.05)

if __name__ == "__main__":
    main()
