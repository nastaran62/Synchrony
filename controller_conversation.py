import pygame
import argparse
import random
import time
from octopus_sensing.devices import LslStreaming
from octopus_sensing.device_coordinator import DeviceCoordinator
from octopus_sensing.common.message_creators import start_message, stop_message, terminate_message, save_message
from octopus_sensing.devices import Shimmer3Streaming
from octopus_sensing.devices import TobiiGlassesStreaming
from octopus_sensing.devices.network_devices.http_device import HttpNetworkDevice, SerializationTypes
from octopus_sensing.devices.testdevice_streaming import TestDeviceStreaming


# Define colors
white = (255, 255, 255)
black = (0, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 128)
window_width = 1500
window_height = 900

CONV_DURATION = 480
BASELKINE_DURATION = 2

def initialize():
    # Initialize Pygame
    pygame.init()

    # Set up the display
    screen = pygame.display.set_mode((window_width, window_height))
    pygame.display.set_caption("Display")

    # Define font
    font = pygame.font.Font(None, 400)
    #font = pygame.font.Font('freesansbold.ttf', 32)

    return screen, font
    # Function to display a number

def waiting_for_enter():
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Exit if the window is closed
                running = False
                break
            elif event.type == pygame.KEYDOWN:  # Detect key presses        
                if event.key == pygame.K_RETURN:
                    waiting = False
                    break
    

def display(content, screen, font):
    screen.fill(white)  # Clear the screen with white background
    text = font.render(str(content), True, blue)
    text_rect = text.get_rect(center=(window_width // 2, window_height // 2))
    screen.blit(text, text_rect)
    pygame.display.flip()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("pair", help="pair id (p01, p02, ...)", type=str)
    args = parser.parse_args()
    pair = args.pair
    screen, font = initialize()
    trials = ["Baseline"]
    trial_list = ["Conv1", "Conv2", "Conv3", "Conv4", "Conv5", "Conv6"]
    random.shuffle(trial_list)
    trials.extend(trial_list)
    experiment_id = "Conv"

    try:
        # Defining sensors
        print("Add devices")   
        #test_device = TestDeviceStreaming(256, name="TestDevice",saving_mode=0, output_path=f"./output_muse/pair{pair}")     
        
        mBrain1 = LslStreaming("mbtrain1", "name", "EEG1", 250, output_path=f"./output/pair{pair}", saving_mode=0)
        mBrain2 = LslStreaming("mbtrain2", "name", "Android_EEG_030133", 250, output_path=f"./output/pair{pair}", saving_mode=0)

        shimmer1 = Shimmer3Streaming(name="shimmer1",
                                        saving_mode=0,
                                        serial_port="/dev/rfcomm0",
                                        output_path=f"./output/pair{pair}")
        
        #shimmer1 = Shimmer3Streaming(name="shimmer1",
        #                                saving_mode=0,
        #                                serial_port="Com11",
        #                                output_path=f"./output/pair{pair}")

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
        #remote_device = HttpNetworkDevice(["http://localhost:9331"], serialization_type=SerializationTypes.PICKLE)
        device_coordinator = DeviceCoordinator()

        # All
        device_coordinator.add_devices([mBrain1, mBrain2, tobii1, tobii2, shimmer1, shimmer2])

        screen.fill(white)  # Clear the screen with white background
        pygame.display.flip()
        i = 0
        rest_index = 1
        current_index = -1
        running = True
        start = False
        rest = False
        while running:

            if not start:
                start = True
            elif not rest:
                print(f" stop {trials[current_index]}, INDEX {current_index}")
                device_coordinator.dispatch(stop_message(experiment_id, trials[current_index]))
                if (current_index+1)%rest_index == 0 and rest is False:
                    if current_index+1 >= len(trials):
                        running = False
                        break
                    rest = True
                    device_coordinator.dispatch(save_message(experiment_id))
                    display("Rest", screen, font)
                    waiting_for_enter()
            if current_index+1 >= len(trials):
                running = False
                break

            rest = False
            print("current_index", current_index)
            font = pygame.font.Font(None, 400)
            display(trials[current_index+1], screen, font)  # Update the display
            current_index += 1  # Move to the next number
            if current_index >= len(trials):  # Loop back to the start
                running = False
                break
            print(f" start {trials[current_index]}, INDEX {current_index}")
            device_coordinator.dispatch(start_message(experiment_id, trials[current_index]))
            loop = True
            start_ticks = pygame.time.get_ticks()
            if trials[current_index] == "Baseline":
                while loop:
                    # Calculate elapsed time in seconds
                    seconds = (pygame.time.get_ticks() - start_ticks) // 1000
                    # Check for space press to stop early
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            loop = False
                            running = False
                            break
                        elif event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_SPACE:
                                loop = False
                                break
                    if seconds >= BASELKINE_DURATION:
                        loop = False
            else:
                while loop:
                    # Calculate elapsed time in seconds
                    seconds = (pygame.time.get_ticks() - start_ticks) // 1000
                    # Check for space press to stop early
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            loop = False
                            running = False
                            break
                        elif event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_SPACE:
                                loop = False
                                break
                    if seconds >= CONV_DURATION:
                        loop = False
        i += 1        


        device_coordinator.dispatch(terminate_message())
    except KeyboardInterrupt:
        print("\nProgram interrupted.")
    finally:
        time.sleep(3)
        pygame.quit()
        device_coordinator.dispatch(terminate_message())
        print("done")

if __name__ == "__main__":
    main()
