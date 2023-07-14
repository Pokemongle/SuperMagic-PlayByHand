from .. components import info, player
import pygame
from .. import tools, setup
from .. import constants

class Level:
    def __init__(self):
        self.info = info.Info('Level')
        self.setup_background()
        self.finished = False
        self.next = None
        self.setup_player()
    def setup_background(self):
        """
                设置背景图像
                :return:
                """
        self.background = setup.GRAPHICS['level_1']
        self.background_rect = self.background.get_rect()  # 设置原始背景图片窗口
        #  背景图片缩放
        self.background = pygame.transform.scale(self.background, (int(self.background_rect.width * constants.BG_MULTI),
                                                                   int(self.background_rect.height * constants.BG_MULTI)))
        self.background_rect = self.background.get_rect()  # 设置缩放后的背景窗口
        # # 设置跟踪窗口
        # self.viewport = setup.SCREEN.get_rect()
        # # 设置标题画面
        # self.caption = tools.get_image(setup.GRAPHICS['title_screen'], 1, 60, 176, 88, (255, 0, 220),
        #                                constants.BG_MULTI)

    def setup_player(self):
        """
        设置人物图像
        :return:
        """
        self.player = player.Player('mario')
        self.player.rect.x = 300
        self.player.rect.y = 300
        self.player_image = tools.get_image(setup.GRAPHICS['mario_bros'], 178, 32, 13, 16, (0, 0, 0), constants.PLAYER_MULTI)

    def update(self, surface, keys):
        self.player.update(keys)
        self.update_player_position()
        self.draw(surface)

    def update_player_position(self):
        self.player.rect.x += self.player.x_vel
        if self.player.rect.y + self.player.y_vel < 490:
            self.player.rect.y += self.player.y_vel
        else:
            self.player.rect.y = 490
    def draw(self, surface):
        surface.blit(self.background, (0, 0))
        surface.blit(self.player.image, self.player.rect)
        self.info.draw(surface)
