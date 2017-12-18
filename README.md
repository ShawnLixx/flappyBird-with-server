# flappyBird-with-server

A Flappy Bird game developed under `cocos-2d` with client-server model to exchange data between client and server.
This project mainly targets to Mobile and Network Programming Practice course from SYSU.

## Introduction

This project contains a copy of Flappy Bird game and we made contributions to enhance the simple game with client-server model.
We developed a simple server and modify Flappy Bird game to a client.

<img src="/screenshots/client.png" height="400px">

Main features:

* Three levels of difficulty available.
* User and account system.
* Score record upload/download to/from server.
* Leaderboard of users.
* Notification from server.
* Simple Encryption for user information.
* A command-line tool for server management.

There are three levels of difficulty available, pipes are generated randomly according to difficulty and it's guaranteed that
the bird can pass pipes randomly generated.

Interactions between server and logined clients are based on tokens to improve the security of sessions. User password is encrypted
using MD5 and our server stores only MD5 encrypted password.

According to the requirement from our course, we made the following compromise:

* File-based database.
* Simple server based on python built-in `socket` library. (No additional third-party library is allowed.)
* Python2. (Encoding issues may occur when using languages besides English.)

Since we mainly contribute to meet the requirements from our course, functional implementation is considered preferentially and
Optimization for server is not paid principally attention. These issues may or may not be solved in future works according to
the author.

## User Guide

### requirements

* `Python2` >= 2.7.14:

    Run `python --version` in command-line to check if your python version satifies the requirement. If not, visit 
    [Python Offical Site](https://www.python.org/) to see python installation guide.

* `Cocos-2d` 0.6.5:

    This dependency is only required for the client side. Run `pip install cocos2d --user` to install cocos-2d to current user.

### Client Usage

Enter `FlappyBirdClient` directory first. You can click `start_client.bat` to start client on Windows operating system.

Generally, on all systems that are supported by `Python2` and `Cocos-2d`, use the following command to start the client:

```
python FlappyBird.py [-h] [--host HOST] [--port PORT]
```

Specify the host and port of server to connect by arguments `--host HOST --port PORT`. If not specified, the defalut port to 
connect is `127.0.0.1:9234` as well as the default arguments for server.

A GUI environment is required to start the graphical Flappy Bird client.

### Server usage

Enter `FlappyBirdServer` directory first. And you can start server on Windows by clicking `start\_server.bat`.

It's recommanded to use command-line to start the server with the following command:

```
python server.py [-h] [--host HOST] [--port PORT] [--timeout TIMEOUT]
              [--saving_gap SAVING_GAP]
```

`TIMEOUT` argument is used for determine whether a connection is lost. The server will automaticly disconnect from connections
that haven't send request after `TIMEOUT` seconds since last request. To avoid data loss, our server writes server data to disk
every `SAVING_GAP` seconds. The default values of `TIMEOUT` and `SAVING_GAP` are 60 and 300.

After start our server using command-line or click `start\_server.bat`, a command-line server manangement tool will start. There
are commands you can use to manage the server and modify user accounts. All commands are shown when you enter the command-line
environment as below:

```
***Enter command line environment for server manager.***
==============================================================
List of supported command:
cllog:  Clear log.
help:   Print all command and get help.
log:    Show server log.
ls:     Show details of all current connections.
lsblk:  Show details of users in black list.
muser:  Modify user. Change user profile, remove user, add/remove user to/from black list.
notice: Change server notice.
nuser:  Create new users.
server: Change or show server status(start, stop, restart).
user:   Search user under conditions(substring of name, range of best score, longest survive time, greatest number of passed pipes.
==============================================================
Enter "help <command>" to show detail of command usage.

```

Follow these instructions and enjoy our Flappy Bird with Server.
