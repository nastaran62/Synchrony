import pygame
import random
import time
from octopus_sensing.devices import LslStreaming
from octopus_sensing.device_coordinator import DeviceCoordinator
from octopus_sensing.common.message_creators import start_message, stop_message, terminate_message
from octopus_sensing.devices import Shimmer3Streaming

# Initialize Pygame
pygame.init()

# Set up the display
window_width = 800
window_height = 600
screen = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("Random Numbers")

# Define colors
white = (255, 255, 255)
black = (0, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 128)

# Define font
font = pygame.font.Font(None, 200)
#font = pygame.font.Font('freesansbold.ttf', 32)

# Generate random order for numbers 1 to 10
numbers = list(range(1, 10))

print(numbers)
random.shuffle(numbers)
print(numbers)

experiment_id = "1"
stimuli_id = "1"

# Function to display a number
def display_number(number):
    screen.fill(white)  # Clear the screen with white background
    text = font.render(str(number), True, blue)
    text_rect = text.get_rect(center=(window_width // 2, window_height // 2))
    screen.blit(text, text_rect)
    pygame.display.flip()

# Main loop to display numbers
current_index = -1
start_flag = False

try:
    # Defining sensors
    my_mBrain1 = LslStreaming("mbtrain1", "name", "EEG1", 250, output_path="./output", saving_mode=0)
    my_mBrain2 = LslStreaming("mbtrain2", "name", "Android_EEG_030132", 250, output_path="./output", saving_mode=0)
    
    my_shimmer1 = Shimmer3Streaming(name="shimmer1",
                                    saving_mode=0,
                                    serial_port="/dev/rfcomm0",
                                    output_path="./output")
    my_shimmer2 = Shimmer3Streaming(name="shimmer2",
                                    saving_mode=0,
                                    serial_port="/dev/rfcomm2",
                                    output_path="./output")
    

    # Defining device coordinator and adding sensors to it
    device_coordinator = DeviceCoordinator()
    #device_coordinator.add_devices([my_mBrain1, my_mBrain2])
    device_coordinator.add_devices([my_mBrain1, my_mBrain2, my_shimmer1, my_shimmer2])

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
                    display_number(numbers[current_index])  # Update the display
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