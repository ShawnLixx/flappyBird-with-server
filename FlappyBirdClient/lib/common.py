import os
import pyglet
from account import Account
from netClient import NetClient

user = Account()
net = NetClient()

visibleSize = {"width":228, "height":512}

THISDIR = os.path.abspath(os.path.dirname(__file__))
DATADIR = os.path.normpath(os.path.join(THISDIR, '..', 'data'))

def load_image(path):
    return pyglet.image.load(os.path.join(DATADIR, path))