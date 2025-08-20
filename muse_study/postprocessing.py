
# How to use this script:
# 2. Run the script with the input JSONL file and output path as arguments:
#    python postprocessing.py --in_file path/to/input.jsonl --out_path path/to
# Example: pipenv run python postprocessing.py 
# --in_file "/home/zsaf419/projects/muse_study/output/pair09/muse/muse-E5.jsonl" 
# --out_path "/home/zsaf419/projects/muse_study/output/pair09/muse"


import json
import os
eeg_list = []
fnirs_list = []
accel_list = []
gyro_list = []
ppg_list = []
marker = None

#get the name of input file as an argument with argparse
import argparse
parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--in_file', type=str, help='Path to the input JSONL file')
parser.add_argument('--out_path', type=str, help='Path to the output', default=None)

args = parser.parse_args()

input_file = args.in_file    

output_path = args.out_path

def interpret_json():
    """
    Interpret the received JSON data.
    This function can be customized based on the expected structure of the JSON.
    """
    # read json list from A JSONL FILE
    #script_dir = os.path.dirname(os.path.abspath(__file__))
    #file_path = os.path.join(script_dir, "output", "pair09", "muse", "muse-E5.jsonl")
    with open(input_file, "r") as f:
        json_lines = [json.loads(line) for line in f]
    # For demonstration, process the first JSON object from the file
    if json_lines:
        json_data = json_lines[0]

    # This function processes the JSON data and extracts relevant information.
    # Initialize lists to store data from different sensors
    global eeg_list, fnirs_list, accel_list, gyro_list, ppg_list, marker

    # Example: print the keys and values in the JSON
    for json_data in json_lines:
        for key, value in json_data.items():
            timestamp = json_data.get("timestamp", None)
            if key not in ["marker", "timestamp"]:
                value.append(timestamp)  # Assuming timestamp is part of the data
            if key == "EEG":
                eeg_list.append(value)
            elif key == "Fnirs":
                fnirs_list.append(value)
            elif key == "Accel":
                accel_list.append(value)
            elif key == "Gyro":
                gyro_list.append(value)
            elif key == "PPG":
                ppg_list.append(value)
            elif key == "marker":
                if len(eeg_list) > 0:
                    eeg_list[-1].append(value)
                    # Assuming marker is added to the last EEG entry
                if len(fnirs_list) > 0: 
                    fnirs_list[-1].append(value)
                if len(accel_list) > 0:
                    accel_list[-1].append(value)
                if len(gyro_list) > 0:
                    gyro_list[-1].append(value)
                if len(ppg_list) > 0:
                    ppg_list[-1].append(value)
            
    # Write the lists to separate CSV files
    with open(os.path.join(output_path, "eeg_data.csv"), "w") as f:
        for item in eeg_list:
            f.write(",".join(map(str, item)) + "\n")
    with open(os.path.join(output_path, "fnirs_data.csv"), "w") as f:
        for item in fnirs_list:
            f.write(",".join(map(str, item)) + "\n")
    with open(os.path.join(output_path, "accel_data.csv"), "w") as f:
        for item in accel_list:
            f.write(",".join(map(str, item)) + "\n")
    with open(os.path.join(output_path, "gyro_data.csv"), "w") as f:
        for item in gyro_list:
            f.write(",".join(map(str, item)) + "\n")

interpret_json()