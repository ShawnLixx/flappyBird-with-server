# -*- coding: utf-8 -*-
import random
from cocos.actions import *
from cocos.cocosnode import *
from cocos.collision_model import *
import random
from atlas import *
from bird import *
from score import *
from game_controller import *
import common

# constants
pipeCount = 3
pipeHeight = 320
pipeWidth = 52
pipeDistance = 100    #上下管道间的距离
pipeInterval = 180    #两根管道的水平距离
waitDistance = 100    #开始时第一根管道距离屏幕最右侧的距离
heightOffset = 25     #管道的高度偏移值
maxOffset = 120
minOffset = -100
# vars
lastHeightOffset = 0
movingSpeed = 50
PIPE_NEW = 0
PIPE_PASS = 1
pipes = {}    #contains nodes of pipes
pipeState = {}    #PIPE_NEW or PIPE_PASS
downPipeYPosition = {}    #朝下pipe的最下侧的y坐标
upPipeYPosition = {}  #朝上pipe的最上侧的y坐标
pipeIndex = 0

class ActorModel(object):
    def __init__(self, cx, cy, half_width, half_height,name):
            self.cshape = CircleShape(eu.Vector2(center_x, center_y), radius)
            self.name = name

def createPipes(layer, gameScene, spriteBird, score, difficulty):
    global g_score, movePipeFunc, calScoreFunc, time, pass_num

    # Randomly generate next pipe height, according to last pipe
    def generateNextPipe():
        global lastHeightOffset
        if random.random() < 0.5:
            # lower pipe
            s = float(pipeInterval - pipeWidth) # real distance between two pipe
            t = s / movingSpeed
            h_min = lastHeightOffset + 0.5 * spriteBird.gravity * (t ** 2)
            h_max = lastHeightOffset
            h_min = minOffset if h_min < minOffset else h_min
            # adjust h_min and h_max according to difficulty
            h_diff = h_max - h_min
            if difficulty == 0:
                h_min = h_min + h_diff * 0.5
            elif difficulty == 1:
                h_min = h_min + h_diff * 0.2
                h_max = h_max - h_diff * 0.2
            elif difficulty == 2:
                h_max = h_max - h_diff * 0.5
            h = random.uniform(h_min, h_max)
        else:
            # higher pipe
            s = float(pipeInterval - pipeWidth)
            t = s / movingSpeed
            h_max = t * upSpeed + lastHeightOffset
            h_min = lastHeightOffset
            h_max = maxOffset if h_max > maxOffset else h_max

            # adjust h_min and h_max according to difficulty
            h_diff = h_max - h_min
            if difficulty == 0:
                h_max = h_max - h_diff * 0.5
            elif difficulty == 1:
                h_max = h_max - h_diff * 0.2
                h_min = h_min + h_diff * 0.2
            elif difficulty == 2:
                h_min = h_min + h_diff * 0.5
            h = random.uniform(h_min, h_max)
        lastHeightOffset = h
        print("Next generated height offset: " + str(h))
        return h # return next higher pipe y position

    def initPipe():
        global movingSpeed, pipeInterval, pipeDistance

        # adjust according to difficulty
        if difficulty == 0:
            movingSpeed = 50
        elif difficulty == 1:
            movingSpeed = 70
            pipeInterval = 150
        elif difficulty == 2:
            movingSpeed = 100
            pipeInterval = 130

        for i in range(0, pipeCount):
            #把downPipe和upPipe组合为singlePipe
            downPipe = CollidableRectSprite("pipe_down", 0, (pipeHeight + pipeDistance), pipeWidth/2, pipeHeight/2) #朝下的pipe而非在下方的pipe
            upPipe = CollidableRectSprite("pipe_up", 0, 0, pipeWidth/2, pipeHeight/2)  #朝上的pipe而非在上方的pipe
            singlePipe = CocosNode()
            singlePipe.add(downPipe, name="downPipe")
            singlePipe.add(upPipe, name="upPipe")
            
            #设置管道高度和位置
            singlePipe.position=(common.visibleSize["width"] + i*pipeInterval + waitDistance, heightOffset + generateNextPipe())
            layer.add(singlePipe, z=10)
            pipes[i] = singlePipe
            pipeState[i] = PIPE_NEW
            upPipeYPosition[i] = singlePipe.position[1] + pipeHeight/2
            downPipeYPosition[i] = singlePipe.position[1] + pipeHeight/2 + pipeDistance

    def movePipe(dt):
        #moveDistance = common.visibleSize["width"]/(2*60)   # 移动速度和land一致
        # Move according to dt instead of frame
        moveDistance = movingSpeed * dt
        for i in range(0, pipeCount):
            pipes[i].position = (pipes[i].position[0]-moveDistance, pipes[i].position[1])
            if pipes[i].position[0] < -pipeWidth/2:
                pipeNode = pipes[i]
                pipeState[i] = PIPE_NEW
                next = i - 1
                if next < 0: next = pipeCount - 1
                pipeNode.position = (pipes[next].position[0] + pipeInterval, heightOffset + generateNextPipe())
                upPipeYPosition[i] = pipeNode.position[1] + pipeHeight/2
                downPipeYPosition[i] = pipeNode.position[1] + pipeHeight/2 + pipeDistance
                break

    def calScore(dt):
        global g_score, pass_num, time
        time = time + dt
        birdXPosition = spriteBird.position[0]
        for i in range(0, pipeCount):
            if pipeState[i] == PIPE_NEW and pipes[i].position[0]< birdXPosition:
                pipeState[i] = PIPE_PASS
                #update data
                if difficulty == 0:
                    g_score = g_score + 1
                elif difficulty == 1:
                    g_score = g_score + 3
                elif difficulty == 2:
                    g_score = g_score + 5
                pass_num = pass_num + 1
                setSpriteScores(g_score) #show score on top of screen

                data = common.net.initializeSession(common.user.token)
                if data['code'] != 1:
                    err_str = getErrorString(data['code'])

                common.net.updateData(common.user.token, g_score, time, pass_num)
    
    g_score = score
    time = 0
    pass_num = score
    initPipe()
    movePipeFunc = movePipe
    calScoreFunc = calScore
    gameScene.schedule(movePipe)
    gameScene.schedule(calScore)
    return pipes

def removeMovePipeFunc(gameScene):
    global movePipeFunc
    if movePipeFunc != None:
        gameScene.unschedule(movePipeFunc)

def removeCalScoreFunc(gameScene):
    global calScoreFunc
    if calScoreFunc != None:
        gameScene.unschedule(calScoreFunc)

def getPipes():
    return pipes

def getUpPipeYPosition():
    return upPipeYPosition

def getPipeCount():
    return pipeCount

def getPipeWidth():
    return pipeWidth
