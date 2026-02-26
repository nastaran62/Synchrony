import time
import argparse
from octopus_sensing.devices import Shimmer3Streaming
from octopus_sensing.devices import LslStreaming
from octopus_sensing.devices import TobiiGlassesStreaming
from octopus_sensing.device_coordinator import DeviceCoordinator
from octopus_sensing.device_message_endpoint import DeviceMessageHTTPEndpoint
from octopus_sensing.common.message_creators import terminate_message

PORT = 9331

parser = argparse.ArgumentParser()
parser.add_argument("pair", help="pair id (p01, p02, ...)", type=str)
args = parser.parse_args()
experiment_id = "r"
pair = args.parse("pair")

try:
    # Defining sensors   
    mBrain1 = LslStreaming("mbtrain1", "name", "EEG1", 250, output_path=f"./output/pair{pair}", saving_mode=0)
    mBrain2 = LslStreaming("mbtrain2", "name", "Android_EEG_030133", 250, output_path=f"./output/pair{pair}", saving_mode=0)
    shimmer1 = Shimmer3Streaming(name="shimmer1",
                                saving_mode=0,
                                serial_port="/dev/rfcomm0",
                                output_path=f"./output/pair{pair}")
    shimmer2 = Shimmer3Streaming(name="shimmer2",
                                saving_mode=0,
                                serial_port="/dev/rfcomm3",
                                output_path=f"./output/pair{pair}")
        
    tobii1 = TobiiGlassesStreaming("192.168.1.214",
                                    50,
                                    name="tobii1",
                                    saving_mode=0,
                                    output_path=f"./output/pair{pair}")
    tobii2 = TobiiGlassesStreaming("192.168.1.232",
                                    50,
                                    name="tobii2",
                                    saving_mode=0,
                                    output_path=f"./output/pair{pair}")

    # Defining device coordinator and adding sensors to it
    device_coordinator = DeviceCoordinator()
    device_coordinator.add_devices([mBrain1, mBrain2, tobii1, tobii2, shimmer1, shimmer2])
    
    # It receives Markers from anywhere in network, on port 9331
    message_endpoint = DeviceMessageHTTPEndpoint(device_coordinator, port=PORT)
    message_endpoint.start()
    # It serves data on port 9330


except KeyboardInterrupt:
    time.sleep(3)
    message_endpoint.stop()
    device_coordinator.dispatch(terminate_message())
    device_coordinator.terminate()
    print("\nProgram interrupted.")
