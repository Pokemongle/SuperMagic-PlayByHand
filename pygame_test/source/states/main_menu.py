import pygame
from .. import setup
from .. import tools
from .. import constants
from .. components import info


class MainMenu:
    """
    主菜单
    Boolean finished-主菜单是否结束
    String next-下一阶段
    Info info-主材单信息
    """
    def __init__(self):
        self.setup_background()  # 设置背景
        self.setup_player()  # 设置玩家
        self.setup_cursor()  # 设置光标
        self.finished = False
        self.next = 'load_screen'
        self.cursor.state = '1P'
        self.info = info.Info('main_menu')

    def setup_background(self):
        """
        设置背景图像
        :return:
        """
        self.background = setup.GRAPHICS['level_1']
        self.background_rect = self.background.get_rect()  # 设置背景窗口
        #  背景窗口缩放
        self.background = pygame.transform.scale(self.background, (int(self.background_rect.width * constants.BG_MULTI),
                                                                   int(self.background_rect.height * constants.BG_MULTI)))
        # 设置跟踪窗口
        self.viewport = setup.SCREEN.get_rect()
        # 设置标题画面
        self.caption = tools.get_image(setup.GRAPHICS['title_screen'], 1, 60, 176, 88, (255, 0, 220), constants.BG_MULTI)

    def setup_player(self):
        """
        设置人物图像
        :return:
        """
        self.player_image = tools.get_image(setup.GRAPHICS['mario_bros'], 178, 32, 13, 16, (0, 0, 0), constants.PLAYER_MULTI)


    def setup_cursor(self):
        """
        设置光标图像
        :return:
        """
        self.cursor = pygame.sprite.Sprite()
        self.cursor.image = tools.get_image(setup.GRAPHICS['item_objects'], 24, 160, 8, 8, (0, 0, 0), constants.PLAYER_MULTI)
        rect = self.cursor.image.get_rect()
        rect.x, rect.y = (220, 360)
        self.cursor.rect = rect

    def update_cursor(self, keys):
        if keys[pygame.K_UP]:
            self.cursor.state = '1P'
            self.cursor.rect.y = 360
        elif keys[pygame.K_DOWN]:
            self.cursor.state = '2P'
            self.cursor.rect.y = 405
        elif keys[pygame.K_RETURN]:
            if self.cursor.state == '1P':
                self.finished = True
            elif self.cursor.state == '2P':
                self.finished = True

    def update(self, surface, keys):
        """
        菜单更新，原理为重新按顺序在屏幕上“画”每个组件的图像
        :param surface:
        :return:
        """
        # surface.fill((random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
        surface.blit(self.background, self.viewport)
        surface.blit(self.caption, (170, 100))
        surface.blit(self.player_image, (110, 490))
        surface.blit(self.cursor.image, self.cursor.rect)

        self.update_cursor(keys)
        self.info.update()
        self.info.draw(surface)
