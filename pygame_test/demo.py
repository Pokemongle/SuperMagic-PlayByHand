import pygame
pygame.init()

width, height = 500, 500
pygame.display.set_mode((width, height))
screen = pygame.display.get_surface()
# 载入背景图并缩放
bgpic = pygame.image.load('./img_test/bg.PNG')
bgpic = pygame.transform.scale(bgpic, (width, height))
# 载入mario
mario_image = pygame.image.load('./img_test/mario.png')
mario_image = pygame.transform.scale(mario_image, (20, 40))
# 创建精灵
mario = pygame.sprite.Sprite()
mario.image = mario_image
mario.rect = mario.image.get_rect()
# 玩家组
player_group = pygame.sprite.Group()
player_group.add(mario)

# 开始游戏
while True:
    # 更新部分
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.display.quit()
            quit()
        if event.type == pygame.KEYDOWN:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_DOWN]:
                mario.rect.y += 10
            if keys[pygame.K_UP]:
                mario.rect.y -= 10
    # 画图部分
    screen.blit(bgpic, (0, 0))
    player_group.draw(screen)
    pygame.display.update()