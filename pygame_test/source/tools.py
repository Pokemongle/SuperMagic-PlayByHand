import random
import pygame
from source import setup
import os


class Game:
    """
    游戏主体
    初始化游戏窗口、帧率、启动游戏
    """

    def __init__(self, state_dict, start_state):
        """
        初始化游戏
        """
        self.screen = pygame.display.get_surface()  # 设置游戏窗口画布
        self.clock = pygame.time.Clock()  # 设置时钟
        self.keys = pygame.key.get_pressed()
        self.state_dict = state_dict
        self.state = self.state_dict[start_state]

    def update(self):
        if self.state.finished:
            next_state = self.state.next
            self.state.finished = False
            self.state = self.state_dict[next_state]
        self.state.update(self.screen, self.keys)

    def run(self):
        """
        启动游戏
        :param
        :return:
        """
        while True:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.display.quit()
                elif event.type == pygame.KEYDOWN:
                    self.keys = pygame.key.get_pressed()
                elif event.type == pygame.KEYUP:
                    self.keys = pygame.key.get_pressed()

            # self.screen.fill((random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
            # image = get_image(setup.GRAPHICS['characters'], 258, 97, 17, 27, (0, 0, 0), random.randint(1,10))
            # self.screen.blit(image, (100, 100))
            self.update()
            pygame.display.update()
            self.clock.tick(60)  # 设置每秒帧数


def load_graph(path, accept=('.jpg', '.png', '.bmp', '.gif')):
    """
    加载一个文件夹中的所有图片
    :param path: 图片的文件夹所在的路径
    :param accept: 允许读入的图片文件的后缀
    :return: 以 图片名:图片文件Surface对象 键值对为基本单元的字典
    """
    graphics = {}  # 建立要返回的图片字典
    for pic in os.listdir(path):  # 对于文件夹中的每一个图片文件
        name, ext = os.path.splitext(pic)  # 获取文件后缀
        if ext.lower() in accept:  # 如果文件类型是允许读取的类型
            img = pygame.image.load(os.path.join(path, pic))  # 允许使用pygame定义的载入方法载入图片
            # 图片格式转换预处理，加快游戏画面渲染
            if img.get_alpha():  # 如果图片有alpha层，统一转换成带透明底的格式
                img = img.convert_alpha()
            else:  # 否则转换成普通格式
                img = img.convert()
            graphics[name] = img
    return graphics


def get_image(sheet, x, y, width, height, colorkey, scale):
    """
    从加载的图片中获取某部分图片
    :param sheet: 传入的一张图片
    :param x: 设置抠图方框的左上角的x坐标
    :param y: 设置抠图方框的左上角的y坐标
    :param width: 抠图方框的宽
    :param height: 抠图方框的高
    :param colorkey: 快速抠图的底色，png格式的底色为纯黑色(0, 0, 0)
    :param scale: 放大倍数，将抠出的原始图片放大scale倍
    :return:
    """
    image = pygame.Surface((width, height))  # 创建空白画布
    image.blit(sheet, (0, 0), (x, y, width, height))  # 在画布的(0, 0)位置画原始的sheet图片
    image.set_colorkey(colorkey)  # 抠除背景
    image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))  # 放大图片
    return image  # 返回图片，image的类型为pygame内置的Surface
