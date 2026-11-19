# ----------------------------------------------------------------------------
# UWB_V2X
# Status : Kept for comparison. One test ranged anchor 1 to both tags this way (273 and 315 cm); that log is not included.
# About  : Alternative design: threaded reader; the ANCHOR is the initiator polling tags [11,12].
# ----------------------------------------------------------------------------
import serial, time, threading

PORT     = "/dev/ttyACM0"
BAUD     = 115200
MY_ADDR  = 1           # ← change to 2, 3, or 4
TAGS     = [11, 12]

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

        # Wake + clear garbage
        ser.write(b"\r\r")
        ser.flush()
        time.sleep(0.5)
        ser.reset_input_buffer()

        # Kill any existing session
        send(ser, "STOP", wait=1.0)

        # Start initiator with both tags
        tag_str = "[" + ",".join(str(x) for x in TAGS) + "]"
        send(ser, f"INITF -MULTI -ADDR={MY_ADDR} -PADDR={tag_str}", wait=1.0)

        print(f"\n[ANC {MY_ADDR}] Ranging to tags {TAGS}...\n")

        while True:
            time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        stop_flag = True
        print("\nStopped.")
