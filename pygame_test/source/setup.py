import pygame
from source import constants
from source import tools

pygame.init()
SCREEN = pygame.display.set_mode(constants.SCREEN_SIZE)

GRAPHICS = tools.load_graph('./resources/graphics')

