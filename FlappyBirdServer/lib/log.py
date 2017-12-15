# -*- coding: utf-8 -*-
import os, datetime

LOG_DIR = "serverData"
LOG_FILE = "log.txt"

class Log:
    def __init__(self):
        # reload data from file
        if not os.path.isdir(LOG_DIR):
            os.mkdir(LOG_DIR)
        self.path = os.path.join(LOG_DIR, LOG_FILE)
        self.file = open(self.path, "a+")

    def log(self, s, usid = None):
	# move file pointer to the end of the file
	self.file.seek(0, 2)
        # write information to file
        if usid: # from user request
            self.file.write("[{}]:<sid: {}> {}\n".format(str(datetime.datetime.now()), usid, s))
        else:
            self.file.write("[{}]: {}\n".format(str(datetime.datetime.now()), s))


    def readLastN(self, n):
        return tail(self.file, n)

    def clearLog(self):
        self.file.truncate(0)
        
    def __del__(self):
        # close file
        self.file.close()


# get last n lines of a file
def tail( f, lines=20 ):
    total_lines_wanted = lines

    BLOCK_SIZE = 1024
    f.seek(0, 2)
    block_end_byte = f.tell()
    lines_to_go = total_lines_wanted
    block_number = -1
    blocks = [] # blocks of size BLOCK_SIZE, in reverse order starting
                # from the end of the file
    while lines_to_go > 0 and block_end_byte > 0:
        if (block_end_byte - BLOCK_SIZE > 0):
            # read the last block we haven't yet read
            f.seek(block_number*BLOCK_SIZE, 2)
            blocks.append(f.read(BLOCK_SIZE))
        else:
            # file too small, start from begining
            f.seek(0,0)
            # only read what was not read
            blocks.append(f.read(block_end_byte))
        lines_found = blocks[-1].count('\n')
        lines_to_go -= lines_found
        block_end_byte -= BLOCK_SIZE
        block_number -= 1
    all_read_text = ''.join(reversed(blocks))
    return '\n'.join(all_read_text.splitlines()[-total_lines_wanted:])
