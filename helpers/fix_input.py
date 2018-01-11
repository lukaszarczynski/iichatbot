import sys


def fix_input():
    if sys.version_info.major < 3:
        global input

        def input(*args, **kwargs):
            """input function similar to one from Python 3"""
            return raw_input(*args, **kwargs).decode("utf8")

        return input

    else:
        return input