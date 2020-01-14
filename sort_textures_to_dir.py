import os
import shutil

DIR = "/home/ranjian0/Downloads/TEXTURES"
TEXTURES = sorted(os.listdir(DIR))

import pprint as pp
pp.pprint(TEXTURES)

for i in range(0, len(TEXTURES), 3):
    group = TEXTURES[i:i+3]

    root_name = "_".join(group[0].split('_')[:-2])
    os.mkdir(os.path.join(DIR, root_name))
    for file in group:
        fp = os.path.join(DIR, file)
        shutil.move(fp, os.path.join(DIR, root_name, file))
