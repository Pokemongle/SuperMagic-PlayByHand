from .. components import info
import pygame


class LoadScreen:
    def __init__(self, msg_queue):
        pass

    def start(self, game_info, msg_queue):
        self.game_info = game_info
        self.msg_queue = msg_queue
        self.duration = 2000
        self.finished = False
        self.next = 'level'
        self.timer = 0
        self.info = info.Info('load_screen', self.game_info)

    def update(self, surface, keys):
        self.draw(surface)
        if self.timer == 0:
            self.timer = pygame.time.get_ticks()
        elif pygame.time.get_ticks() - self.timer > 2000:
            self.finished = True
            self.timer = 0

    def draw(self, surface):
        surface.fill((0, 0, 0))
        self.info.draw(surface)


class GameOver(LoadScreen):
    def __init__(self, game_info, msg_queue):
        LoadScreen.__init__(game_info, msg_queue)
        pass

    def start(self, game_info, msg_queue):
        self.game_info = game_info
        self.msg_queue = msg_queue
        self.finished = False
        self.next = 'main_menu'
        self.duration = 4000
        self.timer = 0
        self.info = info.Info('game_over', self.game_info)


class GameWin(LoadScreen):
    def __init__(self, game_info, msg_queue):
        LoadScreen.__init__(game_info, msg_queue)
        pass

    def start(self, game_info, msg_queue):
        self.game_info = game_info
        self.msg_queue = msg_queue
        self.finished = False
        self.next = 'main_menu'
        self.duration = 4000
        self.timer = 0
        self.info = info.Info('game_win', self.game_info)
