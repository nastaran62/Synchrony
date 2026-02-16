import pygame
import argparse
from octopus_sensing.device_coordinator import DeviceCoordinator
from muse_athena_streaming import MuseAthenaStreaming
from octopus_sensing.devices.testdevice_streaming import TestDeviceStreaming
from random import shuffle
from octopus_sensing.devices import LslStreaming

from octopus_sensing.common.message_creators import start_message, stop_message, terminate_message, save_message

def display(content, screen, font):
    screen.fill(white)  # Clear the screen with white background
    text = font.render(str(content), True, blue)
    text_rect = text.get_rect(center=(window_width // 2, window_height // 2))
    screen.blit(text, text_rect)
    pygame.display.flip()

parser = argparse.ArgumentParser()
parser.add_argument("id", help="Experiment ID, mu or mb", type=str)
parser.add_argument("task", help="Task ID, F: finger tapping, T: Tangram", type=str)
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
task = args.task

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
    #muse1 = MuseAthenaStreaming("museBE3A", 5900, 256, saving_mode=0, output_path=f"./output_muse/pair{pair}")
    #muse2 = MuseAthenaStreaming("museF19E", 5800, 256, saving_mode=0, output_path=f"./output_muse/pair{pair}")
    mBrain1 = LslStreaming("mbtrain1", "name", "EEG1", 250, output_path=f"./output/pair{pair}", saving_mode=0)
    mBrain2 = LslStreaming("mbtrain2", "name", "Android_EEG_030133", 250, output_path=f"./output/pair{pair}", saving_mode=0)
    test_device = TestDeviceStreaming(256, name="TestDevice",saving_mode=0, output_path=f"./output_muse/pair{pair}")
    device_coordinator = DeviceCoordinator()
    device_coordinator.add_devices([mBrain1, mBrain2])
    print("Devices added to coordinator.")

    screen.fill(white)  # Clear the screen with white background


    pygame.display.flip()


    
    blocks = ["Baseline", "baseline1"] 
    if task == "F":
        
        task1 = ["P1_leader", "P2_leader", "Metronome"]
        shuffle(task1)
        blocks.extend(task1)
    else:
        task2 = ["Tangram"]
        shuffle(task2)
        blocks = ["Tangram1", "Tangram2", "Tangram3", "Tangram4", "Tangram5"]

    running = True
    print("blocks:", blocks)

    for item in blocks:
        print("item", item)
        running = True
        start = False
  
        font = pygame.font.Font(None, 100)
        while running:
            for event in pygame.event.get():
                #display_number(numbers[current_index])  # Update the display
                if event.type == pygame.QUIT:  # Exit if the window is closed
                    running = False
                    break
                elif event.type == pygame.KEYDOWN:  # Detect key presses
                    if event.key == pygame.K_SPACE:  # Check if the key is the space, start data recording
                        print(f" start {item}")
                        device_coordinator.dispatch(start_message(experiment_id, item))
                        display_number(item)  # Update the display                           
                        if item not in ["Tangram1", "Tangram2", "Tangram3", "Tangram4", "Tangram5"]:
                            start_ticks = pygame.time.get_ticks()
                            loop = True
                            while loop:
                                # Calculate elapsed time in seconds
                                seconds = (pygame.time.get_ticks() - start_ticks) // 1000
                                if item == "baseline1":
                                    if seconds >= 30:
                                        loop = False
                                else:
                                    if seconds >= 60:
                                        loop = False
                            print(f" stop {item}")
                            device_coordinator.dispatch(stop_message(experiment_id, item))
                            device_coordinator.dispatch(save_message(experiment_id))
                            current_index += 1 
                            display_number(f"Next is {blocks[current_index] if current_index < len(blocks) else 'End'}")
                            running = False
                            break
                    if event.key == pygame.K_RETURN:
                        if item in ["Tangram1", "Tangram2", "Tangram3", "Tangram4", "Tangram5"]:
                            print(f" stop {item}")
                            device_coordinator.dispatch(stop_message(experiment_id, item)) 
                            device_coordinator.dispatch(save_message(experiment_id))                   
                            current_index += 1 
                            display_number(f"Next is {blocks[current_index] if current_index < len(blocks) else 'End'}")
                            running = False
                            break
                    if event.key == pygame.K_ESCAPE:  # Check if the key is the scape terminate
                        device_coordinator.dispatch(terminate_message())
                        running = False
                        break
            if not running:
                break
    device_coordinator.dispatch(terminate_message())
    
except KeyboardInterrupt:
    device_coordinator.dispatch(terminate_message())
    print("\nProgram interrupted.")
finally:
    pygame.quit()
