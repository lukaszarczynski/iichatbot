# coding=utf-8
from __future__ import print_function, unicode_literals, division

import sys

CONSOLE_WIDTH = 80


def progress_bar(console_width=CONSOLE_WIDTH):
    """Draw console progress bar"""
    print(" " * (console_width - 1), "|", sep="", file=sys.stderr)
    print(" " * (console_width - 1), "|", "\b" * console_width, sep="", end="", file=sys.stderr)

    def print_progress(progress):
        """Draw one character into progress bar if needed"""
        while progress >= print_progress.already_printed / console_width:
            print("=", end='', file=sys.stderr)
            sys.stderr.flush()
            print_progress.already_printed += 1

    print_progress.already_printed = 0
    return print_progress