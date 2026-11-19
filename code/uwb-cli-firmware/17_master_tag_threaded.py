# ----------------------------------------------------------------------------
# UWB_V2X
# Status : Proposed. No run is recorded.
# About  : Merged version: threaded reader, tag as initiator with the bracketed anchor list.
# ----------------------------------------------------------------------------
import serial, time, threading

PORT       = "/dev/ttyACM0"
BAUD       = 115200
MY_ADDR    = 11        # ← change to 12 for Pi2 (TAG 2)
ANCHORS    = [1, 2, 3, 4]

stop_flag  = False

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

        # 1. Wake + clear garbage (Fixes the "STOPenough memory" bug)
        ser.write(b"\r\r")
        ser.flush()
        time.sleep(0.3)
        ser.reset_input_buffer()

        # 2. Kill any existing session
        send(ser, "STOP", wait=1.0)

        # 3. Hardware Configs (CRITICAL to prevent Decryption Fails)
        send(ser, "LCFG -STSMODE=1", wait=0.5)
        send(ser, "LCFG -PDOAMODE=0", wait=0.5)
        send(ser, "SAVE", wait=0.5)

        # 4. Start Initiator Mode (Tag pings all 4 anchors in one command)
        anc_str = "[" + ",".join(str(x) for x in ANCHORS) + "]"
        send(ser, f"INITF -MULTI -ADDR={MY_ADDR} -PADDR={anc_str}", wait=1.0)

        print(f"\n[TAG {MY_ADDR}] Ranging started. Listening for distances...\n")

        # Keep main thread alive while background thread prints data
        while True:
            time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        stop_flag = True
        print("\nStopped.")
