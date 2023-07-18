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
    def __init__(self, msg_queue):
        # 主菜单初始化时把游戏信息也初始化
        game_info = {
            'score': 0,  # 分数统计
            'coin': 0,  # 吃到的金币数
            'lives': 3,  # 剩余生命数
            'player_state': 'small'  # 人物状态
        }
        self.start(game_info, msg_queue)  # 其他信息初始化

    def start(self, game_info, msg_queue):
        """
        实现主菜单的重置效果
        :param game_info: 游戏信息
        :param msg_queue: 消息队列
        :return: None
        """
        self.game_info = game_info  # 游戏关键信息
        self.setup_background()  # 设置背景
        self.setup_player()  # 设置玩家
        self.setup_cursor()  # 设置光标
        self.finished = False  # 状态是否关闭
        self.next = 'load_screen'   # 下一个状态的状态名
        self.cursor.state = '1P'    # 游戏模式选择光标状态，初始设置为单人游戏
        self.info = info.Info('main_menu', self.game_info)  # 游戏信息
        self.msg_queue = msg_queue  # 消息队列
        self.msg = ''   # 从消息队列接收到的最新消息
        self.control_msg = ''   # 控制游戏模式选择的消息

    def setup_background(self):
        """
        设置背景图像
        :return: None
        """
        self.background = setup.GRAPHICS['level_1']  # 从图库中取出一份图片文件，为关卡1的关卡图片，超级长的那张
        self.background_rect = self.background.get_rect()  # 获取图片的矩形对象（矩形属性RectType可选，目前没用上）
        # rect means rectangular
        # ============What does rect contain?============
        # x, y - coordinates of the Rect's top left point
        # top, bottom, left, right - left means the distance of the left edge to axis-y, and vice versa
        # center, centerx, centery - center = (centerx, centery)
        # size, width, height
        # w, h

        #  背景窗口缩放
        self.background = pygame.transform.scale(self.background, (int(self.background_rect.width * constants.BG_MULTI),
                                                                   int(self.background_rect.height * constants.BG_MULTI)))
        # ======How to make your specific image exactly fit the window you create as setup.SCREEN?======
        # use pygame.transform to zoom in/ out or stretch and squeeze
        # eg. I zoom out the background image 'level_1' to fit my SCREEN
        #     just calculate the constants BG_MULTI = SCREEN.H / height_of_the_image_in_pixel
        #     you need to checkout the height of the image in pixel by open the exact image file

        # 设置跟踪窗口
        self.viewport = setup.SCREEN.get_rect()  # the same size as the SCREEN
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
        if keys[pygame.K_UP] or self.control_msg == '左':
            self.cursor.state = '1P'
            self.cursor.rect.y = 360
        elif keys[pygame.K_DOWN] or self.control_msg == '右':
            self.cursor.state = '2P'
            self.cursor.rect.y = 405
        elif keys[pygame.K_RETURN] or self.control_msg == '跳':
            self.reset_game_info()
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
        # 读取消息队列最新的消息
        self.msg = (self.msg_queue.get()) if not self.msg_queue.empty() else self.msg
        if self.msg == '左' or self.msg == '右' or self.msg == '跳跃':
            self.control_msg = self.msg
        else:
            pass

        self.update_cursor(keys)
        self.info.update(self.msg)
        self.info.draw(surface)

    def reset_game_info(self):
        self.game_info = {
            'score': 0,
            'coin': 0,
            'lives': 3,
            'player_state': 'small'
        }
