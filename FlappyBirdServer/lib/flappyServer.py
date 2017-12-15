# -*- coding: utf-8 -*-
import socket, select, netstream, random, pickle
import os, traceback, json, uuid
import time, threading
from log import Log
from serverCmd import ServerCmd

# contants
DIR = "serverData"
FILE = "data.json"

class FlappyServer:
    def __init__(self, host, port, timeout, saving_gap):
        # reload data from file.
        # check directory existance.
        if not os.path.isdir(DIR):
            os.mkdir(DIR)
        self.path = os.path.join(DIR, FILE)
        self.logger = Log()
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

        self.host = host
        self.port = port
        self.timeout = timeout
        self.saving_gap = saving_gap
        
    def run(self):
        # multi-thread init
        self.lock = threading.Lock()
        self.runRequestHandle = True

        self._startRequestHandleThread()

        # start a timer to save data
        self.saver = None
        self._startSaver()
        
        print("Enter command line environment for server manager.")
        print("Command help for instructions.")

        # Start cmd loop.
        try:
            returnValue = ServerCmd(self).cmdloop()
            return returnValue
        except:
            self._exit()
            traceback.print_exc()
                
    # Handle request function
    def requestHandle(self):
        while self.runRequestHandle and self.inputs:
            try:
                rs, ws, es = select.select(self.inputs, [], [], 2)
                for r in rs:
                    self.lock.acquire()
                    if self.runRequestHandle and r is self.sock:
                        # accept
                        connection, addr = self.sock.accept()
                        self.logger.log('Got connection from' + str(addr) + " sid: {}".format(self.sid))
                        self.inputs.append(connection)
                        
                        sendData = {}
                        sendData['sid'] = self.sid
                        netstream.send(connection, sendData)

                        cInfo = {}
                        cInfo['connection'] = connection
                        cInfo['addr'] = addr
                        cInfo['uid'] = -1 # -1 for not initalized
                        cInfo['startTime'] = time.time()
                        cInfo['timeStamp'] = time.time()
                        self.connections[str(self.sid)] = cInfo

                        # set timer to moniter session timeout
                        self._updateTimer(self.sid)

                        self.sid += 1
                    else:
                        # receive data
                        recvData = netstream.read(r)

                        if recvData == netstream.CLOSED or recvData == netstream.TIMEOUT: # socket关闭
                            pass

                        else:  # 根据收到的request发送response
                            usid = recvData['sid']
                            usid = str(usid)

                            if usid not in self.connections: # invalid usid
                                netstream.send(r, {'code': 7}) # 7 for timeout
                                continue

                            # update timeout
                            self._updateTimer(usid)
                            self.connections[usid]['timeStamp'] = time.time()

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

                    self.lock.release()

            except Exception:
                self.lock.release()
                self.logger.log(traceback.format_exc())

        self.sock.close()
        print("Server terminated.")



    def _startRequestHandleThread(self):
        # Creating a new thread to handle request.
        try:
            # init variables
            self.connections = {}
            self.sid = 0
            self.sock = socket.socket()
            self.sock.bind((self.host, self.port))
            self.sock.listen(4)
            self.inputs = []
            self.inputs.append(self.sock)
            self.requestHandleThread = threading.Thread(target = self.requestHandle)
            self.runRequestHandle = True
            print('Server start! listening host:{} port:{}...'.format(self.host, self.port))
            self.requestHandleThread.start()
        except Exception:
            print("Unable to create request handler thread.")
            traceback.print_exc()

    def _endRequestHandleThread(self):
        self.lock.acquire()
        # Stop request handler thread.
        self.runRequestHandle = False
        print("Server terminating, please wait...")
        self.lock.release()
        # wait for thread stop.
        while self.requestHandleThread.isAlive():
            continue

    def _endTimers(self):
        # end all timers
        self.lock.acquire()
        for c in self.connections.values():
            if 'timer' in c:
                c['timer'].cancel()
        self.lock.release()
        
    # call this function to end the program
    def _exit(self):
        self._endRequestHandleThread()
        self._endTimers()
        self._endSaver()
        self.save()

    def save(self):
        with open(self.path, "w") as f:
            json.dump({
                "allUsers": self.allUsers,
                "blackList": self.blackList,
                "nextUid": self.nextUid,
                "notice": self.notice}, f)
        self.logger.log("Server data saved.")

    # start saver, save server data to disk per saving_gap seconds.
    def _startSaver(self):
        self.lock.acquire()
        self.save()
        self.saver = threading.Timer(self.saving_gap, self._startSaver)
        self.saver.start()
        self.lock.release()

    def _endSaver(self):
        self.lock.acquire()
        self.saver.cancel()
        self.lock.release()

    def _usernameInUseCheck(self, username):
        return any(u["username"] == username for u in self.allUsers.itervalues())

    def _uidCheck(self, uid):
        return str(uid) in self.allUsers

    def _registration(self, username, password):
        # check for username availability
        # return 1 for success, 2 for username already exists.
        if self._usernameInUseCheck(username):
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
        self.allUsers[str(uid)]['token'] = ""
        
    def _addToBlack(self, uid):
        self._logout(uid)
        if not self._checkBlackList(uid):
            self.blackList.append(int(uid))
            self.logger.log("User {} added to black list.".format(uid))
            return True
        else:
            return False

    def _rmFromBlack(self, uid):
        if self._checkBlackList(uid):
            self.blackList.remove(int(uid))
            self.logger.log("User {} removed from black list.".format(uid))
            return True
        else:
            return False

    def _checkBlackList(self, uid):
        return int(uid) in self.blackList

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

    # timer related
    # update timer when get new time stamp
    def _updateTimer(self, usid):
        usid = str(usid)
        if 'timer' in self.connections[usid]:
            self.connections[usid]['timer'].cancel()
        self.connections[usid]['timer'] = threading.Timer(self.timeout, self._sessionTimeout, (usid, ))
        self.connections[usid]['timer'].start()

    # session timeout
    def _sessionTimeout(self, sid):
        sid = str(sid)
        # destory this session.
        self.lock.acquire()
        self.inputs.remove(self.connections[sid]['connection'])
        del self.connections[sid]
        self.lock.release()

    def registration(self, username, password, usid):
        code = self._registration(username, password)
        netstream.send(self.connections[usid]['connection'], {
           "code": code})
        self.logger.log("Username {} registered.".format(username), usid)

    def login(self, username, password, usid):
        # check information correction
        uid = -1
        for _uid, profile in self.allUsers.iteritems():
            if username == profile["username"]:
                uid = _uid
                # check if in black list
                if self._checkBlackList(uid):
                    netstream.send(self.connections[usid]['connection'], {
                        "code": 6}) # code 6 for in black list
                elif password == profile["password"]:
                    # generate a token
                    newToken = uuid.uuid4().hex
                    self.allUsers[_uid]["token"] = newToken
                    netstream.send(self.connections[usid]['connection'], {
                        "code": 1,
                        "token": newToken}) # code 1 for success
                    self.logger.log("Username {} logined.".format(username), usid)
                else:
                    netstream.send(self.connections[usid]['connection'], {
                        "code": 4}) # code 4 for password error
                    self.logger.log("Username {} password error.".format(username), usid)
                break

        if uid == -1:
            netstream.send(self.connections[usid]['connection'], {
                "code": 3}) # code 3 for user not found
            self.logger.log("Username {} not found.".format(username), usid)


    def initalSession(self, token, usid):
        uid = self._getUidViaToken(token)
        if uid == None:
            netstream.send(self.connections[usid]['connection'], {
                "code": 5}) # code 5 for token invalid
            self.logger.log("Trying to initalize session, but token invalid.", usid)
        # check if in black list
        elif self._checkBlackList(uid):
            netstream.send(self.connections[usid]['connection'], {
                "code": 6}) # code 6 for in black list
        else:
            self.connections[usid]['uid'] = uid
            netstream.send(self.connections[usid]['connection'], {
                "code": 1}) # code 1 for success
            self.logger.log("Initalize session.", usid)

    def logout(self, token, usid):
        uid = self._getUidCheckToken(token, usid)
        if uid == None:
            netstream.send(self.connections[usid]['connection'], {
                "code": 5}) # code 5 for auth failed
            self.logger.log("Trying to logout, but token invalid.", usid)
        else:
            self.connections[usid]['uid'] = -1
            self._logout(uid)
            netstream.send(self.connections[usid]['connection'], {
                "code": 1}) # code 1 for success
            self.logger.log("Logout successfully.", usid)

    def updateData(self, token, score, time, num, usid):
        # check for token
        uid = self._getUidCheckToken(token, usid)
        if uid == None:
            netstream.send(self.connections[usid]['connection'], {
                "code": 5}) # code 5 for auth failed
            self.logger.log("Trying to update user data, but token invalid.", usid)
        # check if in black list
        elif self._checkBlackList(uid):
            netstream.send(self.connections[usid]['connection'], {
                "code": 6}) # code 6 for in black list
        else:
            user = self.allUsers[uid]
            changed = False
            if user['best_score'] < score:
                user['best_score'] = score
                changed = True
            if user['best_time'] < time:
                user['best_time'] = time
                changed = True
            if user['best_num'] < num:
                user['best_num'] = num
                changed = True
            netstream.send(self.connections[usid]['connection'], {
                "code": 1}) # code 1 for success
            if changed:
                self.logger.log("Update user data successfully.", usid)

    def sendNotice(self, usid):
        netstream.send(self.connections[usid]['connection'], {
            "code": 1,
            "notice": self.notice}) # code 1 for success
        self.logger.log("Request notice successfully.", usid)

    def updateTimeStamp(self, usid):
        netstream.send(self.connections[usid]['connection'], {'code': 1}) # code 1 for success

    def getUserInfo(self, token, usid):
        uid = self._getUidViaToken(token)
        if uid == None:
            netstream.send(self.connections[usid]['connection'], {
                "code": 5}) # code 5 for token invalid
            self.logger.log("Trying to get user information, but token invalid.", usid)
        # check if in black list
        elif self._checkBlackList(uid):
            netstream.send(self.connections[usid]['connection'], {
                "code": 6}) # code 6 for in black list
        else:
            user = self.allUsers[uid]
            netstream.send(self.connections[usid]['connection'], {
                "code": 1,
                "username": user['username'],
                "score": user['best_score'],
                "time": user['best_time'],
                "num": user['best_num']}) # code 1 for success
            self.logger.log("Get user information successfully.", usid)

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
        self.logger.log("Get leaderboard successfully.", usid)
