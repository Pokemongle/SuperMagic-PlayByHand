"""
右手控制移动时 判定最灵敏的手势是 [大拇指] 被 [无名指] 和 [中指] 遮住
"""
# (1)调用库
import cv2
import time
import math
from cvzone.HandTrackingModule import HandDetector  # 手部检测方法
import autopy

# (2)函数

def vertorAngle(v1,v2):
    """
        求解二维向量的角度
        :param v1,v2:
        :return angle:
    """
    v1_x = v1[0]
    v1_y = v1[1]
    v2_x = v2[0]
    v2_y = v2[1]
    try:
        angle = math.degrees(math.acos(
            (v1_x * v2_x + v1_y * v2_y) / (((v1_x ** 2 + v1_y ** 2) ** 0.5) * ((v2_x ** 2 + v2_y ** 2) ** 0.5))))
    except:
        angle = 65535.
    if angle > 180.:
        angle = 65535.
    return angle

def handAngle(hand):
    """
    获取单个手掌中五根手指的角度
    :param hand:
    :return AngleList:
    """
    AngleList = [];
    reference=[-1,0]
    #thumb angle
    angle = vertorAngle(reference, (hand[3][0] - hand[4][0], hand[3][1] - hand[4][1]))
    AngleList.append(angle)
    #forefinger angle
    angle = vertorAngle(reference, (hand[7][0] - hand[8][0], hand[7][1] - hand[8][1]))
    AngleList.append(angle)
    #middlefinger angle
    angle = vertorAngle(reference, (hand[11][0] - hand[12][0], hand[11][1] - hand[12][1]))
    AngleList.append(angle)
    #ringfinger angle
    angle = vertorAngle(reference, (hand[15][0] - hand[16][0], hand[15][1] - hand[16][1]))
    AngleList.append(angle)
    #pinkfinger angle
    angle = vertorAngle(reference, (hand[19][0] - hand[20][0], hand[19][1] - hand[20][1]))
    AngleList.append(angle)
    return AngleList

def detectGes(hand,v0,v1,v2,v3,v4):
    """
        判断五根手指的角度是否在指定范围内
        :param hand: 包含五个手指角度的列表
        :param v0-v4: 每个手指角度应该在的范围
        :return: True（如果所有角度都在指定范围内）或False（如果有一个或多个角度不在指定范围内）
    """
    if hand[0] < v0[0] or hand[0] > v0[1]:
        return False
    if hand[1] < v1[0] or hand[1] > v1[1]:
        return False
    if hand[2] < v2[0] or hand[2] > v2[1]:
        return False
    if hand[3] < v3[0] or hand[3] > v3[1]:
        return False
    if hand[4] < v4[0] or hand[4] > v4[1]:
        return False
    return True

def main():
    print('Opening camera')
    print('Game start!')
    #初始化
    AngleListL = None
    AngleListR = None
    minDetect = 1 #seconds
    detectTime : float=0
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
            # 计算五根手指的角度
            AngleListL = handAngle(lmListL)
            print(AngleListL)
        #右手
        if handR:
            lmListR = handR['lmList']
            # 判断右手手指是否张开
            fingersR = detector.fingersUp(handR)
            fingersR[0] = 1 - fingersR[0]  # 拇指逻辑相反，手动矫正。
            # 计算五根手指的角度
            AngleListR = handAngle(lmListR)
            print(AngleListR)
            # 移动判定
            # 左移
            if AngleListR[1]>120 and fingersR[0] == 0 and fingersR[1] == 1 and fingersR[2] == 0 and fingersR[3] == 0 and fingersR[4] == 0:
                print('左')
            # 右移
            elif AngleListR[1]<60 and fingersR[0] == 0 and fingersR[1] == 1 and fingersR[2] == 0 and fingersR[3] == 0 and fingersR[4] == 0:
                print('右')

        #手势判定
        if AngleListL is not None and AngleListR is not None:
            #手势1 三角
            if detectGes(AngleListL,[0,25],[55,70],[45,70],[100,120],[90,120]) and detectGes(AngleListR,[145,180],[115,135],[115,135],[55,80],[55,80]):
                if(time.time()-detectTime>minDetect):
                    detectTime=time.time()
                    print('手势一detected')

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

