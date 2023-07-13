import pygame
from sources import setup
from sources import tools


class MainMenu:
    """
    主菜单
    """
    def __init__(self):
        self.setup_background()  # 设置背景
        self.setup_player()  # 设置玩家
        self.setup_cursor()  # 设置光标

    def setup_background(self):
        self.background = setup.GRAPHICS['']

    def setup_player(self):
        pass

    def setup_cursor(self):
        pass

    def update(self, surface):
        import random
        surface.fill((random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
