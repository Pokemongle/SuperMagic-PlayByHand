import pygame
from .. import tools
from ..setup import GRAPHICS
from .. import constants
from ..components import powerup
import json
import os


class Player(pygame.sprite.Sprite):
    def __init__(self, name):
        pygame.sprite.Sprite.__init__(self)
        self.name = name  # 玩家名字
        self.load_data()  # 载入玩家json文件
        self.load_images()  # 载入动画帧图像
        self.setup_states()  # 初始化玩家状态
        self.setup_velocities()  # 玩家初始速度设定
        self.setup_timers()  # 初始化动画帧计时器
        self.msg = ''  # 手势控制信号
        self.msg_control_move = ''
        self.msg_control_jump = ''
        self.msg_control_special = ''
        self.msg_control_fire = 0.0

    def load_data(self):
        """
        加载人物对应的文件，给人物命名时要选择source/data 中已有的json文件名称
        json文件中的数据保存在self.player_data中
        :return: None
        """
        file_name = self.name + '.json'  # 根据玩家名拼接json文件名， 如生成的玩家为luigi, file_name = luigi.json
        file_path = os.path.join('source/data/player', file_name)  # 生成json文件对应的路径
        with open(file_path) as f:
            self.player_data = json.load(f)  # 加载json文件中保存的玩家数据

    def setup_states(self):
        """
        初始化玩家状态
        :return: None
        """
        self.state = 'stand'
        self.face_right = True
        self.dead = False
        self.big = False
        self.fire = False
        self.can_jump = True
        self.can_shoot = True
        self.hurt_immune = False
        self.ate_mushroom = False

    def setup_velocities(self):
        """
        初始化玩家速度
        :return: None
        """
        speed = self.player_data['speed']
        self.x_vel = 0
        self.y_vel = 0
        self.max_walk_vel = speed['max_walk_speed']
        self.max_run_vel = speed['max_run_speed']
        self.jump_vel = speed['jump_velocity']
        self.max_y_vel = speed['max_y_velocity']
        self.walk_accel = speed['walk_accel']
        self.run_accel = speed['run_accel']
        self.turn_accel = speed['turn_accel']
        self.gravity = constants.GRAVITY
        self.anti_gravity = constants.ANTI_GRAVITY
        self.max_x_vel = self.max_walk_vel
        self.x_accel = self.walk_accel

    def setup_timers(self):
        """
        初始化动画计时器
        :return:
        """
        self.walking_timer = 0
        self.translation_timer = 0
        self.death_timer = 0
        self.hurt_immune_timer = 0
        self.last_fireball_timer = 0

    def load_images(self):
        """
        根据 name.json 文件中的数据加载动画帧
        :return: None
        """
        sheet = GRAPHICS['harry']  # 取图片库中的一张图片
        frame_rects = self.player_data['image_frames']  # 从json文件中读取所有的帧数据, key: 动画组名, value: 帧坐标数据
        # 动画帧分组，见名知意
        self.right_small_normal_frames = []
        self.right_big_normal_frames = []
        self.right_big_fire_frames = []
        self.left_small_normal_frames = []
        self.left_big_normal_frames = []
        self.left_big_fire_frames = []
        # 遍历保存所有帧数据的字典，加载所有的底层动画帧组
        for group, group_frame_rects in frame_rects.items():
            for frame_rect in group_frame_rects:
                right_image = tools.get_image(sheet, frame_rect['x'], frame_rect['y'],
                                              frame_rect['width'], frame_rect['height'],
                                              (103, 167, 141), constants.PLAYER_MULTI)
                left_image = pygame.transform.flip(right_image, True, False)
                if group == 'right_small_normal':
                    self.right_small_normal_frames.append(right_image)
                    self.left_small_normal_frames.append(left_image)
                if group == 'right_big_normal':
                    self.right_big_normal_frames.append(right_image)
                    self.left_big_normal_frames.append(left_image)
                if group == 'right_big_fire':
                    self.right_big_fire_frames.append(right_image)
                    self.left_big_fire_frames.append(left_image)
        # 归纳一层，小、大、大开火三种状态的动画帧
        self.small_normal_frames = [self.right_small_normal_frames, self.left_small_normal_frames]
        self.big_normal_frames = [self.right_big_normal_frames, self.left_big_normal_frames]
        self.big_fire_frames = [self.right_big_fire_frames, self.left_big_fire_frames]
        # 全体动画集合
        self.all_frames = [
            self.right_small_normal_frames,
            self.right_big_normal_frames,
            self.right_big_fire_frames,
            self.left_small_normal_frames,
            self.left_big_normal_frames,
            self.left_big_fire_frames,
        ]
        # 默认的向左和向右移动的动画
        self.right_frames = self.right_small_normal_frames
        self.left_frames = self.left_small_normal_frames
        self.frame_index = 0  # 默认的开始动画帧序号
        self.frames = self.right_frames  # 默认的开始动画组
        self.image = self.frames[self.frame_index]  # 截取初始动画帧图像
        self.rect = self.image.get_rect()  # 获取图像大小

    def update(self, keys, msg, level):
        """
        更新人物位置和状态
        :param keys: 获取的系统键盘按键列表
        :param msg: 手势信号队列
        :return: None
        """
        if msg == '左' or msg == '右' or msg == '中':
            self.msg_control_move = msg

        if msg == '跳' or msg == '无':
            self.msg_control_jump = msg

        if msg == '攻' or msg == '无':
            self.msg_control_special = msg

        if isinstance(msg, float):  # 读取脑电信号
            self.msg_control_fire = msg

        self.current_time = pygame.time.get_ticks()  # 读取当前时间
        self.handle_states(keys, level)
        self.is_hurt_immune()

    def handle_states(self, keys, level):
        """
        人物状态机
        :param keys: 键盘输入
        :return:
        """
        # 传送点
        self.can_jump_or_not(keys)
        self.can_shoot_or_not(keys)

        if self.state == 'stand':
            self.stand(keys, level)
        elif self.state == 'walk':
            self.walk(keys, level)
        elif self.state == 'jump':
            self.jump(keys, level)
        elif self.state == 'fall':
            self.fall(keys, level)
        elif self.state == 'die':
            self.die(keys, level)
        elif self.state == 'small2big':
            self.small2big(keys, level)
        elif self.state == 'big2small':
            self.big2small(keys, level)
        elif self.state == 'big2fire':
            self.big2fire(keys, level)
        elif self.state == 'fire2big':
            self.fire2big(keys, level)

        if self.face_right:
            self.image = self.right_frames[self.frame_index]
        else:
            self.image = self.left_frames[self.frame_index]

    def can_jump_or_not(self, keys):
        if not ((keys[pygame.K_SPACE]) or (self.msg_control_jump == '跳')):
            self.can_jump = True

    def can_shoot_or_not(self, keys):
        if not ((keys[pygame.K_RSHIFT]) or (self.msg_control_jump == '攻')):
            self.can_shoot = True

    def stand(self, keys, level):
        """
        站立状态
        :param keys:
        :return:
        """
        self.frame_index = 0  # 第0帧为站立状态

        # 状态切换
        if keys[pygame.K_RIGHT] or self.msg_control_move == '右':
            self.face_right = True
            self.state = 'walk'
        elif keys[pygame.K_LEFT] or self.msg_control_move == '左':
            self.face_right = False
            self.state = 'walk'
        if ((keys[pygame.K_SPACE]) or (self.msg_control_jump == '跳')) and self.can_jump:
            self.state = 'jump'
            self.y_vel = self.jump_vel
        if (keys[pygame.K_RSHIFT] or self.msg_control_special == '攻') and self.msg_control_fire >= constants.FIRE_CONTROL:
            if self.fire and self.can_shoot:
                self.shoot_fireball(level)

    def walk(self, keys, level):
        """
        走路状态
        :param keys:
        :return:
        """
        # 按住左shift + 方向键可以冲刺
        if keys[pygame.K_LSHIFT]:
            self.max_x_vel = self.max_run_vel
            self.x_accel = self.run_accel
        else:
            self.max_x_vel = self.max_walk_vel
            self.x_accel = self.walk_accel
        # 控制人物跳跃
        if ((keys[pygame.K_SPACE]) or (self.msg_control_jump == '跳')) and self.can_jump:
            self.state = 'jump'
            self.y_vel = self.jump_vel

        if (keys[pygame.K_RSHIFT] or self.msg_control_special == '攻') and self.msg_control_fire >= constants.FIRE_CONTROL:
            if self.fire and self.can_shoot:
                self.shoot_fireball(level)

        # 动画帧更新
        if self.current_time - self.walking_timer > self.calc_frame_duration():
            if self.frame_index < 8:
                self.frame_index += 1
            else:
                self.frame_index = 0
            self.walking_timer = self.current_time

        # 控制人物向右移动
        if keys[pygame.K_RIGHT] or self.msg_control_move == '右':
            self.face_right = True
            self.frames = self.right_frames
            # 加速度系统
            if self.x_vel < 0:  # 按右键时人物在向左运动，则减速
                self.frame_index = 3  # 急停刹车为第3帧
                self.x_accel = self.turn_accel
            # 根据当前速度，加速度，最大速度计算下一步的速度
            self.x_vel = self.calc_vel(self.x_vel, self.x_accel, self.max_x_vel, True)
        # 控制人物向左运动
        elif keys[pygame.K_LEFT] or self.msg_control_move == '左':
            self.face_right = False
            self.frames = self.left_frames
            if self.x_vel > 0:
                self.frame_index = 3
                self.x_accel = self.turn_accel
            self.x_vel = self.calc_vel(self.x_vel, self.x_accel, self.max_x_vel, False)
        # 无按键控制或手势响应，人物逐渐停止
        else:
            if self.face_right:  # 人物姿势是否朝右
                self.x_vel -= self.x_accel
                if self.x_vel < 0:  # 速度减为0，切换状态为站立
                    self.x_vel = 0
                    self.state = 'stand'
            else:
                self.x_vel += self.x_accel
                if self.x_vel > 0:
                    self.x_vel = 0
                    self.state = 'stand'

    def jump(self, keys, level):
        self.frame_index = 9
        self.y_vel += self.anti_gravity
        # 速度为正，状态变为下落
        if self.y_vel >= 0:
            self.state = 'fall'

        if keys[pygame.K_LSHIFT]:
            self.max_x_vel = self.max_run_vel
            self.x_accel = self.run_accel
        else:
            self.max_x_vel = self.max_walk_vel
            self.x_accel = self.walk_accel

        # 控制人物向右移动
        if keys[pygame.K_RIGHT] or self.msg_control_move == '右':
            self.face_right = True
            self.frames = self.right_frames
            # 加速度系统
            if self.x_vel < 0:  # 按右键时人物在向左运动，则减速
                self.frame_index = 3  # 急停刹车为第5帧
                self.x_accel = self.turn_accel
            # 根据当前速度，加速度，最大速度计算下一步的速度
            self.x_vel = self.calc_vel(self.x_vel, self.x_accel, self.max_x_vel, True)
        # 控制人物向左运动
        elif keys[pygame.K_LEFT] or self.msg_control_move == '左':
            self.face_right = False
            self.frames = self.left_frames
            if self.x_vel > 0:
                self.frame_index = 3
                self.x_accel = self.turn_accel
            self.x_vel = self.calc_vel(self.x_vel, self.x_accel, self.max_x_vel, False)
        # 无按键控制或手势响应，人物逐渐停止
        else:
            if self.face_right:  # 人物姿势是否朝右
                self.x_vel -= self.x_accel
                if self.x_vel < 0:  # 速度减为0，切换状态为站立
                    self.x_vel = 0
            else:
                self.x_vel += self.x_accel
                if self.x_vel > 0:
                    self.x_vel = 0

        # 控制人物大小跳
        # if not ((keys[pygame.K_SPACE]) or (self.msg_control_jump == '跳')):
        #     self.state = 'fall'

        if (keys[pygame.K_SPACE]) or (self.msg_control_jump == '跳'):
            pass
        else:
            self.state = 'fall'

        if (keys[pygame.K_RSHIFT] or self.msg_control_special == '攻') and self.msg_control_fire >= constants.FIRE_CONTROL:
            if self.fire and self.can_shoot:
                self.shoot_fireball(level)

    def fall(self, keys, level):
        self.can_jump = False
        self.y_vel = self.calc_vel(self.y_vel, self.gravity, self.max_y_vel, True)
        if keys[pygame.K_LSHIFT]:
            self.max_x_vel = self.max_run_vel
            self.x_accel = self.run_accel
        else:
            self.max_x_vel = self.max_walk_vel
            self.x_accel = self.walk_accel
        # 发射火球
        if (keys[pygame.K_RSHIFT] or self.msg_control_special == '攻') and self.msg_control_fire >= constants.FIRE_CONTROL:
            if self.fire and self.can_shoot:
                self.shoot_fireball(level)
        # 控制人物向右移动
        if keys[pygame.K_RIGHT] or self.msg_control_move == '右':
            self.face_right = True
            self.frames = self.right_frames
            # 加速度系统
            if self.x_vel < 0:  # 按右键时人物在向左运动，则减速
                self.frame_index = 3  # 急停刹车为第5帧
                self.x_accel = self.turn_accel
            # 根据当前速度，加速度，最大速度计算下一步的速度
            self.x_vel = self.calc_vel(self.x_vel, self.x_accel, self.max_x_vel, True)
        # 控制人物向左运动
        elif keys[pygame.K_LEFT] or self.msg_control_move == '左':
            self.face_right = False
            self.frames = self.left_frames
            if self.x_vel > 0:
                self.frame_index = 3
                self.x_accel = self.turn_accel
            self.x_vel = self.calc_vel(self.x_vel, self.x_accel, self.max_x_vel, False)
        # 无按键控制或手势响应，人物逐渐停止
        else:
            if self.face_right:  # 人物姿势是否朝右
                self.x_vel -= self.x_accel
                if self.x_vel < 0:  # 速度减为0，切换状态为站立
                    self.x_vel = 0
            else:
                self.x_vel += self.x_accel
                if self.x_vel > 0:
                    self.x_vel = 0

    def die(self, keys, level):
        self.rect.y += self.y_vel
        self.y_vel += self.anti_gravity

    def small2big(self, keys, level):
        frame_dur = 35
        sizes = [1, 0, 1, 0, 1, 2, 0, 1, 2, 0, 2]  # 0-small, 1-medium, 2-big
        frames_and_idx = [(self.small_normal_frames, 0), (self.small_normal_frames, 7), (self.big_normal_frames, 0)]
        if self.translation_timer == 0:
            self.big = True
            self.ate_mushroom = True
            self.translation_timer = self.current_time
            self.changing_idx = 0
        elif self.current_time - self.translation_timer > frame_dur:
            self.translation_timer = self.current_time
            frames, idx = frames_and_idx[sizes[self.changing_idx]]
            self.change_player_image(frames, idx)
            self.changing_idx += 1
            if self.changing_idx == len(sizes):  # 变身的最后一帧
                self.translation_timer = 0
                self.state = 'walk'
                self.right_frames = self.right_big_normal_frames
                self.left_frames = self.left_big_normal_frames

    def big2small(self, keys, level):
        frame_dur = 35
        sizes = [2, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0]  # 0-small, 1-medium, 2-big
        frames_and_idx = [(self.small_normal_frames, 8), (self.big_normal_frames, 8), (self.big_normal_frames, 4)]
        if self.translation_timer == 0:
            self.translation_timer = self.current_time
            self.ate_mushroom = False
            self.changing_idx = 0
        elif self.current_time - self.translation_timer > frame_dur:
            self.translation_timer = self.current_time
            frames, idx = frames_and_idx[sizes[self.changing_idx]]
            self.change_player_image(frames, idx)
            self.changing_idx += 1
            if self.changing_idx == len(sizes):  # 变身的最后一帧
                self.translation_timer = 0
                self.state = 'walk'
                self.big = False
                self.right_frames = self.right_small_normal_frames
                self.left_frames = self.left_small_normal_frames

    def big2fire(self, keys, level):
        frame_dur = 35
        sizes = [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0]  # 0-small, 1-medium, 2-big
        frames_and_idx = [(self.big_fire_frames, 3), (self.big_normal_frames, 3)]
        if self.translation_timer == 0:
            self.big = True
            self.fire = True
            self.translation_timer = self.current_time
            self.changing_idx = 0
        elif self.current_time - self.translation_timer > frame_dur:
            self.translation_timer = self.current_time
            frames, idx = frames_and_idx[sizes[self.changing_idx]]
            self.change_player_image(frames, idx)
            self.changing_idx += 1
            if self.changing_idx == len(sizes):  # 变身的最后一帧
                self.translation_timer = 0
                self.state = 'walk'
                self.right_frames = self.right_big_fire_frames
                self.left_frames = self.left_big_fire_frames

    def fire2big(self, keys, level):
        frame_dur = 35
        sizes = [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0]  # 0-small, 1-medium, 2-big
        frames_and_idx = [(self.big_normal_frames, 3), (self.big_fire_frames, 3)]
        if self.translation_timer == 0:
            self.big = True
            self.translation_timer = self.current_time
            self.changing_idx = 0
        elif self.current_time - self.translation_timer > frame_dur:
            self.translation_timer = self.current_time
            frames, idx = frames_and_idx[sizes[self.changing_idx]]
            self.change_player_image(frames, idx)
            self.changing_idx += 1
            if self.changing_idx == len(sizes):  # 变身的最后一帧
                self.translation_timer = 0
                self.state = 'walk'
                self.fire = False
                self.right_frames = self.right_big_normal_frames
                self.left_frames = self.left_big_normal_frames

    def change_player_image(self, frames, idx):
        self.frame_index = idx
        if self.face_right:
            self.right_frames = frames[0]
            self.image = self.right_frames[self.frame_index]
        else:
            self.left_frames = frames[1]
            self.image = self.left_frames[self.frame_index]
        last_frame_bottom = self.rect.bottom
        last_frame_centerx = self.rect.centerx
        self.rect = self.image.get_rect()
        self.rect.bottom = last_frame_bottom
        self.rect.centerx = last_frame_centerx

    def go_die(self):
        self.dead = True
        self.y_vel = self.jump_vel
        self.frame_index = 9
        self.state = 'die'
        self.death_timer = self.current_time

    def is_hurt_immune(self):
        if self.hurt_immune:
            if self.hurt_immune_timer == 0:
                self.hurt_immune_timer = self.current_time
                self.blank_image = pygame.Surface((1, 1))
            elif self.current_time - self.hurt_immune_timer < 2000:
                if (self.current_time - self.hurt_immune_timer) % 100 < 50:  # 前50ms
                    self.image = self.blank_image
            else:
                self.hurt_immune = False
                self.hurt_immune_timer = 0

    def calc_vel(self, vel, accel, max_vel, is_positive=True):
        """
        计算下一步的速度
        :param vel: 当前速度
        :param accel: 加速度
        :param max_vel: 最大限速
        :param is_positive: 加速度是否为正（以水平向右为正方向
        :return: None
        """
        if is_positive:
            return min(vel + accel, max_vel)
        else:
            return max(vel - accel, -max_vel)

    def calc_frame_duration(self):
        """
        计算动画每帧持续时间
        :return: None
        """
        # 帧持续时间根据人物速度改变，最大速度时为20ms，最小速度为80ms，线性变换，求出duration和x_vel的关系式
        duration = -60 / self.max_run_vel + abs(self.x_vel) + 80
        return duration

    def shoot_fireball(self, level):
        if self.current_time - self.last_fireball_timer > 300:
            self.frame_index = 10
            fireball = powerup.Fireball(self.rect.centerx, self.rect.centery, self.face_right)
            level.powerup_group.add(fireball)
            self.can_shoot = False
            self.last_fireball_timer = self.current_time
