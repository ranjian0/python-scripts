import os
import filecmp

DIR = '/media/ranjian0/Backup/Music/__UNSORTED/New folder'
os.chdir(DIR)

files = [f for f in os.listdir() if os.path.isfile(f)]
print(len(files))
for f1 in files:
    for f2 in files:
        if f1 != f2:
            cmp = filecmp.cmp(f1, f2, False)
            if cmp:
                print(f1, f2)
