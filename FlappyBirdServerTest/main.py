import sys
from os import path
rootdir = path.dirname( path.dirname( path.abspath(__file__) ) )
sys.path.append( path.join( rootdir, 'FlappyBirdClient', 'lib' ) )
from netClient import NetClient

from config import HOST, PORT

import threading
import unittest

global delay

from time import time
def newClient(clients):
    c = NetClient(host = HOST, port = PORT)
    start = time()
    c.connect()
    end = time()
    global delay
    delay += (end - start) * 1000
    clients.append(c)

class Test(unittest.TestCase):
    def test_connection(self):
        print('\nTesting connection')
        global delay
        delay = 0
        clients = []
        newClient(clients)
        print('  Delay: {0} ms'.format(delay))
        self.assertTrue(clients[0].connected)

    def test_manyConnection(self):
        size = [10, 20]
        for s in size:
            print('\nTesting {0} connections'.format(s))
            clients = []
            threads = []
            global delay
            delay = 0
            for i in range(s):
                t = threading.Thread( target = newClient, args = (clients, ) )
                t.start()
                threads.append(t)
            for t in threads:
                t.join()
            print('  Average delay: {0} ms'.format(delay / s))
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()
