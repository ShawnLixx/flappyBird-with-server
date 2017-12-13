# -*- coding: utf-8 -*-
import cocos
from cocos.scene import *
from cocos.actions import *
from cocos.layer import *  
from cocos.text  import *
from cocos.menu import *
import random
from atlas import *
from land import *
from bird import *
from score import *
from pipe import *
from collision import *
from netClient import NetClient
from errors import getErrorString
import common
import account


#vars
gameLayer = None
gameScene = None
spriteBird = None
land_1 = None
land_2 = None
startLayer = None
pipes = None
score = 0
listener = None
account = None
password = None
ipTextField = None
errorLabel = None
isGamseStart = False

# additional vars
difficulty = 0 # 0~2 three stages

user = Account()
net = NetClient()

def initGameLayer():
    global spriteBird, gameLayer, land_1, land_2
    # gameLayer: 游戏场景所在的layer
    gameLayer = Layer()
    # add background
    bg = createAtlasSprite("bg_day")
    bg.position = (common.visibleSize["width"]/2, common.visibleSize["height"]/2)
    gameLayer.add(bg, z=0)
    # add moving bird
    spriteBird = creatBird()
    gameLayer.add(spriteBird, z=20)
    # add moving land
    land_1, land_2 = createLand()
    gameLayer.add(land_1, z=10)
    gameLayer.add(land_2, z=10)
    # add gameLayer to gameScene
    gameScene.add(gameLayer)

def game_start(_gameScene):
    global gameScene, net
    # 给gameScene赋值
    gameScene = _gameScene
    initGameLayer()
    start_botton = SingleGameStartMenu()
    gameLayer.add(start_botton, z=20, name=start_botton.name)
    net.connect()

def createLabel(value, x, y):
    label=Label(value,  
        font_name='Times New Roman',  
        font_size=15, 
        color = (0,0,0,255), 
        width = common.visibleSize["width"] - 20,
        multiline = True,
        anchor_x='center',anchor_y='center')
    label.position = (x, y)
    return label

# single game start button的回调函数
def singleGameReady():
    removeContent()
    ready = createAtlasSprite("text_ready")
    ready.position = (common.visibleSize["width"]/2, common.visibleSize["height"] * 3/4)

    tutorial = createAtlasSprite("tutorial")
    tutorial.position = (common.visibleSize["width"]/2, common.visibleSize["height"]/2)
    
    spriteBird.position = (common.visibleSize["width"]/3, spriteBird.position[1])

    #handling touch events
    class ReadyTouchHandler(cocos.layer.Layer):
        is_event_handler = True     #: enable director.window events

        def __init__(self):
            super( ReadyTouchHandler, self).__init__()

        def on_mouse_press (self, x, y, buttons, modifiers):
            """This function is called when any mouse button is pressed

            (x, y) are the physical coordinates of the mouse
            'buttons' is a bitwise or of pyglet.window.mouse constants LEFT, MIDDLE, RIGHT
            'modifiers' is a bitwise or of pyglet.window.key modifier constants
               (values like 'SHIFT', 'OPTION', 'ALT')
            """
            self.singleGameStart(buttons, x, y)
    
        # ready layer的回调函数
        def singleGameStart(self, eventType, x, y):
            isGamseStart = True
        
            spriteBird.gravity = gravity #gravity is from bird.py
            # handling bird touch events
            addTouchHandler(gameScene, isGamseStart, spriteBird)
            score = 0   #分数，飞过一个管子得到一分
            # add moving pipes
            pipes = createPipes(gameLayer, gameScene, spriteBird, score, difficulty)
            # 小鸟AI初始化
            # initAI(gameLayer)
            # add score
            createScoreLayer(gameLayer)
            # add collision detect
            addCollision(gameScene, gameLayer, spriteBird, pipes, land_1, land_2)
            # remove startLayer
            gameScene.remove(readyLayer)

    readyLayer = ReadyTouchHandler()
    readyLayer.add(ready)
    readyLayer.add(tutorial)
    gameScene.add(readyLayer, z=10)

def backToMainMenu():
    restartButton = RestartMenu()
    gameLayer.add(restartButton, z=50, name = restartButton.name)

def showNotice():
    data = net.notice()
    if data['code'] != 1:
        showContent(getErrorString(data['code']))
    showContent(data['notice'])


def showContent(content):
    removeContent()
    notice = createLabel(content, common.visibleSize["width"]/2+5, common.visibleSize["height"] * 9/10)
    gameLayer.add(notice, z=70, name="content")

def removeContent():
    try:
        gameLayer.remove("content")
    except Exception, e:
        pass
    

class RestartMenu(Menu):
    def __init__(self):  
        super(RestartMenu, self).__init__()
        self.name = "restart_menu"
        self.menu_valign = CENTER  
        self.menu_halign = CENTER
        items = [
                (ImageMenuItem(common.load_image("button_restart.png"), self.initMainMenu)),
                (ImageMenuItem(common.load_image("button_notice.png"), showNotice)),
                (ImageMenuItem(common.load_image("button_difficulty.png"), lambda: chooseDifficulty(self))),
                ]  
        self.create_menu(items,selected_effect=zoom_in(),unselected_effect=zoom_out())

    def initMainMenu(self):
        gameScene.remove(gameLayer)
        initGameLayer()
        isGamseStart = False
        singleGameReady()

class SingleGameStartMenu(Menu):
    def __init__(self):  
        super(SingleGameStartMenu, self).__init__()
        self.name = "start_menu"
        self.menu_valign = CENTER
        self.menu_halign = CENTER
        items = [
                (ImageMenuItem(common.load_image("button_start.png"), self.gameStart)),
                (ImageMenuItem(common.load_image("button_notice.png"), showNotice)),
                (ImageMenuItem(common.load_image("button_difficulty.png"), lambda: chooseDifficulty(self))),
                ]
        self.create_menu(items,selected_effect=zoom_in(),unselected_effect=zoom_out())

    def gameStart(self):
        gameLayer.remove(self.name)
        singleGameReady() 

# Choose difficulty menu and callback functions
def chooseDifficulty(pre_menu):
    # pass previous menu to go back
    gameLayer.remove(pre_menu.name)
    choose_difficulty_menu = ChooseDifficultyMenu(pre_menu)
    gameLayer.add(choose_difficulty_menu, z=20, name=choose_difficulty_menu.name)

class ChooseDifficultyMenu(Menu):
    def __init__(self, pre_menu):
        super(ChooseDifficultyMenu, self).__init__()
        self.pre_menu = pre_menu
        self.name = "choose_difficulty_menu"
        self.menu_valign = CENTER
        self.menu_halign = CENTER
        items = [
                (ImageMenuItem(common.load_image("button_difficulty_easy.png"), lambda: self.changeDifficulty(0))),
                (ImageMenuItem(common.load_image("button_difficulty_medium.png"), lambda: self.changeDifficulty(1))),
                (ImageMenuItem(common.load_image("button_difficulty_hard.png"), lambda: self.changeDifficulty(2))),
                ]
        self.create_menu(items,selected_effect=zoom_in(),unselected_effect=zoom_out())

    def changeDifficulty(self, d):
        global difficulty
        difficulty = d
        diff_string = "unknown"
        if d == 0:
            diff_string = "easy"
        elif d == 1:
            diff_string = "medium"
        elif d == 2:
            diff_string = "hard"
        print("Set difficuly to " + diff_string + ".")

        # back to privious menu
        gameLayer.remove(self.name)
        gameLayer.add(self.pre_menu, z=50, name = self.pre_menu.name)
