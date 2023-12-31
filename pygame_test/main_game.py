from source.states import main_menu, load_screen, level
from source import tools
import hand_detect, brain_detect
import pygame
import multiprocessing
from multiprocessing import Queue


def main_game(msg_queue):
    pygame.init()

    state_dict = {
        'main_menu': main_menu.MainMenu(msg_queue),
        'load_screen': load_screen.LoadScreen(msg_queue),
        'level': level.Level(msg_queue),
        'game_over': load_screen.GameOver([], msg_queue),
        'game_win': load_screen.GameWin([], msg_queue)
    }
    game = tools.Game(state_dict, 'main_menu', msg_queue)
    game.run()


if __name__ == '__main__':
    msg_queue = Queue()
    p1 = multiprocessing.Process(target=main_game, args=(msg_queue,))
    p2 = multiprocessing.Process(target=hand_detect.main_hand_detect, args=(msg_queue,))
    p3 = multiprocessing.Process(target=brain_detect.main_brain, args=(msg_queue,))

    p1.start()
    p2.start()
    p3.start()
