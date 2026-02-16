import pygame
import argparse
from octopus_sensing.device_coordinator import DeviceCoordinator
from muse_athena_streaming import MuseAthenaStreaming

from octopus_sensing.common.message_creators import start_message, stop_message, terminate_message

parser = argparse.ArgumentParser()
parser.add_argument("id", help="Experiment ID, mu or mb", type=str)
parser.add_argument("pair", help="pair id (p01, p02, ...)", type=str)
args = parser.parse_args()

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

experiment_id = args.id
pair = args.pair

# Function to display a number
def display_number(number):
    screen.fill(white)  # Clear the screen with white background
    text = font.render(str(number), True, blue)
    text_rect = text.get_rect(center=(window_width // 2, window_height // 2))
    screen.blit(text, text_rect)
    pygame.display.flip()

# Main loop to display numbers
current_index = 0
start_flag = False

try:
    muse1 = MuseAthenaStreaming("museBE3A", 5900, 256, saving_mode=0, output_path=f"./output_muse/pair{pair}")
    #muse2 = MuseAthenaStreaming("museF19E", 5800, 256, saving_mode=0, output_path=f"./output_muse/pair{pair}")
    device_coordinator = DeviceCoordinator()
    device_coordinator.add_devices([muse1])

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
                if event.key == pygame.K_SPACE:  # Check if the key is the space, start data recording
                    print(f" start {current_index}")
                    device_coordinator.dispatch(start_message(experiment_id, str(current_index)))
                    display_number(current_index)  # Update the display
                if event.key == pygame.K_RETURN:  # Check if the key is the enter, stop data recording
                    print(f" stop {[current_index]}")
                    device_coordinator.dispatch(stop_message(experiment_id, str(current_index)))
                    current_index += 1  # Move to the next number
                if event.key == pygame.K_ESCAPE:  # Check if the key is the scape terminate
                    device_coordinator.dispatch(terminate_message())
                    running = False
                    break
        if not running:
            break
    
except KeyboardInterrupt:
    device_coordinator.dispatch(terminate_message())
    print("\nProgram interrupted.")
finally:
    pygame.quit()
