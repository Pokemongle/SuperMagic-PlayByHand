import pygame
from . import constants, tools

# pygame.init()
SCREEN = pygame.display.set_mode(constants.SCREEN_SIZE)
# GRAPHICS = tools.load_graph('D:/Code_files/shortterm/tests/demo1_test/Sorcerer/pygame_test/resources/graphics')
GRAPHICS = tools.load_graph('./resources/graphics')

