import pygame
from .. import tools, setup
from .. import constants
from .powerup import create_powerup


class Brick(pygame.sprite.Sprite):
    def __init__(self, x, y, brick_type, group=None, color=None, name='brick'):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.brick_type = brick_type
        self.group = group
        self.color = color
        self.name = name
        bright_frame_rects = [(16, 0, 16, 16), (48, 0, 16, 16)]
        dark_frame_rects = [(16, 32, 16, 16), (48, 32, 16, 16)]
        if not color:
            self.frame_rects = bright_frame_rects
        else:
            self.frame_rects = dark_frame_rects
        self.frames = []
        for frame_rect in self.frame_rects:
            self.frames.append(tools.get_image(setup.GRAPHICS['tile_set'], *frame_rect, (0, 0, 0), constants.BRICK_MULTI))
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y
        self.timer = 0
        self.gravity = constants.GRAVITY
        self.state = 'rest'

    def update(self):
        self.current_time = pygame.time.get_ticks()
        self.handle_states()

    def handle_states(self):
        if self.state == 'rest':
            self.rest()
        elif self.state == 'bumped':
            self.bumped()

    def go_bumped(self):
        self.y_vel = -7
        self.state = 'bumped'

    def rest(self):
        pass

    def bumped(self):
        self.rect.y += self.y_vel
        self.y_vel += self.gravity

        if self.rect.y > self.y + 10:
            self.rect.y = self.y
            if self.brick_type == 0:
                self.state = 'rest'
            elif self.brick_type == 1:
                self.state = 'open'
            else:
                self.group.add(create_powerup(self.rect.centerx, self.rect.centery, self.brick_type))

    def open(self):
        self.frame_index = 1
        self.image = self.frames[self.frame_index]

    def smashed(self, group):
        # x, y, x_vel, y_vel
        debris = [
            (self.rect.x, self.rect.y, -2, -10),
            (self.rect.x, self.rect.y, 2, -10),
            (self.rect.x, self.rect.y, -2, -5),
            (self.rect.x, self.rect.y, 2, -5),
        ]
        for d in debris:
            group.add(Debris(*d))
        self.kill()


class Debris(pygame.sprite.Sprite):
    def __init__(self, x, y, x_vel, y_vel):
        pygame.sprite.Sprite.__init__(self)
        self.image = tools.get_image(setup.GRAPHICS['tile_set'], 68, 20, 8, 8, (0, 0, 0), constants.BRICK_MULTI)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.x_vel = x_vel
        self.y_vel = y_vel
        self.gravity = constants.GRAVITY

    def update(self, *args):
        self.rect.x += self.x_vel
        self.rect.y += self.y_vel
        self.y_vel += self.gravity
        if self.rect.y > constants.SCREEN_H:
            self.kill()


