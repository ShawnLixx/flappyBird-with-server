# -*- coding: utf-8 -*-
import socket, netstream
import hashlib
import traceback

def _getMD5(s):
    MD5 = hashlib.md5()
    MD5.update(s)
    return MD5.hexdigest()

HOST = '127.0.0.1'
PORT = 9234

class NetClient:
    def __init__(self):
        self.connected = False
        self.host = HOST
        self.port = PORT
        self.sock = socket.socket()
        self.sid = -1

    def connect(self):
        try:
            self.sock.connect((self.host, self.port))
            # receive sid
            self.connected = True
            response = self._recv()
            self.sid = response['sid']
        except Exception:
            traceback.print_exc()
            self.connected = False

        return self.connected

    # decorator to ensure connected
    def connectedRequired(fun):
        def wrapper(self, *args, **kwargs):
            if self.connected:
                return fun(self, *args)
            else:
                return None
        return wrapper

    @connectedRequired
    def _send(self, data):
        data['sid'] = self.sid
        netstream.send(self.sock, data)
        return True

    @connectedRequired
    def _recv(self):
        data = netstream.read(self.sock)
        if data == netstream.TIMEOUT or data == netstream.CLOSED or data == netstream.EMPTY:
            return None
        else:
            return data

    def _sendAndRecv(self, data):
        if self._send(data):
            data = self._recv()
        else:
            data = None
        if data == None:
            data = {'code': -1} # -1 for network error
        return data

    # functions corresponding to API

    def registration(self, username, password):
        password = _getMD5(password)
        return self._sendAndRecv({
            'type': 0,
            'username': username,
            'password': password})

    def login(self, username, password):
        password = _getMD5(password)
        return self._sendAndRecv({
            'type': 1,
            'username': username,
            'password': password})

    def initializeSession(self, token):
        return self._sendAndRecv({
            'type': 2,
            'token': token})

    def notice(self):
        return self._sendAndRecv({
            'type': 5})

    def logout(self, token):
        return self._sendAndRecv({
            'type': 3,
            'token': token})

    def updateData(self, token, score, time, num):
        return self._sendAndRecv({
            'type': 4,
            'token': token,
            'score': score,
            'time': time,
            'num': num})

    def updateTimeStamp(self):
        return self._sendAndRecv({
            'type': 6})

    def getUserInfo(self, token):
        return self._sendAndRecv({
            'type': 7,
            'token': token})

    def getLeaderboard(self, by):
        return self._sendAndRecv({
            'type': 8,
            'by': by})

