"""
这个地方写注释
"""
# (1)调用库
import numpy as np
import cv2
import time
import math
from pynput import mouse
from cvzone.HandTrackingModule import HandDetector  # 手部检测方法
from cvzone import cornerRect
import autopy
import pyautogui
import win32api
import win32con

# (2)函数
def main():
    print('Opening camera')
    print('Game start!')
    #屏幕尺寸
    wScr, hScr = autopy.screen.size()  # 返回电脑屏幕的宽和高(1920.0, 1080.0)
    #摄像头与显示尺寸
    cap = cv2.VideoCapture(0 + cv2.CAP_DSHOW)  # 0代表自己电脑的摄像头
    cap.set(cv2.CAP_PROP_FPS, 30)  # 帧率 帧/秒
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1080)  # 设置显示框的宽度
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)  # 设置显示框的高度

    #检测手
    print('prepare detection...')
    detector = HandDetector(mode=False,  # 视频流图像
                            maxHands=2,  # 最多检测2只手
                            detectionCon=0.8,  # 最小检测置信度
                            minTrackCon=0.5)  # 最小跟踪置信度

    #处理数据
    print('srart detection...')
    pTime = 0  # 设置第一帧开始处理的起始时间
    presstime: float = 0
    clicktime: float = 0
    lastfps = 0

    while True:
        imgOSD = None
        # 图片是否成功接收、img帧图像
        success, img = cap.read()

        # flip as mirror
        img = cv2.flip(img, flipCode=1)  # 1代表水平翻转，0代表竖直翻转
        #手关键点坐标
        hands, img = detector.findHands(img, flipType=False, draw=True)  # flip hands label, draw skeleoton
        #print(hands)  # for debug use only
        fingerTopList = range(4, 21, 4)
        # split hands data
        handL = {}
        handR = {}
        for hand in range(len(hands)):
            if ('Left' == hands[hand]['type']):
                handL = hands[hand]
            elif ('Right' == hands[hand]['type']):
                handR = hands[hand]
        #左手
        if handL:
            lmListL = handL['lmList']
            print(lmListL)
        #右手
        if handR:
            lmListR = handR['lmList']
            print(lmListR)
            fingersR = detector.fingersUp(handR)
            fingersR[0] = 1 - fingersR[0]  # 拇指逻辑相反，手动矫正。
        #OSD information
        # FPS
        cTime = time.time()  # 处理完一帧图像的时间
        fps = (1 / (cTime - pTime) + lastfps * 2) / 3
        lastfps = (fps * 2 + lastfps) / 3
        pTime = cTime  # 重置起始时间
        # 在视频上显示fps信息，先转换成整数再变成字符串形式，文本显示坐标，文本字体，文本大小
        cv2.putText(img, '{:.1f}'.format(fps), (70, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)

        # show image on screen
        cv2.imshow('image', img)
        # 每帧滞留10毫秒后消失，ESC键退出
        if cv2.waitKey(10) & 0xFF == 27:
            break

    # exit program
    cap.release()
    cv2.destroyAllWindows()

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

