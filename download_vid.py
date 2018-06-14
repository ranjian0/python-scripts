import sys
import time

import pytube as pt


url = "https://www.youtube.com/watch?v=EbT13dznkOM"
dest = "/home/ranjian0/Videos/MUSIC/YOUTUBE CLASSICS"

start_time = time.time()

def print_dot(stream, chunk, file_handle, bytes_remaining):
    global start_time
    if time.time() - start_time > 1.0:

        res = "Downloading -> {} MB Remaining \n".format(str(bytes_remaining/1000000))
        sys.stdout.write(res)
        sys.stdout.flush()
        start_time = time.time()


yt = pt.YouTube(url)
yt.register_on_progress_callback(print_dot)
vid = yt.streams.filter(subtype='mp4').all()[-1]

vid.download(dest)
