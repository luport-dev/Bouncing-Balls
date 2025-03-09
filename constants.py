import pygame

# Initialize Pygame
pygame.init()

# Get screen info
screen_info = pygame.display.Info()
HEIGHT = int(screen_info.current_h * 0.6)  # 60% of the screen height
WIDTH = int(HEIGHT * 4/3)  # 4:3 ratio based on the height

# Constants
FPS = 60
BALL_SPEED = 7 

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
COLORS = [
    (255, 0, 0),    # Red
    (0, 255, 0),    # Green
    (0, 0, 255),    # Blue
    (255, 255, 0),  # Yellow
    (255, 0, 255),  # Magenta
    (0, 255, 255)   # Cyan
]