#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import socket, json, base64

# constants
TIMEOUT = -1
CLOSED = -2
EMPTY = -3    #means read empty data

# param: sock, dict
# return: 1-success TIMEOUT-timeout CLOSED-closed EMPTY-empty
def send(sock, dic):  # take dict as argument!!
    try:
        sock.send(pack(dic))
    except socket.error as (err_code, err_message):
        if err_code == 9:
            return CLOSED
        else:
            return TIMEOUT
    return 1

# param: sock
# return: table-success TIMEOUT-timeout CLOSED-closed EMPTY-empty
def read(sock):
    #读取三位的长度信息
    sock.setblocking(1)
    sock.settimeout(1)
    try:
        length = sock.recv(3)
        #读取到''说明socket另一头被关闭
        if length == '':
            return CLOSED
    
        length = int(length)
        if length == 0:
            return EMPTY

    except socket.timeout:
        return TIMEOUT
    except socket.error:
        return CLOSED
        
    #根据长度信息读取数据
    try:
        data = sock.recv(length)
    except socket.error as (err_code, err_message):
        #异常处理
        if err_code == 35:
            return TIMEOUT
        elif err_code == 54:
            return CLOSED
        elif err_code == 9:
            return CLOSED
        else:
            return TIMEOUT
    #读取到''说明socket另一头被关闭
    if data == '':
        return CLOSED
    
    #解析数据
    return unpack(data)

# 功能：对输入的dict使用json转换 使用base64加密 加上长度信息
# 输入：dict
# 输出：string
def pack(dic):
    # 转换成json
    jsonData = json.dumps(dic)
    # base64加密
    jsonData = base64.b64encode(jsonData)
    # 加上头部信息
    length = len(jsonData)
    string = None
    if length < 10 and length > 0:
        string = "00"+str(length)+jsonData
    elif length < 100:
        string = "0"+str(length)+jsonData
    elif length < 1000:
        string = str(length)+jsonData
    else:
        string = "000"
    return string
    
# 功能：对输入的string（不含长度信息） 进行base64解密 再用json转换 得到dict
# 输入string
# 输出dict
def unpack(string):
    # base64解密
    jsonData = base64.b64decode(string)
    # json解析
    dic = json.loads(jsonData)
    return dic
