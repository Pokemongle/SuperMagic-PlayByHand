import pygame
from .. import tools, setup
from .. import constants
from .powerup import create_powerup

class Box(pygame.sprite.Sprite):
    def __init__(self, x, y, box_type, group=None, name='box'):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.box_type = box_type  # 宝箱类型
        self.name = name
        self.group = group
        # 宝箱帧图像在总图像的位置，用于抠图
        self.frame_rects = {
            (384, 0, 16, 16),
            (400, 0, 16, 16),
            (416, 0, 16, 16),
            (432, 0, 16, 16),
        }
        self.frames = []
        for frame_rect in self.frame_rects:
            self.frames.append(tools.get_image(setup.GRAPHICS['tile_set'], *frame_rect, (0, 0, 0), constants.BRICK_MULTI))
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

        self.gravity = constants.GRAVITY
        self.state = 'rest'
        self.timer = 0

    def update(self, level):
        self.current_time = pygame.time.get_ticks()
        self.handle_states(level)

    def handle_states(self, level):
        if self.state == 'rest':
            self.rest()
        elif self.state == 'bumped':
            self.bumped(level.player)
        elif self.state == 'open':
            self.open()

    def go_bumped(self):
        self.y_vel = -7
        self.state = 'bumped'

    def rest(self):
        # 宝箱闪烁效果
        frame_durations = [400, 100, 100, 50]
        if self.current_time - self.timer > frame_durations[self.frame_index]:
            self.frame_index = (self.frame_index + 1) % 4
            self.timer = self.current_time
        self.image = self.frames[self.frame_index]

    def bumped(self, player):
        self.rect.y += self.y_vel
        self.y_vel += self.gravity
        self.frame_index = 3
        self.image = self.frames[self.frame_index]
        if self.rect.y > self.y + 5:
            self.rect.y = self.y
            self.state = 'open'
            # box_type 0, 1, 2, 3 对应 空，金币，星星，蘑菇/ 火花
            if self.box_type == 1:
                pass
            elif self.box_type == 2:
                pass
            elif self.box_type == 3:
                self.group.add(create_powerup(self.rect.centerx, self.rect.centery, self.box_type, player))

    def open(self):
        self.frame_index = 1
        self.image = self.frames[self.frame_index]
