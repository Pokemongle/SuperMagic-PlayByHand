# 游戏主要入口
<<<<<<< HEAD
from source import setup
from source.states import main_menu, load_screen, level

from source import tools
=======
from . source import setup
from . source.states import main_menu, load_screen, level

from . source import tools
>>>>>>> feature01_handmove


def main():
    state_dict = {
        'main_menu': main_menu.MainMenu(),
        'load_screen': load_screen.LoadScreen(),
        'level': level.Level()
    }
    game = tools.Game(state_dict, 'main_menu')
    game.run()


if __name__ == '__main__':
    main()
