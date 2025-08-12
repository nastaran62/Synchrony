import socket
import struct
import csv
import time

# CSV setup
csv_filename = f"muse_multistream_{int(time.time())}.csv"
csv_file = open(csv_filename, mode='w', newline='')
csv_writer = csv.writer(csv_file)
csv_writer.writerow([
    "Timestamp",
    "TP9", "AF7", "AF8", "TP10",           # EEG
    "Acc_X", "Acc_Y", "Acc_Z",            # Accelerometer
    "Gyro_X", "Gyro_Y", "Gyro_Z",         # Gyroscope
    "Heart_Rate",                         # Heart
    "fNIRS_Left", "fNIRS_Right"           # fNIRS (hypothetical)
])

# TCP server setup
HOST = '0.0.0.0'
PORT = 5000

# Data buffers
latest_data = {
    "eeg": [None] * 4,
    "acc": [None] * 3,
    "gyro": [None] * 3,
    "heart": [None],
    "fnirs": [None] * 2
}

def parse_osc_message(data):
    try:
        address_end = data.find(b'\x00')
        address = data[:address_end].decode('utf-8')

        type_tag_start = (address_end + 4) & ~3
        type_tag_end = data.find(b'\x00', type_tag_start)
        type_tag = data[type_tag_start:type_tag_end].decode('utf-8')

        values_start = (type_tag_end + 4) & ~3
        num_floats = type_tag.count('f')
        values = struct.unpack(f'>{num_floats}f', data[values_start:values_start + 4 * num_floats])

        return address, values
    except Exception as e:
        print(f"Parse error: {e}")
        return None, None

def write_row():
    timestamp = time.time()
    row = [timestamp]
    row += latest_data["eeg"]
    row += latest_data["acc"]
    row += latest_data["gyro"]
    row += latest_data["heart"]
    row += latest_data["fnirs"]
    csv_writer.writerow(row)
    print(f"{timestamp}: {row}")

# Start TCP server
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen(1)
    print(f"Listening for Muse TCP data on {HOST}:{PORT}...")
    conn, addr = s.accept()
    with conn:
        print(f"Connected by {addr}")
        buffer = b''
        try:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                buffer += data

                while len(buffer) >= 32:
                    msg = buffer[:32]
                    buffer = buffer[32:]
                    address, values = parse_osc_message(msg)
                    if address and values:
                        if address == "/muse/eeg":
                            latest_data["eeg"] = list(values)
                        elif address == "/muse/acc":
                            latest_data["acc"] = list(values)
                        elif address == "/muse/gyro":
                            latest_data["gyro"] = list(values)
                        elif address == "/muse/heart":
                            latest_data["heart"] = list(values)
                        elif address == "/muse/fnirs":
                            latest_data["fnirs"] = list(values)
                        
                        # Write row if EEG is updated (you can change this trigger)
                        if address == "/muse/eeg":
                            write_row()
        except KeyboardInterrupt:
            print("Stopping...")
        finally:
            csv_file.close()
