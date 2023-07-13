import pygame
from .. import constants
from source.components import coin
from source import tools, setup
pygame.font.init()


class Info:
    def __init__(self, state):
        self.state = state
        self.create_state_labels()
        self.create_info_labels()
        self.flash_coin = coin.FlashingCoin()
    def create_state_labels(self):
        """
        方法1：字体->文字->图片
        创建主界面文字信息图片
        :return: None
        """
        self.state_labels = []  # (图片对象，放置位置)
        if self.state == 'main_menu':
            self.state_labels.append((self.create_label('1 PLAYER GAME'), (272, 360)))
            self.state_labels.append((self.create_label('2 PLAYER GAME'), (272, 405)))
            self.state_labels.append((self.create_label('TOP - '), (290, 450)))
            self.state_labels.append((self.create_label('000000'), (400, 450)))
        elif self.state == 'load_screen':
            self.state_labels.append((self.create_label('WORLD'), (280, 200)))
            self.state_labels.append((self.create_label('1 - 1'), (430, 200)))
            self.state_labels.append((self.create_label('X    3'), (380, 280)))
            self.player_image = tools.get_image(setup.GRAPHICS['mario_bros'], 178, 32, 12, 16, (0, 0, 0), constants.BG_MULTI)



    def create_info_labels(self):
        """
        方法1：字体->文字->图片
        创建其它状态文字信息图片
        :return: None
        """
        self.info_labels = []  # (图片对象，放置位置)
        self.info_labels.append((self.create_label('MARIO'), (75, 30)))
        self.info_labels.append((self.create_label('WORLD'), (450, 30)))
        self.info_labels.append((self.create_label('TIME'), (625, 30)))
        self.info_labels.append((self.create_label('000000'), (75, 55)))
        self.info_labels.append((self.create_label('x00'), (300, 55)))
        self.info_labels.append((self.create_label('1 - 1'), (480, 55)))


    def create_label(self, label, size=40, width_scale=1.25, height_scale=1):
        """
        方法1：字体->文字->图片
        :param label: 文字信息的内容
        :param size: 字体大小
        :param width_scale: 宽度放大倍数
        :param height_scale: 高度放大倍数
        :return label_image: 字体图像的Surface对象
        """
        font = pygame.font.SysFont(constants.FONT, size)
        label_image = font.render(label, 1, (255, 255, 255))
        rect = label_image.get_rect()
        label_image = pygame.transform.scale(label_image, (int(rect.width * width_scale),
                                                           int(rect.height * height_scale)))
        return label_image

    def update(self):
        self.flash_coin.update()

    def draw(self, surface):
        for label in self.state_labels:
            surface.blit(label[0], label[1])
        for label in self.info_labels:
            surface.blit(label[0], label[1])
        surface.blit(self.flash_coin.image, self.flash_coin.rect)

        if self.state == 'load_screen':
            surface.blit(self.player_image, (300, 270))