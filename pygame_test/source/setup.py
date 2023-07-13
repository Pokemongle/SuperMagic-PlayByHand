import pygame
from . import constants
from . import tools

pygame.init()
SCREEN = pygame.display.set_mode(constants.SCREEN_SIZE)

GRAPHICS = tools.load_graph('./resources/graphics')

