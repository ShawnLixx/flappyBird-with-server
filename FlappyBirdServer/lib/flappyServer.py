# -*- coding: utf-8 -*-
import socket, select, netstream, random, pickle, os, traceback, json, uuid
import time

# contants
HOST = "127.0.0.1"
PORT = 9234
DIR = "serverData"
FILE = "data.json"

class FlappyServer:
    def __init__(self):
        # reload data from file.
        # check directory existance.
        if not os.path.isdir(DIR):
            os.mkdir(DIR)
        self.path = os.path.join(DIR, FILE)
        try:
            with open(self.path, "r") as f:
                serverData = json.load(f)
            self.allUsers = serverData["allUsers"]
            self.blackList = serverData["blackList"]
            self.nextUid = serverData["nextUid"]
            self.notice = serverData["notice"]
        except Exception:
            print("Server data does not exist or is destroyed.")
            self.allUsers = {}
            self.blackList = []
            self.nextUid = 0
            self.notice = ""
            self.save()
        self.connections = {}
        self.sid = 0
        self.host = HOST
        self.port = PORT
        self.sock = socket.socket()

    def run(self):
        self.sock.bind((self.host, self.port))
        self.sock.listen(4)
        self.inputs = []
        self.inputs.append(self.sock)
        print('server start! listening host:{} port:{}'.format(self.host, self.port))
        self.requestHandle()
        # creating

    def requestHandle(self):
        while self.inputs:
            try:
                rs, ws, es = select.select(self.inputs, [], [])
                for r in rs:
                    if r is self.sock:
                        # accept
                        connection, addr = self.sock.accept()
                        print('Got connection from' + str(addr) + " sid: {}".format(self.sid))
                        self.inputs.append(connection)
                        sendData = {}
                        sendData['sid'] = self.sid
                        netstream.send(connection, sendData)

                        cInfo = {}
                        cInfo['connection'] = connection
                        cInfo['addr'] = str(addr)
                        cInfo['uid'] = -1 # -1 for not initalized
                        cInfo['startTime'] = time.time()
                        cInfo['timeStamp'] = time.time()
                        self.connections[self.sid] = cInfo

                        self.sid += 1
                    else:
                        # receive data
                        recvData = netstream.read(r)
                        if recvData == netstream.CLOSED or recvData == netstream.TIMEOUT: # socket关闭
                            pass

                        else:  # 根据收到的request发送response
                            usid = recvData['sid']
                            if usid not in self.connections: # invalid usid
                                continue
                            # for registration
                            if recvData['type'] == 0: 
                                self.registration(recvData['username'], recvData['password'], usid)

                            # for login
                            elif recvData['type'] == 1:
                                self.login(recvData['username'], recvData['password'], usid)

                            # for initialize session
                            elif recvData['type'] == 2:
                                self.initalSession(recvData['token'], usid)
                            
                            # for request notice
                            elif recvData['type'] == 5:
                                self.sendNotice(usid)

                            # for update time stamp
                            elif recvData['type'] == 6:
                                self.updateTimeStamp(usid)

                            # for getting leaderboard
                            elif recvData['type'] == 8:
                                self.getLeaderboard(recvData['by'], usid)

                            # following request require session initalized
                            elif self.connections[usid]['uid'] == -1: # not initialized session
                                netstream.send(self.connections[usid]['connection'], {
                                   "code": 0}) # 0 for not initialized

                            else: # session initialized
                                # for logout
                                if recvData['type'] == 3:
                                    self.logout(recvData['token'], usid)

                                # for update states
                                elif recvData['type'] == 4:
                                    self.updateData(recvData['token'], recvData['score'], recvData['time'], recvData['num'], usid)

                                # for getting user information
                                elif recvData['type'] == 7:
                                    self.getUserInfo(recvData['token'], usid)


            except Exception:
                traceback.print_exc()
                print 'Error: socket 链接异常'

    def save(self):
        with open(self.path, "w") as f:
            json.dump({
                "allUsers": self.allUsers,
                "blackList": self.blackList,
                "nextUid": self.nextUid,
                "notice": self.notice}, f)

    def _registration(self, username, password):
        # check for username availability
        # return 1 for success, 2 for username already exists.
        if any(u["username"] == username for u in self.allUsers.itervalues()):
            return 2
        else:
            # add user
            self.allUsers[self.nextUid] = {
                    "username": username,
                    "password": password,
                    "token": "",
                    "best_score": 0,
                    "best_num": 0,
                    "best_time": 0}
            self.nextUid += 1
            self.save()
            return 1

    def _logout(self, uid):
        self.allUsers[uid]['token'] = ""
        
    def _addToBlack(self, uid):
        if uid not in self.blackList:
            self.blackList.append(uid)
            return True
        else:
            return False

    def _checkBlackList(self, uid):
        return uid in self.blackList

    def _getUidViaToken(self, token):
        for uid, user in self.allUsers.iteritems():
            if user['token'] == token:
                return uid
        return None

    def _getUidCheckToken(self, token, usid):
        # check token validation
        uid = self.connections[usid]['uid']
        user = self.allUsers[uid]
        if 'token' in user and user['token'] != "":
            if user['token'] == token:
                return self.connections[usid]['uid']
            else:
                # token error
                return None
        else:
            # user not logined
            return None

    def registration(self, username, password, usid):
        code = self._registration(username, password)
        netstream.send(self.connections[usid]['connection'], {
           "code": code}) 

    def login(self, username, password, usid):
        # check information correction
        uid = -1
        for _uid, profile in self.allUsers.iteritems():
            if username == profile["username"]:
                uid = _uid
                if password == profile["password"]:
                    # generate a token
                    newToken = uuid.uuid4().hex
                    self.allUsers[_uid]["token"] = newToken
                    netstream.send(self.connections[usid]['connection'], {
                        "code": 1,
                        "token": newToken}) # code 1 for success
                else:
                    netstream.send(self.connections[usid]['connection'], {
                        "code": 4}) # code 4 for password error
                break

        if uid == -1:
            netstream.send(self.connections[usid]['connection'], {
                "code": 3}) # code 3 for user not found

    def initalSession(self, token, usid):
        uid = self._getUidViaToken(token)
        if uid == None:
            netstream.send(self.connections[usid]['connection'], {
                "code": 5}) # code 5 for token invalid
        else:
            self.connections[usid]['uid'] = uid
            netstream.send(self.connections[usid]['connection'], {
                "code": 1}) # code 1 for success

    def logout(self, token, usid):
        uid = self._getUidCheckToken(token, usid)
        if uid == None:
            netstream.send(self.connections[usid]['connection'], {
                "code": 5}) # code 5 for auth failed
        else:
            self.connections[usid]['uid'] = -1
            self._logout(uid)
            netstream.send(self.connections[usid]['connection'], {
                "code": 1}) # code 1 for success


    def updateData(self, token, score, time, num, usid):
        # check for token
        uid = self._getUidCheckToken(token, usid)
        if uid == None:
            netstream.send(self.connections[usid]['connection'], {
                "code": 5}) # code 5 for auth failed
        else:
            user = self.allUsers[uid]
            if user['best_score'] < score:
                user['best_score'] = score
            if user['best_time'] < time:
                user['best_time'] = time
            if user['best_num'] < num:
                user['best_num'] = num
            netstream.send(self.connections[usid]['connection'], {
                "code": 1}) # code 1 for success


    def sendNotice(self, usid):
        netstream.send(self.connections[usid]['connection'], {
            "code": 1,
            "notice": self.notice}) # code 1 for success

    def updateTimeStamp(self, usid):
        self.connections[usid]['timeStamp'] = time.time()

    def getUserInfo(self, token, usid):
        uid = self._getUidViaToken(token)
        if uid == None:
            netstream.send(self.connections[usid]['connection'], {
                "code": 5}) # code 5 for token invalid
        else:
            user = self.allUsers[uid]
            netstream.send(self.connections[usid]['connection'], {
                "code": 1,
                "username": user['username'],
                "score": user['best_score'],
                "time": user['best_time'],
                "num": user['best_num']}) # code 1 for success

    def getLeaderboard(self, by, usid):
        key = "best_score"
        if by == 1:
            key = "best_time"
        elif by == 2:
            key = "best_num"
        # get list of user sorted by key
        sortedUsers = sorted(self.allUsers.values(), key = lambda x: x[key], reverse = True)
        # get top 10 user
        sortedUsers = sortedUsers[0:10]
        leaderboard = [{'username': user['username'],
            'data': user[key]} for user in sortedUsers]
        netstream.send(self.connections[usid]['connection'], {
            "code": 1,
            "leaderboard": leaderboard}) # code 1 for success

