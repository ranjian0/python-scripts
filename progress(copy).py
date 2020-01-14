import sys
import time
import shutil

def progress(count, total, prefix="", suffix=""):
    size = shutil.get_terminal_size((80, 20))

    if prefix != "":
        prefix = prefix + "    "
    if suffix != "":
        suffix = "    " + suffix

    bar_len = size.columns - len(prefix) - len(suffix) - 10
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('%s[%s] %s%%%s\r' % (prefix, bar, percents, suffix))
    sys.stdout.flush()

def progress_clear():
    size = shutil.get_terminal_size((80, 20))
    sys.stdout.write(" " * size.columns + "\r")
    sys.stdout.flush()


for i in range(100):
    time.sleep(0.25)
    progress(i+1, 100)
progress_clear()
