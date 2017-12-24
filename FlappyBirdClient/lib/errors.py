# -*- coding: utf-8 -*-

# constant ERRORS
NOT_CONNECTED = "Client not connected to the server!"
USERNAME_EXIST = "Username already exits in server!"
USER_NOT_FOUND = "Username not exits in server!"
PASSWORD_ERROR = "Password is wrong!"
SESSION_NOT_INIT = "Connection from server is broken!"
TOKEN_ERROR = "Authentication failed, please login again!"
NETWORK_ERROR = "Network Error, check your network settings or server may be shutdown!"
BLOCKED = "You are in the black list of the server! Please contact the admin!"
SESSION_TIMEOUT = "Your session is removed by server because of timeout, please restart the game!"

def getErrorString(code):
    if code == -1:
        return NETWORK_ERROR
    elif code == 0:
        return SESSION_NOT_INIT
    elif code == 2:
        return USERNAME_EXIST
    elif code == 3:
        return USER_NOT_FOUND
    elif code == 4:
        return PASSWORD_ERROR
    elif code == 5:
        return TOKEN_ERROR
    elif code == 6:
        return BLOCKED
    elif code == 7:
        return SESSION_TIMEOUT
