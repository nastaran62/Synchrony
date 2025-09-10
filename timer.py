import pygame
import sys

# Initialize pygame
pygame.init()

# Set up display
width, height = 400, 300
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Pygame Timer Example")

# Set up font
font = pygame.font.SysFont(None, 48)

# Clock to control frame rate
clock = pygame.time.Clock()

# Start time
start_ticks = pygame.time.get_ticks()

# Main loop
running = True
while running:
    screen.fill((255, 255, 255))  # White background

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Calculate elapsed time in seconds
    seconds = (pygame.time.get_ticks() - start_ticks) // 1000

    # Close window when timer reaches 10 seconds
    if seconds >= 10:
        running = False

    # Render the timer (black text)
    timer_text = font.render(f"Time: {seconds}s", True, (0, 0, 0))
    screen.blit(timer_text, (100, 130))

    # Render another message (red text)
    message_text = font.render("Welcome to Pygame!", True, (255, 0, 0))
    screen.blit(message_text, (50, 50))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
