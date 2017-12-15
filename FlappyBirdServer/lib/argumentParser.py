# -*- coding: utf-8 -*-
import argparse
import sys
class ArgumentParser(argparse.ArgumentParser):

    def error(self, message):
        self.print_help(sys.stderr)
        self.exit(2, '%s: error: %s\n' % (self.prog, message))

    def parse_args(self, arg):
        try:
            return super(ArgumentParser, self).parse_args(arg)
        except SystemExit:
            pass
