import pygame
import random
import time
from octopus_sensing.devices import LslStreaming
from octopus_sensing.device_coordinator import DeviceCoordinator
from octopus_sensing.common.message_creators import start_message, stop_message, terminate_message, save_message
from octopus_sensing.devices import Shimmer3Streaming
from octopus_sensing.devices import TobiiGlassesStreaming
from octopus_sensing.devices.network_devices.http_device import HttpNetworkDevice, SerializationTypes

# experiment_id = "1"  : numbers # p1 leader, p2 follower
# experiment_id = "2"  : numbers # p1 follower, p2 leader   
# experiment_id = "3"  : shuffled numbers # p1 leader, p2 leader
# experiment_id = "4"  : shuffled numbers # p1 follower, p2 leader
# experiment_id = "5"  : Free # p1 leader, p2 follower
# experiment_id = "6"  : Free # p1 follower, p2 leader
# experiment_id = "7"  : shapes # p1 leader, p2 follower
# experiment_id = "8"  : shapes # p1 follower, p2 leader      
# experiment_id = "9"  : shuffled shapes # p1 leader, p2 leader
# experiment_id = "10" : shuffled shapes # p1 follower, p2 leader

experiment_id = "1"
Pair = "02"
rest_index = 9  # Number of items before rest

# Define colors
white = (255, 255, 255)
black = (0, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 128)
window_width = 1500
window_height = 900

def pygame_initialize():
    # Initialize Pygame
    pygame.init()

    # Set up the display

    screen = pygame.display.set_mode((window_width, window_height))
    pygame.display.set_caption("Display")

    # Define font
    font = pygame.font.Font(None, 400)
    #font = pygame.font.Font('freesansbold.ttf', 32)

    # Generate random order for numbers 1 to 10
    numbers = list(range(1, 10))
    print(numbers) 
    shapes = ['Circle', 'Square', 'Triangle', 'Rectangle', 'Pentagon', 'Hexagon', 'Diamond', 'Star', 'Heart']
    #random.shuffle(shapes)

    items = []
    # p1 leader, p2 follower
    if experiment_id == "1":
        items = numbers
        items = items * 3  # Repeat the numbers three times
        print(items)
    # p1 folower, p2 leader
    elif experiment_id == "2":
        items = numbers
        items = items * 3  # Repeat the numbers three times
        print(items)
    # p1 leader, p2 leader
    elif experiment_id == "3":
        items = numbers
        items = items * 3  # Repeat the numbers three times
        random.shuffle(items)
        print(items)
    # p1 folower, p2 leader
    elif experiment_id == "4":
        items = numbers
        items = items * 3  # Repeat the numbers three times
        random.shuffle(items)
        print(items)
    # p1 leader, p2 folower
    elif experiment_id == "5":
        items = ["Free"]
    # p1 folower, p2 leader
    elif experiment_id == "6":
        items = ["Free"]
    # p1 leader, p2 leader
    elif experiment_id == "7":
        items = shapes
        items = items * 3  # Repeat the numbers three times
        print(items)
    # p1 folower, p2 leader
    elif experiment_id == "8":
        items = shapes
        items = items * 3  # Repeat the numbers three times
        print(items)
    # p1 leader, p2 leader
    elif experiment_id == "9":
        items = shapes
        items = items * 3  # Repeat the numbers three times
        random.shuffle(items)
        print(items)
    # p1 folower, p2 leader
    elif experiment_id == "10":
        items = shapes
        items = items * 3  # Repeat the numbers three times
        random.shuffle(items)
        print(items)


    return screen, font, items

    # Function to display a number
def display(content, screen, font):
    screen.fill(white)  # Clear the screen with white background
    text = font.render(str(content), True, blue)
    text_rect = text.get_rect(center=(window_width // 2, window_height // 2))
    screen.blit(text, text_rect)
    pygame.display.flip()

def main():
    screen, font, numbers = pygame_initialize()
    # 1: Zane numbers, 2: Carl numbers, 3: Zane leader free, 4: Carl leader free


    # Main loop to display numbers
    current_index = -1
    start_flag = False

    try:
        # Defining sensors
        
        mBrain1 = LslStreaming("mbtrain1", "name", "EEG1", 250, output_path="./output/pair{0}".format(Pair), saving_mode=0)
        mBrain2 = LslStreaming("mbtrain2", "name", "Android_EEG_030133", 250, output_path="./output/pair{0}".format(Pair), saving_mode=0)

        shimmer1 = Shimmer3Streaming(name="shimmer1",
                                        saving_mode=0,
                                        serial_port="Com4",
                                        output_path="./output/pair{0}".format(Pair))
        shimmer2 = Shimmer3Streaming(name="shimmer2",
                                        saving_mode=0,
                                        serial_port="Com5",
                                        output_path="./output/pair{0}".format(Pair))
            
        tobii1 = TobiiGlassesStreaming("192.168.1.214",
                                       50,
                                       name="tobii1",
                                       saving_mode=0,
                                       output_path="./output/pair{0}".format(Pair))
        tobii2 = TobiiGlassesStreaming("192.168.1.232",
                                       50,
                                       name="tobii2",
                                       saving_mode=0,
                                       output_path="./output/pair{0}".format(Pair))
        

        # Defining device coordinator and adding sensors to it
        #remote_device = HttpNetworkDevice(["http://localhost:9331"], serialization_type=SerializationTypes.PICKLE)
        device_coordinator = DeviceCoordinator()

        # All
        device_coordinator.add_devices([mBrain1, mBrain2, shimmer1, shimmer2, tobii1, tobii2])

        screen.fill(white)  # Clear the screen with white background
        pygame.display.flip()
        running = True
        start = False
        rest = False
        while running:
            for event in pygame.event.get():
                #display_number(numbers[current_index])  # Update the display
                if event.type == pygame.QUIT:  # Exit if the window is closed
                    running = False
                    break
                elif event.type == pygame.KEYDOWN:  # Detect key presses        
                    if event.key == pygame.K_SPACE:  # Check if the key is the s, stop data recording
                        if not start:
                            start = True
                        elif not rest:
                            print(f" stop {numbers[current_index]}, INDEX {current_index}")
                            device_coordinator.dispatch(stop_message(experiment_id, numbers[current_index]))
                            if (current_index+1)%rest_index == 0 and rest is False:
                                rest = True
                                device_coordinator.dispatch(save_message(experiment_id))
                                display("Rest", screen, font)
                                break

                        rest = False
                        display("+", screen, font)
                        time.sleep(2)
                        print("current_index", current_index)
                        display(numbers[current_index+1], screen, font)  # Update the display
                        current_index += 1  # Move to the next number
                        if current_index >= len(numbers):  # Loop back to the start
                            running = False
                            break
                        print(f" start {numbers[current_index]}, INDEX {current_index}")
                        device_coordinator.dispatch(start_message(experiment_id, numbers[current_index]))


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