from .. components import info, player, stuff
import pygame
from .. import tools, setup
from .. import constants
import os
import json


class Level:
    def __init__(self, msg_queue):
        self.info = info.Info('Level')
        self.finished = False
        self.next = 'main_menu'
        self.load_map_data()
        self.setup_start_position()
        self.setup_background()
        self.setup_player()
        self.setup_ground_items()
        self.msg_queue = msg_queue
        self.msg = '无'

    def load_map_data(self):
        file_name = 'level_1.json'
        file_path = os.path.join('source/data/maps', file_name)
        with open(file_path) as f:
            self.map_data = json.load(f)

    def setup_background(self):
        """
        设置背景图像
        :return:
        """
        self.image_name = self.map_data['image_name']
        self.background = setup.GRAPHICS[self.image_name]
        self.background_rect = self.background.get_rect()  # 设置原始背景图片窗口
        #  背景图片缩放
        self.background = pygame.transform.scale(self.background, (int(self.background_rect.width * constants.BG_MULTI),
                                                                   int(self.background_rect.height * constants.BG_MULTI)))
        self.background_rect = self.background.get_rect()  # 设置缩放后的背景窗口
        # 设置跟踪窗口
        self.game_window = setup.SCREEN.get_rect()
        self.game_ground = pygame.Surface((self.background_rect.width, self.background_rect.height))

    def setup_player(self):
        """
        设置人物图像
        :return:
        """
        self.player = player.Player('mario')
        self.player.rect.x = self.game_window.x + self.player_x
        self.player.rect.bottom = self.player_y
        self.player_image = tools.get_image(setup.GRAPHICS['mario_bros'], 178, 32, 13, 16, (0, 0, 0),
                                            constants.PLAYER_MULTI)

    def setup_ground_items(self):
        self.ground_items_group = pygame.sprite.Group()
        for name in ['ground', 'pipe', 'step']:
            for item in self.map_data[name]:
                self.ground_items_group.add(stuff.Item(item['x'], item['y'], item['width'], item['height'], name))

    def setup_start_position(self):
        self.positions = []
        for data in self.map_data['maps']:
            self.positions.append((data['start_x'], data['end_x'], data['player_x'], data['player_y']))
        self.start_x, self.end_x, self.player_x, self.player_y = self.positions[0]

    def update(self, surface, keys):
        self.current_time = pygame.time.get_ticks()
        self.msg = self.msg_queue.get() if not self.msg_queue.empty() else self.msg
        self.player.update(keys, self.msg)
        if self.player.dead:
            if self.current_time - self.player.death_timers > 3000:
                self.__init__(self.msg_queue)
                self.finished = True

        else:
            self.update_player_position()
            self.check_if_go_die()
            self.update_game_window()
        self.draw(surface)

    def update_player_position(self):

        # x position
        # 限制人物跑动不超出窗口
        self.player.rect.x += self.player.x_vel
        if self.player.rect.x < self.start_x:
            self.player.rect.x = self.start_x
        elif self.player.rect.right > self.end_x:
            self.player.rect.right = self.end_x
        self.check_x_collisions()

        # y position
        self.player.rect.y += self.player.y_vel
        self.check_y_collisions()

    def check_x_collisions(self):
        # 检查水平方向人物是否与精灵组中的任何一个精灵发生碰撞， 返回与马里奥碰撞的第一个精灵， 什么都没有就返回空
        ground_item = pygame.sprite.spritecollideany(self.player, self.ground_items_group)
        if ground_item:
            self.adjust_player_x(ground_item)

    def check_y_collisions(self):
        # 检查竖直方向人物是否与精灵组中的任何一个精灵发生碰撞， 返回与马里奥碰撞的第一个精灵， 什么都没有就返回空
        ground_item = pygame.sprite.spritecollideany(self.player, self.ground_items_group)
        if ground_item:
            self.adjust_player_y(ground_item)
        self.check_will_fall(self.player)

    def check_if_go_die(self):
        if self.player.rect.y > constants.SCREEN_H:
            self.player.go_die()

    def adjust_player_x(self, sprite):
        """
        x方向碰撞检测操作
        :param sprite: 人物碰撞到的物体
        :return: None
        """
        if self.player.rect.x < sprite.rect.x:
            self.player.rect.right = sprite.rect.left
        else:
            self.player.rect.left = sprite.rect.right
        self.player.x_vel = 0

    def adjust_player_y(self, sprite):
        """
        y方向碰撞检测操作
        :param sprite: y方向碰撞到的物体
        :return: None
        """
        # 下落
        if self.player.rect.bottom < sprite.rect.bottom:
            self.player.y_vel = 0
            self.player.rect.bottom = sprite.rect.top
            self.player.state = 'walk'
        # 上升
        else:
            self.player.y_vel = 7   # 反弹速度
            self.player.rect.top = sprite.rect.bottom
            self.player.state = 'fall'

    def check_will_fall(self, sprite):
        sprite.rect.y += 1
        check_group = pygame.sprite.Group(self.ground_items_group)
        collided = pygame.sprite.spritecollideany(sprite, check_group)
        if not collided and sprite.state != 'jump':
            sprite.state = 'fall'
        sprite.rect.y -= 1

    def update_game_window(self):
        third = self.game_window.x + self.game_window.width / 3
        # 不可以走回头路
        # if self.player.x_vel > 0 and self.player.rect.centerx > third and self.game_window.right < self.end_x:
        if self.game_window.right < self.end_x:  # 可以走回头路
            self.game_window.x += self.player.x_vel
            self.start_x = self.game_window.x

        # self.game_window.x += self.player.x_vel

    def draw(self, surface):
        # 参数1：要将self.background画到self.game_fround图层上
        # 参数2：game_window(rect)中有(x,y,width,height)四个数据，将self.background画到self.game_ground图层的(x,y)位置
        # 参数3：从self.background上的(x,y)位置抠下宽度为width，高度为height大小的图像
        # 目的大概是将游戏背景单独作为一个图层，和马里奥的人物图层隔离
        self.game_ground.blit(self.background, self.game_window, self.game_window)
        self.game_ground.blit(self.player.image, self.player.rect)
        surface.blit(self.game_ground, (0, 0), self.game_window)
        self.info.draw(surface)
