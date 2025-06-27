import time
from octopus_sensing.devices import Shimmer3Streaming
from octopus_sensing.devices import LslStreaming
from octopus_sensing.devices import TobiiGlassesStreaming
from octopus_sensing.device_coordinator import DeviceCoordinator
from octopus_sensing.device_message_endpoint import DeviceMessageHTTPEndpoint
from octopus_sensing.common.message_creators import stop_message
from octopus_sensing.common.message_creators import start_message, stop_message, terminate_message

PORT = 9331
experiment_id = "10"
Pair = "1"

try:
    # Defining sensors   
    #my_mBrain2 = LslStreaming("mbtrain2", "name", "EEG", 250, output_path="./output", saving_mode=1)


    tobii2 = TobiiGlassesStreaming("192.168.71.50",
                                    50,
                                    name="tobii1",
                                    saving_mode=0,
                                    output_path="./pair{0}".format(Pair))

    # Defining device coordinator and adding sensors to it
    device_coordinator = DeviceCoordinator()
    device_coordinator.add_devices([tobii2])
    
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
