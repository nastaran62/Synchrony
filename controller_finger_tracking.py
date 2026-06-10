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

# p1: Carl tobii1-port1 , com5-20E1 or com11-92D4  Android_EEG_030133
# p2: Zane tobii2-port2 , com4-92F9,  ECL


# Define colors
white = (255, 255, 255)
black = (0, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 128)
window_width = 1500
window_height = 900

BASELKINE_DURATION = 60
TASK_DURATION = 8

def initialize():
    # Initialize Pygame
    pygame.init()

    # Set up the display

    screen = pygame.display.set_mode((window_width, window_height))
    pygame.display.set_caption("Display")

    # Define font
    font = pygame.font.Font(None, 400)
    #font = pygame.font.Font('freesansbold.ttf', 32)


    complex_shapes = ['Octagon', 'Star', 'Octagon', 'Hexagon', 'Hexagon', 'Star', 'Pentagon']
    simple_shapes = ['Circle', 'Square', 'Triangle', 'Rectangle', 'Cross', 'Diamond', 'Oval']
    objects = ["Cloud", "House", "Tree", "Sun", "Mountains", "Leaf", "Car"]

    E1 = ["Baseline1"] + ["Baseline2"] 
    
    E2 = ["Free1", "Free2"]
    random.shuffle(E2)

    E3 = simple_shapes
    random.shuffle(E3)

    E4 = simple_shapes
    random.shuffle(E4)

    E5 = complex_shapes
    random.shuffle(E5)

    E6 = complex_shapes
    random.shuffle(E6)


    E7 = objects
    random.shuffle(E7)

    E8 = objects
    random.shuffle(E8)

    E9 = E3.copy()
    random.shuffle(E9)

    E10 = E4.copy()
    random.shuffle(E10)

    E11 = E5.copy()
    random.shuffle(E11)

    E12 = E6.copy()
    random.shuffle(E12)

    block0_desc = ["E1"]
    block1_desc = ["E2"]
    block2_desc = ["E3", "E4"]
    block3_desc = ["E5", "E6"]
    block4_desc = ["E7", "E8"]
    block5_desc = ["E9", "E10"]
    block6_desc = ["E11", "E12"]
    
    return (screen, font, [[E1], [E2], [E3,E4], [E5, E6], [E7, E8], [E9, E10], [E11, E12]],
                         [block0_desc, block1_desc, block2_desc, block3_desc, block4_desc, block5_desc, block6_desc])

    # Function to display a number

def waiting_for_space():
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Exit if the window is closed
                running = False
                break
            elif event.type == pygame.KEYDOWN:  # Detect key presses        
                if event.key == pygame.K_SPACE:
                    waiting = False
                    break


def get_description(experiment_id):
    if experiment_id == "E1":
        return "Baseline"
    elif experiment_id == "E2":
        return "Free movement"
    elif experiment_id == "E3":
        return "Simple Shapes, p1 leader, p2 folower"
    elif experiment_id == "E4":
        return "Simple Shapes, p2 leader, p1 follower"
    elif experiment_id == "E5":
        return "Complex Shapes, p1 leader, p2 follower"
    elif experiment_id == "E6":
        return "Complex Shapes, p2 leader, p1 follower"
    elif experiment_id == "E7":
        return "Objects, p1 leader, p2 follower"
    elif experiment_id == "E8":
        return "Objects, p2 leader, p1 follower"
    elif experiment_id == "E9":
        return "Simple Shapes, p1 leader, p2 folower"
    elif experiment_id == "E10":
        return "Simple Shapes, p2 leader, p1 follower"
    elif experiment_id == "E11":
        return "Complex Shapes, p1 leader, p2 follower"
    elif experiment_id == "E12":
        return "Complex Shapes, p2 leader, p1 follower"
    

def display(content, screen, font):
    screen.fill(white)  # Clear the screen with white background
    text = font.render(str(content), True, blue)
    text_rect = text.get_rect(center=(window_width // 2, window_height // 2))
    screen.blit(text, text_rect)
    pygame.display.flip()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("block", help="Block number(0, 1, 2, 3, 4, 5, 6), 1 ordered, 2 shuffled", type=int)
    parser.add_argument("pair", help="pair id (p01, p02, ...)", type=str)
    args = parser.parse_args()
    screen, font, blocks, blocks_desc = initialize()

    block_id = args.block
    pair = args.pair
    block = blocks[block_id]
    block_desc = blocks_desc[block_id]

    print(f"Running block {block_id} with pair {pair}")
    print(f"Block description: {block_desc}")


    # Zip them together, shuffle, then unzip
    paired = list(zip(block, block_desc))
    random.shuffle(paired)
    block, block_desc = zip(*paired)
    print(f"Block description: {block_desc}")


    try:
        # Defining sensors
        print("Add devices")
        #muse1 = \
        #    MuseAthenaStreaming("museBE3A", 5700, 256, saving_mode=0, output_path=f"./output/pair{pair}")
        #muse2 = \
        #    MuseAthenaStreaming("museF19E", 5800, 256, saving_mode=0, output_path=f"./output/pair{pair}")
        test_device = TestDeviceStreaming(256, name="TestDevice",saving_mode=0, output_path=f"./pair{pair}")
        
        
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
                                        serial_port="/dev/rfcomm1",
                                        output_path=f"./output/pair{pair}")
            
        tobii1 = TobiiGlassesStreaming("192.168.10.218",
                                       50,
                                       name="tobii1",
                                       saving_mode=0,
                                       output_path=f"./output/pair{pair}")
        tobii2 = TobiiGlassesStreaming("192.168.10.202",
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
        for items in block:
            print(items)
            running = True
            start = False
            rest = False
            print(f"items {items}")
            font = pygame.font.Font(None, 100)
            display(get_description(block_desc[i]), screen, font)  # Display the first item
            experiment_id = block_desc[i]
            waiting_for_space()


            print(f"Experiment ID: {experiment_id}")
            if experiment_id in ["E1", "E2"]:
                rest_index = 1  # For Free1 and Free2
            else:
                rest_index = 9
            current_index = -1
            while running:

                if not start:
                    start = True
                elif not rest:
                    print(f" stop {items[current_index]}, INDEX {current_index}")
                    device_coordinator.dispatch(stop_message(experiment_id, items[current_index]))
                    if (current_index+1)%rest_index == 0 and rest is False:
                        if current_index+1 >= len(items):
                            running = False
                            break
                        rest = True
                        device_coordinator.dispatch(save_message(experiment_id))
                        display("Rest", screen, font)
                        waiting_for_space()
                if current_index+1 >= len(items):
                    running = False
                    break

                rest = False
                display("+", screen, font)
                time.sleep(2)
                print("current_index", current_index)
                font = pygame.font.Font(None, 400)
                display(items[current_index+1], screen, font)  # Update the display
                current_index += 1  # Move to the next number
                if current_index >= len(items):  # Loop back to the start
                    running = False
                    break
                print(f" start {items[current_index]}, INDEX {current_index}")
                device_coordinator.dispatch(start_message(experiment_id, items[current_index]))
                loop = True
                start_ticks = pygame.time.get_ticks()
                if experiment_id in ["E1", "E2"]:
                    while loop:
                        # Calculate elapsed time in seconds
                        seconds = (pygame.time.get_ticks() - start_ticks) // 1000
                        if seconds >= BASELKINE_DURATION:
                            loop = False
                else:
                    while loop:
                        # Calculate elapsed time in seconds
                        seconds = (pygame.time.get_ticks() - start_ticks) // 1000
                        if seconds >= TASK_DURATION:
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