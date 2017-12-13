# -*- coding: utf-8 -*-
import os
import json
import hashlib

from network import send_message

# constants
DIR = "userData"
USERFILE = "userInfo.json"

class Account:
    def __init__(self):
        # check directory existance.
        if not os.path.isdir(DIR):
            os.mkdir(DIR)
        # check if there is already a user file.
        self.path = os.path.join(DIR, USERFILE)
        try:
            with open(path, "r") as f:
                userData = json.load(f)

            self.username = userData["username"]
            self.uid = userData["uid"]
            self.token = userData["token"]
            self.best_score = userData["best_score"]
            self.best_num = userData["best_num"]
            self.best_time = userData["best_time"]

        except:
            # user file dose not exist or is destroyed.
            print("User file does not exist or is destroyed.")
            self.username = "anonymous"
            self.uid = -1
            self.token = ""
            self.best_score = 0
            self.best_num = 0
            self.best_time = 0
            self.save() # save to file

    def save(self):
        with open(self.path, "w") as f:
            json.dump({
                    "username": self.username,
                    "uid": self.uid,
                    "token": self.token,
                    "best_score": self.best_score,
                    "best_num": self.best_num,
                    "best_time": self.best_time}, f)

