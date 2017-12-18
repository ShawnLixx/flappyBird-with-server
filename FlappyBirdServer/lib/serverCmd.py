# -*- coding: utf-8 -*-
import cmd
from functools import wraps
from argumentParser import ArgumentParser
import hashlib, traceback

INF = float('inf')

def _getMD5(s):
    MD5 = hashlib.md5()
    MD5.update(s)
    return MD5.hexdigest()


class ServerCmd(cmd.Cmd, object):
    # A command line handler for server.
    def __init__(self, server):
        super(ServerCmd, self).__init__()
        self.server = server
        self.prompt = "FlappyServer> "
        self.intro = "***Enter command line environment for server manager.***\n" \
        "==============================================================\n" \
        "List of supported command:\n" \
        "cllog:  Clear log.\n" \
        "help:   Print all command and get help.\n" \
        "log:    Show server log.\n" \
        "ls:     Show details of all current connections.\n" \
        "lsblk:  Show details of users in black list.\n" \
        "muser:  Modify user. Change user profile, remove user, add/remove user to/from black list.\n" \
        "notice: Change server notice.\n" \
        "nuser:  Create new users.\n" \
        "server: Change or show server status(start, stop, restart).\n" \
        "user:   Search user under conditions(substring of name, range of best score, " \
        "longest survive time, greatest number of passed pipes).\n" \
        "==============================================================\n" \
        '''Enter "help <command>" to show detail of command usage.'''

        # init some argument parsers for command
        # user command
        self.userParser = ArgumentParser(
                prog = "user",
                description = 'Search for users with restrictions.',
                epilog = "-1 is used in above MAX, N for no limit.")
        self.userParser.add_argument("--name", default = "", type = str,
                help = "username containing certain string.")
        self.userParser.add_argument("--score", default = [0, -1], type = int,
                nargs = 2, metavar = ("MIN", "MAX"),
                help = "user best score in [MIN, MAX), input should be integer.")
        self.userParser.add_argument("--time", default = [0, -1], type = int,
                nargs = 2, metavar = ("MIN", "MAX"),
                help = "user longest surviving time in [MIN, MAX), input should be integer.")
        self.userParser.add_argument("--num", default = [0, -1], type = int,
                nargs = 2, metavar = ("MIN", "MAX"),
                help = "user greatest number of passed pipes in a single game in [MIN, MAX), " \
                        "input should be integer.")
        self.userParser.add_argument("-n", default = -1, type = int,
                help = "show first N users of results, input should be integer.")


        # muser command
        self.muserParser = ArgumentParser(
                prog = "muser",
                description = 'Modify user and user profile.')
        self.muserParser.add_argument("uid", type = int, #required = True,
                help = "uid of user to be modified.")
        self.muserParser.add_argument("--name", type = str, 
                help = "modify username.")
        self.muserParser.add_argument("--score", type = int,
                help = "modify user best score, input should be integer.")
        self.muserParser.add_argument("--time", type = int,
                help = "modify user longest surviving time, input should be integer.")
        self.muserParser.add_argument("--num", type = int,
                help = "modify user greatest number of passed pipes, input should be integer.")
        self.muserParser.add_argument("--rm", action = "store_true",
                help = "remove user from database.")
        self.muserParser.add_argument("--addbl", action = "store_true",
                help = "put user in black list.")
        self.muserParser.add_argument("--rmbl", action = "store_true",
                help = "remove user from black list.")
        
        # nuser command
        self.nuserParser = ArgumentParser(
                prog = "nuser",
                description = 'Create a new user.')
        self.nuserParser.add_argument("username", type = str,
                help = "username of new user.")
        self.nuserParser.add_argument("password", type = str,
                help = "password of new user.")


        # log command
        self.logParser = ArgumentParser(
                prog = "log",
                description = 'Show server logs.')
        self.logParser.add_argument("-n", default = 10, type = int,
                help = "show last N lines of log, 10 default.")


        # server command
        self.serverParser = ArgumentParser(
                prog = "server",
                description = 'Show or change server status.')
        self.serverParser.add_argument("-o", type = str,
                help = '''passible operations: "start", "stop", "restart".''',
                metavar = "OPERATION")
        self.serverParser.add_argument("--status", action = "store_true",
                help = "show server status.")

    
    # exception handle
    def cmdloop(self, intro=None):
        try:
            super(ServerCmd, self).cmdloop(intro = intro)
        except Exception:
            traceback.print_exc()
            self.lock.release()
            self.server._exit()


    def do_EOF(self, line):
        """Enter ctrl+d to exit this environment.
        (Note: Server will also be stopped.)"""
        self.server._exit()
        return True


    # decorator to address thread lock is needed.
    def lockNeed(fun):
        @wraps(fun)
        def wrapper(self, *args, **kwargs):
            self.server.lock.acquire()
            fun(self, *args)
            self.server.lock.release()
        return wrapper


    # show logs from server
    @lockNeed
    def do_log(self, line):
        args = self.logParser.parse_args(line.split())
        if args != None:
            print(self.server.logger.readLastN(args.n))
    def help_log(self, line):
        self.logParser.print_help()


    # clear log
    @lockNeed
    def do_cllog(self, line):
        """cllog
        clear logs."""
        self.server.logger.clearLog()
        print("Log cleared.")

    
    # List current online gamers.
    @lockNeed
    def do_ls(self, line):
        """ls
        List all online gamers."""
        allConnections = self.server.connections
        print("Total {} connections.".format(len(allConnections)))
        print("=" * 40)
        # print information grouped by logined or not
        loginedConnections = {}
        annoymousConnections = {}
        for sid in allConnections:
            if allConnections[sid]['uid'] == -1:
                annoymousConnections[sid] = allConnections[sid]
            else:
                loginedConnections[sid] = allConnections[sid]
        # for logined connections
        print("Total {} logined connections.".format(len(loginedConnections)))
        print("{:<6} {:<6} {:<15} {:<8} {:<8} {:<8} {:<12} {:<15} {:<6}".format('Sid', 'Uid', 
            'Username','Score', 'Time', 'Number', 'Online time', 'Address', 'Port'))
        for sid in loginedConnections:
            uid = loginedConnections[sid]['uid']
            user = self.server.allUsers[uid]
            c = loginedConnections[sid]
            print("{:<6} {:<6} {:<15} {:<8} {:<8.2f} {:<8} {:<12.2f} {:<15} {:<6}".format(sid, uid, user['username'],
                user['best_score'], user['best_time'], user['best_num'], 
                c['timeStamp'] - c['startTime'], c['addr'][0], c['addr'][1]))
        print("=" * 40)
        # for annoymous connections
        print("Total {} annoymous connections.".format(len(annoymousConnections)))
        print("{:<6} {:<12} {:<15} {:<6}".format('Sid', 'Online time', 'Address', 'Port'))
        for sid in annoymousConnections:
            c = annoymousConnections[sid]
            print("{:<6} {:<12.2f} {:<15} {:<6}".format(sid, c['timeStamp'] - c['startTime'],
                c['addr'][0], c['addr'][1]))
        print("\nNote: In the above table, 'Score', 'Time', 'Number', 'Online time' stand for" \
            "best game score, longest game time, best number of passed pipes," \
            "online time since connected to server. And the unit of 'Time' and 'Online time'" \
            "is second.")

    
    # User related
    
    # format user information display
    def _formatUsers(self, users):
        print("{} users are selected from a total of {} users.".format(len(users),
            len(self.server.allUsers)))
        print("=" * 40)
        print("{:<6} {:<15} {:<8} {:<8} {:<8}".format('Uid', 
            'Username','Score', 'Time', 'Number'))
        for (uid, user) in users:
            print("{:<6} {:<15} {:<8} {:<8.2f} {:<8}".format(uid, user['username'],
                user['best_score'], user['best_time'], user['best_num']))
        print("\nNote: In the above table, 'Score', 'Time', 'Number' stand for" \
            "best game score, longest game time, best number of passed pipes," \
            "And the unit of 'Time' and is second.")


    # list users according to regulation
    @lockNeed 
    def do_user(self, line):
        args = self.userParser.parse_args(line.split())
        if args != None:
            def filterUser(tp):
                return self._filterUser(tp[1], args.name, args.score,
                        args.time, args.num)
            results = filter(filterUser, self.server.allUsers.iteritems())
            # get first n
            if args.n >= 0:
                results = results[:args.n]
            # print result
            self._formatUsers(results)
            
    def help_user(self):
        self.userParser.print_help()

    def _filterUser(self, user, name, score, time, num):
        # -1 for infinit max
        for i in (score, time, num):
            i[1] = INF if i[1] == -1 else i[1]
        return name in user['username'] and \
                score[0] <= user['best_score'] < score[1] and \
                time[0] <= user['best_time'] < time[1] and \
                num[0] <= user['best_num'] < num[1]
    
    # manage users
    @lockNeed
    def do_muser(self, line):
        args = self.muserParser.parse_args(line.split())
        if args != None:
            uid = args.uid
            uid = str(uid)
            # check uid exists
            if self.server._uidCheck(uid):
                if args.rm:
                    # remove user
                    self.server._delUser(uid)
                    print("User deleted.")
                else:
                    if args.name:
                        # username already in use
                        if self.server._usernameInUseCheck(args.name):
                            print("Error: User name already in use!")
                        else:
                            self.server.allUsers[uid]['username'] = args.name
                            print("User name modified.")
                    if args.score:
                        if args.score < 0:
                            print("Error: score should not be less than 0!")
                        else:
                            self.server.allUsers[uid]['best_score'] = args.score
                            print("Best score modified.")
                    if args.time:
                        if args.time < 0:
                            print("Error: time should not be less than 0!")
                        else:
                            self.server.allUsers[uid]['best_time'] = args.time
                            print("Longest time modified.")
                    if args.num:
                        if args.num < 0:
                            print("Error: num should not be less than 0!")
                        else:
                            self.server.allUsers[uid]['best_num'] = args.num
                            print("Greatest number of passed pipes modified.")
                    if args.addbl:
                        if self.server._addToBlack(int(uid)):
                            print("User added to black list.")
                        else:
                            print("Error: User already in black list!")
                    if args.rmbl:
                        if self.server._rmFromBlack(int(uid)):
                            print("User removed from black list.")
                        else:
                            print("Error: User not in black list!")
            else:
                print("Input uid invalid!")

    def help_muser(self):
        self.muserParser.print_help()

    # create new user
    def do_nuser(self, line):
        args = self.nuserParser.parse_args(line.split())
        if args != None:
            if self.server._registration(args.username, _getMD5(args.password)) == 2:
                print("Username already in use!")
            else:
                print("User created successfully.")
    def help_nuser(self):
        self.nuserParser.print_help()



    # List black list
    @lockNeed
    def do_lsblk(self, line):
        """lsblk
        List all users in black list."""
        users = [(uid, self.server.allUsers[str(uid)]) for uid in self.server.blackList]
        self._formatUsers(users)


    # server related command
    def do_server(self, line):
        args = self.serverParser.parse_args(line.split())
        if args != None:
            # server operations
            if args.o:
                if args.o == "start":
                    if self.server.runRequestHandle:
                        print("Server already started!")
                    else:
                        self.server._startRequestHandleThread()
                elif args.o == "stop":
                    if not self.server.runRequestHandle:
                        print("Server not start yet!")
                    else:
                        self.server._endRequestHandleThread()
                elif args.o == "restart":
                    if not self.server.runRequestHandle:
                        print("Server not start yet!")
                    else:
                        self.server._endRequestHandleThread()
                        self.server._startRequestHandleThread()
                else:
                    print('''Operation not valid! Use "help server" to see valid values.''')
            # show server status
            if args.status:
                if self.server.runRequestHandle:
                    print("Server is running at {}:{} with {} connections currently.\nServer Notice: {}".format(
                        self.server.host, self.server.port, len(self.server.connections), self.server.notice))
                else:
                    print("Server is stopped.")

    def help_server(self):
        self.serverParser.print_help()


    # set notice
    @lockNeed
    def do_notice(self, line):
        """notice NOTICE_TEXT
        Set new server notice."""
        self.server._setNotice(line)
        print("Set new server notice: {}".format(self.server.notice))
