# -*- coding: utf-8 -*-
import socket, netstream
import hashlib
MD5 = hashlib.md5()

def _getMD5(s):
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
            self.connected = False

        return self.connected

    # decorator to ensure connected
    def connectedRequired(fun):
        def wrapper(self, *args, **kwargs):
            if self.connected:
                return fun(self, **kwargs)
            else:
                return None
        return wrapper

    def _send(self, data):
        if self.connected:
            data['sid'] = self.sid
            netstream.send(self.sock, data)
            return True
        else:
            return False

    @connectedRequired
    def _recv(self):
        data = netstream.read(sock)
        if data == netstream.TIMEOUT or data == netstream.CLOSED or data == netstream.EMPTY:
            return None
        else:
            return data

    def _sendAndRecv(self, data):
        self._send(data)
        data = self._recv()
        if data == None:
            data = {'code': -1} # -1 for network error
        return data

    # functions corresponding to API

    @connectedRequired
    def registration(self, username, password):
        password = _getMD5(password)
        return self._sendAndRecv({
            'type': 0,
            'username': username,
            'password': password})

    @connectedRequired
    def login(self, username, password):
        password = _getMD5(password)
        return self._sendAndRecv({
            'type': 1,
            'username': username,
            'password': password})

    @connectedRequired
    def initializeSession(self, token):
        return self._sendAndRecv({
            'type': 2,
            'token': token})

    @connectedRequired
    def notice(self):
        return self._sendAndRecv({
            'type': 5})

    @connectedRequired
    def logout(self):
        return self._sendAndRecv({
            'type': 3})

    @connectedRequired
    def updateData(self, token, score, time, num):
        return self._sendAndRecv({
            'type': 4,
            'token' token,
            'score': score,
            'time': time,
            'num': num})

    @connectedRequired
    def updateTimeStamp(self):
        return self._sendAndRecv({
            'type': 6})
