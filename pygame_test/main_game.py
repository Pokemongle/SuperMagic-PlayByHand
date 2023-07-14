from source.states import main_menu, load_screen, level
from source import tools
import hand_detect
import pygame
import multiprocessing
from multiprocessing import Queue


def main_game(msg_queue):
    pygame.init()

    state_dict = {
        'main_menu': main_menu.MainMenu(msg_queue),
        'load_screen': load_screen.LoadScreen(),
        'level': level.Level(msg_queue)
    }
    game = tools.Game(state_dict, 'main_menu')
    game.run()


if __name__ == '__main__':
    msg_queue = Queue()
    # p1 = multiprocessing.Process(target=main_game)
    # p2 = multiprocessing.Process(target=hand_detect.main_hand_detect)
    p1 = multiprocessing.Process(target=main_game, args=(msg_queue,))
    p2 = multiprocessing.Process(target=hand_detect.main_hand_detect, args=(msg_queue,))

    p1.start()
    p2.start()
