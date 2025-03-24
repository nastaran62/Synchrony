import pygame
import random
import time
from octopus_sensing.devices import LslStreaming
from octopus_sensing.device_coordinator import DeviceCoordinator
from octopus_sensing.common.message_creators import start_message, stop_message, terminate_message
from octopus_sensing.devices import Shimmer3Streaming

experiment_id = "1"
Pair = "1"

# Define colors
white = (255, 255, 255)
black = (0, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 128)
window_width = 800
window_height = 600

def pygame_initialize():
    # Initialize Pygame
    pygame.init()

    # Set up the display

    screen = pygame.display.set_mode((window_width, window_height))
    pygame.display.set_caption("Random Numbers")

    # Define font
    font = pygame.font.Font(None, 200)
    #font = pygame.font.Font('freesansbold.ttf', 32)

    # Generate random order for numbers 1 to 10
    numbers = list(range(1, 10))
    #shapes = ['circle', 'square', 'triangle', 'rectangle', 'pentagon', 'hexagon', 'diamond', 'star', 'heart']
    #random.shuffle(shapes)

    items = []
    # p1 leader, p2 follower
    if experiment_id == "1":
        items = numbers
        items.extend(numbers)
        items.extend(numbers)
        print(items)
    # p1 folower, p2 leader
    elif experiment_id == "2":
        items = numbers
        items.extend(numbers)
        items.extend(numbers)
        print(items)
    # p1 leader, p2 leader
    elif experiment_id == "3":
        items = numbers
        items.extend(numbers)
        items.extend(numbers)
        random.shuffle(items)
        print(items)
    # p1 folower, p2 leader
    elif experiment_id == "4":
        items = numbers
        items.extend(numbers)
        items.extend(numbers)
        random.shuffle(items)
        print(items)
    # p1 leader, p2 folower
    elif experiment_id == "5":
        items = ["Free"]
    # p1 folower, p2 leader
    elif experiment_id == "6":
        items = ["Free"]


    return screen, font, items

    # Function to display a number
def display_number(number, screen, font):
    screen.fill(white)  # Clear the screen with white background
    text = font.render(str(number), True, blue)
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
        my_mBrain1 = LslStreaming("mbtrain1", "name", "EEG1", 250, output_path="./pair{0}".format(Pair), saving_mode=0)
        my_mBrain2 = LslStreaming("mbtrain2", "name", "Android_EEG_030132", 250, output_path="./pair{0}".format(Pair), saving_mode=0)

        my_shimmer1 = Shimmer3Streaming(name="shimmer1",
                                        saving_mode=0,
                                        serial_port="/dev/rfcomm3",
                                        output_path="./pair{0}".format(Pair))
        my_shimmer2 = Shimmer3Streaming(name="shimmer2",
                                        saving_mode=0,
                                        serial_port="/dev/rfcomm2",
                                        output_path="./pair{0}".format(Pair))


        # Defining device coordinator and adding sensors to it
        device_coordinator = DeviceCoordinator()
        #device_coordinator.add_devices([my_mBrain1, my_mBrain2])
        device_coordinator.add_devices([my_shimmer1, my_shimmer2])


        screen.fill(white)  # Clear the screen with white background
        pygame.display.flip()
        running = True
        while running:
            for event in pygame.event.get():
                #display_number(numbers[current_index])  # Update the display
                if event.type == pygame.QUIT:  # Exit if the window is closed
                    running = False
                    break
                elif event.type == pygame.KEYDOWN:  # Detect key presses
                    if event.key == pygame.K_s:  # Check if the key is the s, start data recording
                        print(f" start {numbers[current_index]}, INDEX {current_index}")
                        device_coordinator.dispatch(start_message(experiment_id, numbers[current_index]))
                    if event.key == pygame.K_e:  # Check if the key is the s, stop data recording
                        print(f" stop {numbers[current_index]}, INDEX {current_index}")
                        device_coordinator.dispatch(stop_message(experiment_id, numbers[current_index]))
                    if event.key == pygame.K_SPACE:  # Check if the key is the spacebar go to next
                        print(current_index, len(numbers))
                        display_number(numbers[current_index], screen, font)  # Update the display
                        current_index += 1  # Move to the next number
                        if current_index >= len(numbers):  # Loop back to the start
                            running = False
                            break
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