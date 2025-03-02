import time
from octopus_sensing.devices import Shimmer3Streaming
from octopus_sensing.devices import LslStreaming
from octopus_sensing.device_coordinator import DeviceCoordinator
from octopus_sensing.device_message_endpoint import DeviceMessageHTTPEndpoint
from octopus_sensing.common.message_creators import stop_message
from octopus_sensing.realtime_data_endpoint import RealtimeDataEndpoint
from octopus_sensing.common.message_creators import start_message, stop_message, terminate_message

PORT = 9331

try:
    # Defining sensors   
    #my_mBrain2 = LslStreaming("mbtrain2", "name", "EEG", 250, output_path="./output", saving_mode=1)

    my_shimmer2 = Shimmer3Streaming(name="shimer",
                                    saving_mode=0,
                                    serial_port="/dev/rfcomm0",
                                    output_path="./output")

    # Defining device coordinator and adding sensors to it
    device_coordinator = DeviceCoordinator()
    device_coordinator.add_devices([my_shimmer2])
    
    # It receives Markers from anywhere in network, on port 9331
    message_endpoint = DeviceMessageHTTPEndpoint(device_coordinator, port=PORT)
    message_endpoint = DeviceMessageHTTPEndpoint(device_coordinator, port=PORT)
    message_endpoint.start()
    # It serves data on port 9330
    monitoring_endpoint = RealtimeDataEndpoint(device_coordinator)

    monitoring_endpoint.start()

    device_coordinator.dispatch(start_message(1, 1))

    time.sleep(5)

    device_coordinator.dispatch(stop_message(1, 1))
    experiment_id = "1"
    stimuli_id = "2"
    time.sleep(5)

    device_coordinator.dispatch(start_message(1, 2))

    time.sleep(5)

    device_coordinator.dispatch(stop_message(1, 2))


except KeyboardInterrupt:
    time.sleep(3)
    message_endpoint.stop()
    device_coordinator.dispatch(terminate_message())
    monitoring_endpoint.stop()
    device_coordinator.terminate()
    print("\nProgram interrupted.")
