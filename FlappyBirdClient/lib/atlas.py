# -*- coding: utf-8 -*-
import cocos
import os

from cocos.euclid import *
from cocos.collision_model import *
from cocos.actions import *
import common

#位置信息
atlas = {}
atlas["bg_day"]={"width":288, "height":512, "x":0, "y":0}
atlas["bg_night"]={"width":288, "height":512, "x":292, "y":0}
atlas["bird0_0"]={"width":48, "height":48, "x":0, "y":970}
atlas["bird0_1"]={"width":48, "height":48, "x":56, "y":970}
atlas["bird0_2"]={"width":48, "height":48, "x":112, "y":970}
atlas["bird1_0"]={"width":48, "height":48, "x":168, "y":970}
atlas["bird1_1"]={"width":48, "height":48, "x":224, "y":646}
atlas["bird1_2"]={"width":48, "height":48, "x":224, "y":698}
atlas["bird2_0"]={"width":48, "height":48, "x":224, "y":750}
atlas["bird2_1"]={"width":48, "height":48, "x":224, "y":802}
atlas["bird2_2"]={"width":48, "height":48, "x":224, "y":854}
atlas["black"]={"width":32, "height":32, "x":584, "y":412}
atlas["blink_00"]={"width":10, "height":10, "x":276, "y":682}
atlas["blink_01"]={"width":10, "height":10, "x":276, "y":734}
atlas["blink_02"]={"width":10, "height":10, "x":276, "y":786}
atlas["brand_copyright"]={"width":126, "height":14, "x":884, "y":182}
atlas["button_menu"]={"width":80, "height":28, "x":924, "y":52}
atlas["button_ok"]={"width":80, "height":28, "x":924, "y":84}
atlas["button_pause"]={"width":26, "height":28, "x":242, "y":612}
atlas["button_play"]={"width":116, "height":70, "x":702, "y":234}
atlas["button_rate"]={"width":74, "height":48, "x":924, "y":0}
atlas["button_resume"]={"width":26, "height":28, "x":668, "y":284}
atlas["button_score"]={"width":116, "height":70, "x":822, "y":234}
atlas["button_share"]={"width":80, "height":28, "x":584, "y":284}
atlas["font_048"]={"width":24, "height":44, "x":992, "y":116}
atlas["font_049"]={"width":16, "height":44, "x":272, "y":906}
atlas["font_050"]={"width":24, "height":44, "x":584, "y":316}
atlas["font_051"]={"width":24, "height":44, "x":612, "y":316}
atlas["font_052"]={"width":24, "height":44, "x":640, "y":316}
atlas["font_053"]={"width":24, "height":44, "x":668, "y":316}
atlas["font_054"]={"width":24, "height":44, "x":584, "y":364}
atlas["font_055"]={"width":24, "height":44, "x":612, "y":364}
atlas["font_056"]={"width":24, "height":44, "x":640, "y":364}
atlas["font_057"]={"width":24, "height":44, "x":668, "y":364}
atlas["land"]={"width":336, "height":112, "x":584, "y":0}
atlas["medals_0"]={"width":44, "height":44, "x":242, "y":516}
atlas["medals_1"]={"width":44, "height":44, "x":242, "y":564}
atlas["medals_2"]={"width":44, "height":44, "x":224, "y":906}
atlas["medals_3"]={"width":44, "height":44, "x":224, "y":954}
atlas["new"]={"width":32, "height":14, "x":224, "y":1002}
atlas["number_context_00"]={"width":12, "height":14, "x":276, "y":646}
atlas["number_context_01"]={"width":12, "height":14, "x":276, "y":664}
atlas["number_context_02"]={"width":12, "height":14, "x":276, "y":698}
atlas["number_context_03"]={"width":12, "height":14, "x":276, "y":716}
atlas["number_context_04"]={"width":12, "height":14, "x":276, "y":750}
atlas["number_context_05"]={"width":12, "height":14, "x":276, "y":768}
atlas["number_context_06"]={"width":12, "height":14, "x":276, "y":802}
atlas["number_context_07"]={"width":12, "height":14, "x":276, "y":820}
atlas["number_context_08"]={"width":12, "height":14, "x":276, "y":854}
atlas["number_context_09"]={"width":12, "height":14, "x":276, "y":872}
atlas["number_context_10"]={"width":12, "height":14, "x":992, "y":164}
atlas["number_score_00"]={"width":16, "height":20, "x":272, "y":612}
atlas["number_score_01"]={"width":16, "height":20, "x":272, "y":954}
atlas["number_score_02"]={"width":16, "height":20, "x":272, "y":978}
atlas["number_score_03"]={"width":16, "height":20, "x":260, "y":1002}
atlas["number_score_04"]={"width":16, "height":20, "x":1002, "y":0}
atlas["number_score_05"]={"width":16, "height":20, "x":1002, "y":24}
atlas["number_score_06"]={"width":16, "height":20, "x":1008, "y":52}
atlas["number_score_07"]={"width":16, "height":20, "x":1008, "y":84}
atlas["number_score_08"]={"width":16, "height":20, "x":584, "y":484}
atlas["number_score_09"]={"width":16, "height":20, "x":620, "y":412}
atlas["pipe2_down"]={"width":52, "height":320, "x":0, "y":646}
atlas["pipe2_up"]={"width":52, "height":320, "x":56, "y":646}
atlas["pipe_down"]={"width":52, "height":320, "x":112, "y":646}
atlas["pipe_up"]={"width":52, "height":320, "x":168, "y":646}
atlas["score_panel"]={"width":238, "height":126, "x":0, "y":516}
atlas["text_game_over"]={"width":204, "height":54, "x":784, "y":116}
atlas["text_ready"]={"width":196, "height":62, "x":584, "y":116}
atlas["title"]={"width":178, "height":48, "x":702, "y":182}
atlas["tutorial"]={"width":114, "height":98, "x":584, "y":182}
atlas["white"]={"width":32, "height":32, "x":584, "y":448}

#获得atlas sprite
def createAtlasSprite(name):
    sprite = cocos.sprite.Sprite(common.load_image(name+".png"))
    return sprite

def createAnimatingSprite(name):
    sprite = cocos.sprite.Sprite(common.load_image(name+".gif"))
    return sprite

class CollidableAnimatingSprite(cocos.sprite.Sprite):
    def __init__(self, image, center_x, center_y, radius):
        super(CollidableAnimatingSprite, self).__init__(common.load_image(image+".gif"))
        self.position = (center_x, center_y)
        self.cshape = CircleShape(Vector2(center_x, center_y), radius)
        self.name = image
        self.gravity = 0
        self.velocity = (0, 0)
        self.do(Move())

class CollidableRectSprite(cocos.sprite.Sprite):
    def __init__(self, image, center_x, center_y, half_width, half_height):
        super(CollidableRectSprite, self).__init__(common.load_image(image+".png"))
        self.position = (center_x, center_y)
        self.cshape = AARectShape(Vector2(center_x, center_y), half_width, half_height)
        self.name = image