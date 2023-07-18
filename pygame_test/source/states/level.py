from .. components import info, player, stuff, brick, box, enemy
import pygame
from .. import tools, setup
from .. import constants
import os
import json


class Level:
    def __init__(self, msg_queue):
        pass

    def start(self, game_info, msg_queue):
        self.game_info = game_info
        self.finished = False
        self.next = 'game_over'
        self.info = info.Info('level', self.game_info)
        self.msg_queue = msg_queue
        self.msg = ''

        self.load_map_data()
        self.setup_background()
        self.setup_bricks_boxes()
        self.setup_checkpoints()
        self.setup_enemies()
        self.setup_ground_items()
        self.setup_start_position()
        self.setup_player()

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

    def setup_bricks_boxes(self):
        """
        添加场景中的砖块和宝箱（精灵类）
        :return:
        """
        # 添加砖块
        self.brick_group = pygame.sprite.Group()
        # 添加宝箱
        self.box_group = pygame.sprite.Group()
        # 添加金币
        self.coin_group = pygame.sprite.Group()
        # 添加功能性道具
        self.powerup_group = pygame.sprite.Group()

        if 'brick' in self.map_data:
            for brick_data in self.map_data['brick']:
                x, y = brick_data['x'], brick_data['y']
                brick_type = brick_data['type']
                if brick_type == 0:
                    if 'brick_num' in brick_data:  # 批量处理砖块
                        # TODO batch bricks
                        pass
                    else:
                        self.brick_group.add(brick.Brick(x, y, brick_type, None))
                elif brick_type == 1:
                    self.brick_group.add(brick.Brick(x, y, brick_type, self.coin_group))
                else:
                    self.brick_group.add(brick.Brick(x, y, brick_type, self.powerup_group))

        if 'box' in self.map_data:
            for box_data in self.map_data['box']:
                x, y = box_data['x'], box_data['y']
                box_type = box_data['type']
                if box_type == 1:
                    self.box_group.add(box.Box(x, y, box_type, self.coin_group))
                elif box_type == 2 or box_type == 3:
                    self.box_group.add(box.Box(x, y, box_type, self.powerup_group))
                else:
                    self.box_group.add(box.Box(x, y, box_type))





    def setup_checkpoints(self):
        self.checkpoint_group = pygame.sprite.Group()
        for item in self.map_data['checkpoint']:
            x, y, w, h = item['x'], item['y'], item['width'], item['height']
            checkpoint_type = item['type']
            enemy_groupid = item.get('enemy_groupid')
            self.checkpoint_group.add(stuff.Checkpoint(x, y, w, h, checkpoint_type, enemy_groupid))

    def setup_enemies(self):
        """
        设置敌人
        :return: None
        """
        self.dying_group = pygame.sprite.Group()
        self.shell_group = pygame.sprite.Group()
        self.enemy_group = pygame.sprite.Group()
        self.enemy_group_dict = {}  # 组数:精灵组
        for enemy_group_data in self.map_data['enemy']:
            group = pygame.sprite.Group()
            for enemy_group_id, enemy_list in enemy_group_data.items():
                for enemy_data in enemy_list:
                    group.add(enemy.create_enemy(enemy_data))
                self.enemy_group_dict[enemy_group_id] = group

    def setup_player(self):
        """
        设置人物图像
        :return: None
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

    def is_frozen(self):
        return self.player.state in ['small2big', 'big2small', 'big2fire', 'fire2small', ]

    def update(self, surface, keys):
        self.current_time = pygame.time.get_ticks()
        # 接收手势信号
        self.msg = self.msg_queue.get() if not self.msg_queue.empty() else self.msg
        self.player.update(keys, self.msg, self)
        if self.player.dead:
            if self.current_time - self.player.death_timer > 3000:
                self.finished = True
                self.update_game_info()
        elif self.is_frozen():
            pass
        else:
            self.update_player_position()
            self.check_checkpoints()
            self.check_if_go_die()
            self.update_game_window()
            self.info.update(self.msg)
            self.brick_group.update()
            self.box_group.update()
            self.enemy_group.update(self)
            self.dying_group.update(self)
            self.shell_group.update(self)
            self.coin_group.update(self)
            self.powerup_group.update(self)

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
        if not self.player.dead:
            self.player.rect.y += self.player.y_vel
            self.check_y_collisions()

    def check_x_collisions(self):
        # x方向碰撞检测
        check_group = pygame.sprite.Group(self.ground_items_group, self.brick_group, self.box_group)
        # 检查水平方向人物是否与精灵组中的任何一个精灵发生碰撞， 返回与马里奥碰撞的第一个精灵， 什么都没有就返回空
        collided_sprite = pygame.sprite.spritecollideany(self.player, check_group)
        if collided_sprite:
            self.adjust_player_x(collided_sprite)

        if self.player.hurt_immune:
            return

        # 检测水平方向人物是否与敌人相撞
        enemy = pygame.sprite.spritecollideany(self.player, self.enemy_group)
        if enemy:  # 人物死亡
            if ((not self.player.fire) and self.player.big):
                self.player.state = 'big2small'
                self.player.hurt_immune = True
            elif self.player.fire and self.player.big:
                self.player.state = 'fire2big'
                self.player.hurt_immune = True
            else:
                self.player.go_die()

        # 检测水平方向 人物与龟壳 是否相撞
        shell = pygame.sprite.spritecollideany(self.player, self.shell_group)
        if shell:  # 撞到龟壳
            if shell.state == 'slide':
                self.player.go_die()
            else:
                if self.player.rect.x < shell.rect.x:
                    shell.x_vel = 10  # 龟壳弹开加速度
                    shell.rect.x += 40  # 直接弹开，防止撞到人物
                    shell.direction = 1  # 龟壳向右弹开
                else:
                    shell.x_vel = -10
                    shell.rect.x -= 40
                    shell.direction = 0
                shell.state = 'slide'

        powerup = pygame.sprite.spritecollideany(self.player, self.powerup_group)
        if powerup:
            if powerup.name == 'fireball':
                pass
            if powerup.name == 'mushroom':
                self.player.state = 'small2big'
                powerup.kill()
            elif powerup.name == 'fireflower':
                self.player.state = 'big2fire'
                powerup.kill()

    def check_y_collisions(self):
        ground_item = pygame.sprite.spritecollideany(self.player, self.ground_items_group)
        brick = pygame.sprite.spritecollideany(self.player, self.brick_group)
        box = pygame.sprite.spritecollideany(self.player, self.box_group)
        enemy = pygame.sprite.spritecollideany(self.player, self.enemy_group)

        # 检测人物离砖块还是宝箱更近
        if brick and box:
            to_brick = abs(self.player.rect.x - brick.rect.centerx)
            to_box = abs(self.player.rect.x - box.rect.centerx)
            if to_brick <= to_box:
                box = None
            else:
                brick = None

        # 与地面碰撞
        if ground_item:
            self.adjust_player_y(ground_item)
        elif brick:
            self.adjust_player_y(brick)
        elif box:
            self.adjust_player_y(box)
        elif enemy:
            if self.player.hurt_immune:
                return

            if self.player.y_vel < 0:
                self.enemy_group.remove(enemy)
                self.dying_group.add(enemy)
                how = 'bumped'
                # 敌人不同的死法
                enemy.go_die(how, 1 if self.player.face_right else -1)
            elif self.player.y_vel > 0:
                self.enemy_group.remove(enemy)
                # 将乌龟加入龟壳组
                if enemy.name == 'koopa':
                    self.shell_group.add(enemy)
                else:
                    self.dying_group.add(enemy)
                self.dying_group.add(enemy)
                how = 'trampled'
                self.player_state = 'jump'
                self.player.rect.bottom = enemy.rect.top
                self.player.y_vel = self.player.jump_vel * 0.8
                # 敌人不同的死法
                enemy.go_die(how,  1 if self.player.face_right else -1)
            else:
                pass

        self.check_will_fall(self.player)

    def check_if_go_die(self):
        if self.player.rect.y > constants.SCREEN_H:
            self.player.go_die()

    def check_checkpoints(self):
        checkpoint = pygame.sprite.spritecollideany(self.player, self.checkpoint_group)
        if checkpoint:
            if checkpoint.checkpoint_type == 0:  # 敌人出现检查点
                self.enemy_group.add(self.enemy_group_dict[str(checkpoint.enemy_groupid)])
            checkpoint.kill()

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
        # 一切都是由碰撞引起的
        # 下落
        if self.player.rect.bottom < sprite.rect.bottom:
            self.player.y_vel = 0
            self.player.rect.bottom = sprite.rect.top
            self.player.state = 'walk'
        # 上升
        else:
            self.player.y_vel = 7  # 反弹速度
            self.player.rect.top = sprite.rect.bottom
            self.player.state = 'fall'

            self.is_enemy_on(sprite)

            if sprite.name == 'box':
                if sprite.state == 'rest':
                    sprite.go_bumped()
            if sprite.name == 'brick':
                if self.player.big and sprite.brick_type == 0:
                    sprite.smashed(self.dying_group)
                else:
                    sprite.go_bumped()

    def is_enemy_on(self, sprite):
        sprite.rect.y -= 1
        enemy = pygame.sprite.spritecollideany(sprite, self.enemy_group)
        if enemy:
            self.enemy_group.remove(enemy)
            self.dying_group.add(enemy)
            # 撞击方向优化
            if sprite.rect.centerx > enemy.rect.centerx:
                direction = -1
            else:
                direction = 1
            enemy.go_die('bumped', direction)
        sprite.rect.y += 1


    def check_will_fall(self, sprite):
        sprite.rect.y += 1
        check_group = pygame.sprite.Group(self.ground_items_group, self.brick_group, self.box_group)
        collided_sprite = pygame.sprite.spritecollideany(sprite, check_group)
        if not collided_sprite and sprite.state != 'jump' and not self.is_frozen():
            sprite.state = 'fall'
        sprite.rect.y -= 1

    def update_game_window(self):
        third = self.game_window.x + self.game_window.width / 3
        # 不可以走回头路
        # if self.player.x_vel > 0 and self.player.rect.centerx > third and self.game_window.right < self.end_x:
        if self.game_window.right < self.end_x:  # 可以走回头路
            self.game_window.x += self.player.x_vel
            self.start_x = self.game_window.x

    def update_game_info(self):
        if self.player.dead:
            self.game_info['lives'] -= 1
        if self.game_info['lives'] == 0:
            self.next = 'game_over'
        else:
            self.next = 'load_screen'

    def draw(self, surface):
        # 参数1：要将self.background画到self.game_ground图层上
        # 参数2：game_window(rect)中有(x,y,width,height)四个数据，将self.background画到self.game_ground图层的(x,y)位置
        # 参数3：从self.background上的(x,y)位置抠下宽度为width，高度为height大小的图像
        # 目的大概是将游戏背景单独作为一个图层，和马里奥的人物图层隔离
        self.game_ground.blit(self.background, self.game_window, self.game_window)
        self.game_ground.blit(self.player.image, self.player.rect)
        self.coin_group.draw(self.game_ground)
        self.powerup_group.draw(self.game_ground)
        self.brick_group.draw(self.game_ground)
        self.box_group.draw(self.game_ground)
        self.enemy_group.draw(self.game_ground)
        self.dying_group.draw(self.game_ground)
        self.shell_group.draw(self.game_ground)

        surface.blit(self.game_ground, (0, 0), self.game_window)
        self.info.draw(surface)

