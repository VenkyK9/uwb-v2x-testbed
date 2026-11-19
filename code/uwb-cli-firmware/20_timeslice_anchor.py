# ----------------------------------------------------------------------------
# UWB_V2X
# Status : Proposed. No run is recorded; the project moved to UCI firmware instead.
# About  : Anchor that alternates every 2.5 s between tag 11 and tag 12 (STOP, RESPF, wait).
# ----------------------------------------------------------------------------
import serial, time, threading

PORT     = "/dev/ttyACM0"
BAUD     = 115200
MY_ADDR  = 1            # ← CHANGE TO 2, 3, or 4 based on the Pi!

stop_flag = False

def reader(ser):
    while not stop_flag:
        try:
            line = ser.readline().decode("ascii", errors="ignore").strip()
            if line:
                print(line)
        except:
            pass

def send(ser, cmd, wait=0.5):
    print(f">>> {cmd}")
    ser.write((cmd + "\r\n").encode("ascii"))
    ser.flush()
    time.sleep(wait)

def main():
    global stop_flag
    with serial.Serial(PORT, BAUD, timeout=1) as ser:
        t = threading.Thread(target=reader, args=(ser,), daemon=True)
        t.start()

        ser.write(b"\r\r")
        ser.flush()
        time.sleep(0.3)
        ser.reset_input_buffer()

        # Initial Configuration
        send(ser, "STOP", wait=1.0)
        send(ser, "LCFG -STSMODE=1", wait=0.5)
        send(ser, "LCFG -PDOAMODE=0", wait=0.5)
        send(ser, "SAVE", wait=0.5)

        print(f"\n[ANC {MY_ADDR}] Entering Multiplexing Loop...\n")

        # The Time-Slicing Loop
        while not stop_flag:
            # --- Listen to BOT 1 (Tag 11) ---
            send(ser, "STOP", wait=0.2)
            send(ser, f"RESPF -MULTI -ADDR={MY_ADDR} -PADDR=11", wait=0.2)
            print(f"\n---> LOCKING ONTO BOT 1 (TAG 11) <---")
            time.sleep(2.5) # Listen for 2.5 seconds

            # --- Listen to BOT 2 (Tag 12) ---
            send(ser, "STOP", wait=0.2)
            send(ser, f"RESPF -MULTI -ADDR={MY_ADDR} -PADDR=12", wait=0.2)
            print(f"\n---> LOCKING ONTO BOT 2 (TAG 12) <---")
            time.sleep(2.5) # Listen for 2.5 seconds

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        stop_flag = True
        print("\nStopped.")
