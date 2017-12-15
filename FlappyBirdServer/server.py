# -*- coding: utf-8 -*-
import sys, argparse
from lib.flappyServer import FlappyServer

# Parse argumnets for host and port
argParser = argparse.ArgumentParser(
        prog = "server",
        description = "A Server for flappy bird game.")
argParser.add_argument("--host", default = "127.0.0.1", type = str,
        help = "Set a specific host, 127.0.0.1 default.")
argParser.add_argument("--port", default = 9234, type = int,
        help = "Set a specific port, 9234 default.")
argParser.add_argument("--timeout", default = 60, type = int,
        help = "Timeout for each client session in seconds, 60 default." \
                "Must be positive.")
argParser.add_argument("--saving_gap", default = 300, type = int,
        help = "Gap of saving server data to disk in seconds, 300 default." \
                "Must be positive.")



if __name__ == "__main__":
    args = argParser.parse_args(sys.argv[1:])
    if args.port <= 0 or args.timeout <= 0 or args.saving_gap <= 0:
        print("Port and times must be positive!")
    else:   
        ser = FlappyServer(args.host, args.port, args.timeout, args.saving_gap)
        ser.run()
