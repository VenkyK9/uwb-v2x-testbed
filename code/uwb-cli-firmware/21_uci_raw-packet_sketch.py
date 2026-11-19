# ----------------------------------------------------------------------------
# UWB_V2X
# Status : Sketch only. The app-config payload is a placeholder ('4103...'), so it cannot run as written.
# About  : Illustration of raw UCI packets over pyserial.
# ----------------------------------------------------------------------------
import serial
import time

PORT = "/dev/ttyACM0"
BAUD = 115200

# Helper function to send raw bytes
def send_uci_packet(ser, hex_string):
    packet = bytes.fromhex(hex_string)
    ser.write(packet)
    time.sleep(0.1)
    # Read response header
    response = ser.read(ser.in_waiting)
    return response

def main():
    ser = serial.Serial(PORT, BAUD, timeout=1)

    print("Resetting UWB Device...")
    # CORE_DEVICE_RESET (Group 00, Opcode 00)
    send_uci_packet(ser, "4000010000")
    time.sleep(1)

    print("Initializing Session...")
    # SESSION_INIT (Group 01, Opcode 00) - Session ID: 101, Session Type: 00
    send_uci_packet(ser, "410005006500000000")

    print("Setting App Config for O2M Controller...")
    # SESSION_SET_APP_CONFIG (Group 01, Opcode 03)
    # This hex string is a simplified representation.
    # It must contain Tag MAC, Device Role=0 (Init), Device Type=1 (Controller),
    # Multi-node=1 (O2M), and No. of Controlees=4 (plus their MACs)
    # >> You will generate this specific byte array using the Qorvo Python tool.
    app_config_payload = "4103..."
    send_uci_packet(ser, app_config_payload)

    print("Starting Ranging...")
    # SESSION_START (Group 01, Opcode 01) - Session ID: 101
    send_uci_packet(ser, "4101040065000000")

    print("Listening for Distance Notifications...")
    while True:
        # Distance data comes back as SESSION_INFO_NTF (Group 01, Opcode 02)
        # You will parse the raw bytes here to extract the distance integer
        data = ser.read(ser.in_waiting)
        if data:
            # Parse the binary data to extract anchor distances
            pass

if __name__ == "__main__":
    main()
