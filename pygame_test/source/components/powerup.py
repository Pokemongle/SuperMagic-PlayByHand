import pygame
from .. import tools, setup
from .. import constants

def create_powerup(centerx, centery, type):
    return Fireflower(centerx, centery)

class Powerup(pygame.sprite.Sprite):
    def __init__(self, centerx, centery, frame_rects):
        pygame.sprite.Sprite.__init__(self)

        self.frames = []
        self.frame_index = 0
        for frame_rect in frame_rects:
            self.frames.append(tools.get_image(setup.GRAPHICS['item_objects'], *frame_rect, (0, 0, 0), constants.TREASURE_MULTI))
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.centerx = centerx
        self.rect.centery = centery
        self.origin_y = centery - self.rect.height / 2

        self.x_vel = 0
        self.direction = 1
        self.y_vel = -1
        self.gravity = constants.GRAVITY
        self.max_y_vel = 8

    def load_frames(self, frame_rects):
        for frame_rect in frame_rects:
            left_frame = tools.get_image(setup.GRAPHICS['enemies'], *frame_rect, (0, 0, 0), constants.ENEMY_MULTI)
            right_frame = pygame.transform.flip(left_frame, True, False)
            self.left_frames.append(left_frame)
            self.right_frames.append(right_frame)

    def update(self, level):
        self.current_time = pygame.time.get_ticks()
        self.handle_states(level)
        self.update_position(level)

    def update_position(self, level):
        self.rect.x += self.x_vel
        self.check_x_collision(level)
        self.rect.y += self.y_vel
        self.check_y_collision(level)
        # 道具跑出屏幕会销毁
        if self.rect.x < 0 or self.rect.y > constants.SCREEN_H:
            self.kill()

    def check_x_collision(self, level):
        sprite = pygame.sprite.spritecollideany(self, level.ground_items_group)
        if sprite:
            # 防止检测x碰撞受y碰撞的干扰
            if self.direction:  # 向右
                self.direction = 0
                self.rect.right = sprite.rect.left
            else:  # 向左
                self.direction = 1
                self.rect.left = sprite.rect.right

            self.x_vel *= -1

    def check_y_collision(self, level):
        check_group = pygame.sprite.Group(level.ground_items_group, level.box_group, level.brick_group)
        sprite = pygame.sprite.spritecollideany(self, check_group)
        if sprite:
            if self.rect.top < sprite.rect.top:
                self.rect.bottom = sprite.rect.top
                self.y_vel = 0
                self.state = 'walk'
        level.check_will_fall(self)


class Mushroom(Powerup):
    def __init__(self, centerx, centery):
        Powerup.__init__(self, centerx, centery, [(0, 0, 16, 16)])
        self.x_vel = 2
        self.state = 'grow'
        self.name = 'mushroom'

    def update(self, level):
        if self.state == 'grow':
            self.rect.y += self.y_vel
            if self.rect.bottom < self.origin_y:
                self.state = 'walk'
        elif self.state == 'walk':
            pass
        elif self.state == 'fall':
            if self.y_vel < self.max_y_vel:
                self.y_vel += self.gravity

        if self.state != 'grow':
            self.update_position(level)


class Fireflower(Powerup):
    def __init__(self, centerx, centery):
        frame_rects = [
            (0, 32, 16, 16),
            (16, 32, 16, 16),
            (32, 32, 16, 16),
            (48, 32, 16, 16),
        ]
        Powerup.__init__(self, centerx, centery, frame_rects)
        self.x_vel = 2
        self.state = 'grow'
        self.name = 'fireflower'
        self.timer = 0

    def update(self, level):
        if self.state == 'grow':
            self.rect.y += self.y_vel
            if self.rect.bottom < self.origin_y:
                self.state = 'rest'

        self.current_time = pygame.time.get_ticks()
        if self.timer == 0:
            self.timer = self.current_time
        elif self.current_time - self.timer > 30:
            self.frame_index += 1
            self.frame_index %= len(self.frames)
            self.timer = self.current_time
            self.image = self.frames[self.frame_index]

class Fireball(Powerup):
    def __init__(self, centerx, centery, direction):
        frame_rects = [
            # 小飞弹
            (96, 144, 8, 8),
            (104, 144, 8, 8),
            (96, 152, 8, 8),
            (104, 152, 8, 8),
            # 爆炸效果
            (112, 144, 16, 16),
            (112, 160, 16, 16),
            (112, 176, 16, 16),
        ]
        Powerup.__init__(self, centerx, centery, frame_rects)
        self.name = 'fireball'
        self.state = 'fly'
        self.direction = direction
        self.x_vel = 10 if self.direction else -10
        self.y_vel = 10
        self.gravity = 1
        self.timer = 0

    def update(self, level):
        self.current_time = pygame.time.get_ticks()
        if self.state == 'fly':
            self.y_vel += self.gravity
            if self.current_time - self.timer > 200:
                self.frame_index += 1
                self.frame_index %= 4
                self.timer = self.current_time
                self.image = self.frames[self.frame_index]
        elif self.state == 'boom':
            if self.current_time - self.timer > 50:
                if self.frame_index < 6:
                    self.frame_index += 1
                    self.timer = self.current_time
                    self.image = self.frames[self.frame_index]
                else:
                    self.kill()

        self.update_position(level)

    def update_position(self, level):
        self.rect.x += self.x_vel
        self.check_x_collision(level)

        self.rect.y += self.y_vel
        self.check_y_collision(level)

        if self.state == 'boom':
            self.rect.x -= self.x_vel
            self.rect.y -= self.y_vel

        # 道具跑出屏幕会销毁
        if self.rect.x < 0 or self.rect.y > constants.SCREEN_H:
            self.kill()

    def check_x_collision(self, level):
        if self.state == 'boom':
            pass
        else:
            # sprite = pygame.sprite.spritecollideany(self, level.ground_items_group)
            # if sprite:
            #     self.frame_index = 4
            #     self.state = 'boom'

            # 检测火球碰撞地面物体
            ground_item = pygame.sprite.spritecollideany(self, level.ground_items_group)
            if ground_item:
                self.frame_index = 4
                self.state = 'boom'
            # 检测火球碰撞敌人
            enemy = pygame.sprite.spritecollideany(self, level.enemy_group)
            if enemy:
                self.frame_index = 4
                self.state = 'boom'
                enemy.go_die('burned')

    def check_y_collision(self, level):
        if self.state == 'boom':
            pass
        else:
            check_group = pygame.sprite.Group(level.ground_items_group, level.box_group, level.brick_group)
            # sprite = pygame.sprite.spritecollideany(self, check_group)
            # if sprite:
            #     if self.rect.top < sprite.rect.top:
            #         self.rect.bottom = sprite.rect.top
            #         self.y_vel = -10

            ground_item = pygame.sprite.spritecollideany(self, level.ground_items_group)
            enemy = pygame.sprite.spritecollideany(self, level.enemy_group)

            if enemy:
                self.state = 'boom'
                enemy.go_die('burned')
            elif ground_item:
                if self.rect.top < ground_item.rect.top:
                    self.rect.bottom = ground_item.rect.top
                    self.y_vel = -10


class LifeMushroom(Powerup):
    pass


class Star(Powerup):
    pass

