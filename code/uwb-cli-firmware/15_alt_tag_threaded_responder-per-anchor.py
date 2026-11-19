# ----------------------------------------------------------------------------
# UWB_V2X
# Status : Kept for comparison. The per-anchor loop cannot work: the firmware accepts one session at a time (see the stacking test).
# About  : Alternative design: threaded reader; the TAG runs RESPF once per anchor.
# ----------------------------------------------------------------------------
import serial, time, threading

PORT       = "/dev/ttyACM0"
BAUD       = 115200
MY_ADDR    = 11        # ← change to 12 for TAG2
ANCHORS    = [1, 2, 3, 4]

output_lines = []
stop_flag    = False

def reader(ser):
    while not stop_flag:
        try:
            line = ser.readline().decode("ascii", errors="ignore").strip()
            if line:
                print(line)
                output_lines.append(line)
        except:
            pass

def send(ser, cmd, wait=0.5):
    print(f">>> {cmd}")
    ser.write((cmd + "\r\n").encode("ascii"))
    ser.flush()
    time.sleep(wait)

def wait_active(timeout=10):
    start = time.time()
    seen = len(output_lines)
    while time.time() - start < timeout:
        for line in output_lines[seen:]:
            if "ACTIVE" in line:
                return True
        time.sleep(0.1)
    return False

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
        output_lines.clear()

        # Kill any existing session
        send(ser, "STOP", wait=1.0)

        # Register one RESPF session per anchor
        for anc in ANCHORS:
            output_lines.clear()
            send(ser, f"RESPF -MULTI -ADDR={MY_ADDR} -PADDR={anc}", wait=0.3)
            if wait_active(timeout=8):
                print(f"  ✓ ACTIVE for ANC{anc}")
            else:
                print(f"  ✗ No ACTIVE for ANC{anc} – check anchor MAC")
            time.sleep(0.5)

        print(f"\n[TAG {MY_ADDR}] All sessions started. Listening...\n")

        # Stream ranging output indefinitely
        while True:
            time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        stop_flag = True
        print("\nStopped.")
