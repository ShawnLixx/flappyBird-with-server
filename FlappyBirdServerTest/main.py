import sys
from os import path
rootdir = path.dirname( path.dirname( path.abspath(__file__) ) )
sys.path.append( path.join( rootdir, 'FlappyBirdClient', 'lib' ) )
from netClient import NetClient

from config import HOST, PORT

import threading
import unittest

import string
import random
def randstr(size = 8):
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(size))

global delay
global users
users = []
size = [10]

from time import time
def test(clients, target):
    c = NetClient(host = HOST, port = PORT)
    clients.append(c)
    start = time()
    c.connect()
    target(c)
    end = time()
    global delay
    delay += (end - start) * 1000

def newClient(c):
    pass

def registerLoginLogout(c):
    username = randstr()
    password = randstr()
    global users
    users.append([username, password])
    c.registration(username, password)
    token = c.login(username, password)['token']
    c.initializeSession(token)
    c.logout(token)

def noticeLeaderboardUserinfo(c):
    username, password = random.choice(users)
    token = c.login(username, password)['token']
    c.initializeSession(token)
    c.notice()
    c.getLeaderboard(0)
    c.getLeaderboard(1)
    c.getLeaderboard(2)
    c.getUserinfo(token)
    c.logout(token)

def gameplay(c):
    username, password = random.choice(users)
    token = c.login(username, password)['token']
    c.initializeSession(token)
    score, time, num = [0, 0, 0]
    for i in range(10):
        score += random.randint(1, 10)
        time += random.randint(1, 10)
        num += random.randint(1, 10)
        c.updateData(token, score, time, num)
    c.logout(token)

def mixedText(c):
    username = randstr()
    password = randstr()
    c.registration(username, password)
    token = c.login(username, password)
    notice = c.notice()
    c.logout()

def testWithPressure(target, prompt):
    for s in size:
        print('\nTesting {0} with {1} connections'.format(prompt, s))
        clients = []
        threads = []
        global delay
        delay = 0
        for i in range(s):
            t = threading.Thread( target = test, args = (clients, target) )
            t.start()
            threads.append(t)
        for t in threads:
            t.join()
        print('  Average delay: {0} ms'.format(delay / s))

class Test(unittest.TestCase):
    def test_00_connection(self):
        print('\nTesting connection')
        global delay
        delay = 0
        clients = []
        test( clients, newClient )
        print('  Delay: {0} ms'.format(delay))
        self.assertTrue(clients[0].connected)

    def test_01_manyConnection(self):
        testWithPressure( newClient, 'connection' )
        self.assertTrue(True)

    def test_02_registerLoginLogout(self):
        testWithPressure( registerLoginLogout, 'register, login and logout')
        self.assertTrue(True)

    def test_03_noticeLeaderboardUserinfo(self):
        testWithPressure( noticeLeaderboardUserinfo, 'notice' )
        self.assertTrue(True)

    def test_04_gameplay(self):
        testWithPressure( gameplay, 'gameplay' )
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()
