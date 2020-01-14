import os
import sys
import time

DIR   = "/media/ranjian0/Backup/Music/__UNSORTED/New folder"
# ~ DIR = "/media/ranjian0/8545-1AE3/Oldies"
JOIN  = os.path.join
FILES = os.listdir(DIR)
YEAR  = time.localtime().tm_year

def main():
    new_names, old_names = [], []
    for f in FILES:
        if os.path.isdir(JOIN(DIR, f)):
            continue

        # -- replace underscores with spaces
        underscore, fn = remove_underscore(f)

        # -- make file names title case
        title, fn = make_title_case(fn)

        # -- remove all phrases enclosed in brackets
        brackets, fn = remove_brackets(fn)

        # -- fix empty space before extension
        space, fn = fix_empty_spaces(fn)

        # -- remove null phrase
        null, fn = remove_null_phrases(fn)

        # -- if the filename changes, inform user that we are fixing it
        old_names.append(f)
        new_names.append(fn)
        if fn != f:
            print("FIXING: ", f)
            if underscore:
                print(f"Removed underscores: \t\t{fn}")
            if title:
                print(f"Made TitleCase: \t\t{fn}")
            if brackets:
                print(f"Removed brackets: \t\t{fn}")
            if space:
                print(f"Removed whitespace: \t\t{fn}")
            if null:
                print(f"Removed null phrases: \t\t{fn}")


    # Rename files, if any changed
    if set(new_names) - set(old_names):
        do_rename = input("Rename files to fix all issues (Y/n)?")
        if do_rename.lower() in ('y', 'yes', ''):
            for new, old in zip(new_names, old_names):
                os.rename(JOIN(DIR, old), JOIN(DIR, new))

    # Duplicate Finder
    # ~ print("\n\nFINDING DUPLICATES:")
    # ~ check_duplicates(os.listdir(DIR))

    return 0

def remove_underscore(file):
    n = file.replace("_", " ")
    if n != file:
        return True, n
    return False, file

def make_title_case(file):
    n = file.title()
    if n != file:
        return True, n
    return False, file

def remove_brackets(file):
    b_start = ['(', '[', '{']
    b_end = [')', ']', '}']
    original_file = file
    if not any(b in file for b in b_start):
        return False, file

    idx = 0
    n = file
    while idx < len(b_start):

        try:
            start = file.index(b_start[idx])
        except ValueError:
            n = file.replace(b_end[idx], "")
            idx += 1
            file = n
            continue

        #XXX Start was found, check if end exists
        try:
            end = file.index(b_end[idx])
        except ValueError:
            # -- Just remove start and move on
            n = file.replace(b_start[idx], "")
            idx += 1
            file = n
            continue

        # An open and close bracket exists
        bracket = file[start:end+1]
        if any(tag in bracket for tag in ['Feat. ', 'Ft. ']):
            # -- this is important, just replace the brackets with empty space
            n = file.replace(bracket, bracket[1:-1])
        else:
            # -- remove the while bracket phrase
            n = file.replace(bracket, "")
        file = n
        idx += 1

    if n != original_file:
        return True, n
    return False, file

def fix_empty_spaces(file):
    rev = file[::-1]
    ext, *f = rev.split('.')

    corrected = ".".join(f)[::-1]
    n = corrected.strip()+'.'+ext[::-1]
    if n != file:
        return True, n
    return False, file

def remove_null_phrases(file):
    redundant = ['Mp3', 'Official', 'Music', 'Video', 'Lyrics', 'Tribute', '128', 'Kbps', 'Full', 'Hd']
    phrases = file.split(" ")
    *n, ext = phrases[-1].split('.')
    all_phrases = phrases[:-1] + n

    for ph in [p for p in all_phrases]:
        # -- remove large numbers
        try:
            num = int(ph)
        except ValueError:
            num = None

        if num and num > YEAR:
            all_phrases.remove(ph)

        # -- remove redundant phrases
        if ph in redundant:
            all_phrases.remove(ph)

    n = " ".join(all_phrases).strip() + "." + ext
    if n != file:
        return True, n
    return False, file


def check_duplicates(files):

    cache_phrases = [f.split(" ") for f in files]
    delete_queue = []
    for idx, file in enumerate(files):
        phrases = file.split(" ")

        for cidx, cache_phrase in enumerate(cache_phrases):
            # -- skip the cache_phrase of this file
            if cidx == idx:
                continue

            # -- compare this file's phrases against all the rest
            comparison = set(phrases).difference(set(cache_phrase))
            percent_match = (len(phrases) - len(comparison)) / len(phrases)

            if percent_match > .9:
                print(f"Found Duplicate: Match: {percent_match*100} %")
                print(f"\t Original  (O): {file}")
                print(f"\t Duplicate (D): {' '.join(cache_phrase)}\n")


                do_delete = input("Remove file: (D - remove duplicate, O - remove original, Enter to skip) :")
                if do_delete.lower() in (''):
                    pass
                elif do_delete.lower() in ('d'):
                    # -- remove the duplicate file found
                    dup_file = JOIN(DIR, " ".join(cache_phrase))
                    delete_queue.append(dup_file)
                elif do_delete.lower() in ('o'):
                    # -- remove the original file
                    original_file = JOIN(DIR, file)
                    delete_queue.append(original_file)

    #XXX Delete all the files in the delete queue
    print("\n\n DELETING FILES [!! THIS ACTION IS IRREVESRIBLE]")
    for file in delete_queue:
        if os.path.exists(file):
            print(f"\tdeleting ... {file}")
            os.remove(file)

if __name__ == '__main__':
    sys.exit(main())
