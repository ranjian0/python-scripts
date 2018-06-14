#!/usr/bin/env python
import os, sys, time
import argparse
from urllib.request import urlopen

import pytube  # pip install pytube


CS294_playlist_url = "https://www.youtube.com/playlist?list=PLjArG72MRbUVLP4mQRt0kqH8e3QRJ2cEf"


def get_playlist_links(playlist_url):
    page_elements = urlopen(playlist_url).readlines()
    video_elements = [str(el) for el in page_elements if 'pl-video-title-link' in str(el)]  # Filter out unnecessary lines
    video_urls = [v.split('href="',1)[1].split('" ',1)[0] for v in video_elements]  # Grab the video urls from the elements
    return ['http://www.youtube.com' + v for v in video_urls]


start_time = time.time()

def print_dot(stream, chunk, file_handle, bytes_remaining):
    global start_time
    if time.time() - start_time > 1.0:
        sys.stdout.write(str(bytes_remaining/1000000) + ' MB\n')
        sys.stdout.flush()
        start_time = time.time()


parser = argparse.ArgumentParser(usage='%(prog)s [-h] [-p PLAYLISTURL] [-d DESTINATION]')
parser.add_argument('-p', '--playlisturl', help='url of the playlist to be downloaded', default=CS294_playlist_url, metavar='')
parser.add_argument('-d', '--destination', help='path of directory to save videos to', default=os.path.curdir, metavar='')
args = parser.parse_args()


if os.path.exists(args.destination):
    directory_contents = [f.split('.mp4',1)[0] for f in os.listdir(args.destination) if f.endswith('.mp4')]
else:
    print('Destination directory does not exist')
    sys.exit(1)

video_urls = get_playlist_links(args.playlisturl)
confirmation = input('You are about to download {} videos to {}\nWould you like to continue? [Y/n] '.format(
    len(video_urls), os.path.abspath(args.destination)))

if confirmation.lower() in ['y', '']:
    for u in video_urls:
        yt = pytube.YouTube(u)
        yt.register_on_progress_callback(print_dot)
        vid = yt.streams.filter(subtype='mp4').all()[-1]

        if vid.default_filename in directory_contents:
            print('Skipping {}'.format(vid.default_filename))
            continue
        else:
            print('Downloading {}'.format(vid.default_filename))

            vid.download(args.destination) #, on_progress=print_dot)
            print('Done')
