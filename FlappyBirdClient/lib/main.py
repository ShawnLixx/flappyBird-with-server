# -*- coding: utf-8 -*-
import cocos
from cocos.actions import *
from cocos.director import *
from cocos.scene import *
from game_controller import *

import common

def main(host, port):
    #initialize director
    director.init( width=common.visibleSize["width"], height=common.visibleSize["height"], caption="Flappy Bird")

    #turn off display FPS
    # director.show_FPS = True
    
    #run
    gameScene = Scene()
    game_start(gameScene, host, port)

    if director.scene:
        director.replace(gameScene)
    else:
        director.run(gameScene)

