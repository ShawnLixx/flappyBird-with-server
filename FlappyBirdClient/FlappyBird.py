#! /usr/bin/env python

import sys, argparse
import os

# Parse argumnets for host and port
argParser = argparse.ArgumentParser(
        prog = "FlappyBird",
        description = "Flappy bird game client.")
argParser.add_argument("--host", default = "127.0.0.1", type = str,
        help = "Set a specific host, 127.0.0.1 default.")
argParser.add_argument("--port", default = 9234, type = int,
        help = "Set a specific port, 9234 default.")

from lib import main
if __name__ == "__main__":
    args = argParser.parse_args(sys.argv[1:])
    if args.port <= 0:
        print("Port must be positive!")
    else:
        main.main(args.host, args.port)
