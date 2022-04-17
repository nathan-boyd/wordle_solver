#!/usr/bin/env python3

import logging
import os
import mmap

COMMON_WORDS_FILE_PATH = "/Users/nboyd/git/google-10000-english/google-10000-english-usa-no-swears-medium.txt"
ALLOWED_STRINGS_FILE = f"/Users/nboyd/git/wordle_bot/allowed_strings.txt"
NEW_ALLOWED_STRINGS_FILE = f"/Users/nboyd/git/wordle_bot/allowed_strings_new.txt"


class Handler:

    def check_files(self, path):
        if not os.path.exists(path):
            raise Exception(f"path does not exist {path}")
        else:
            self.logger.info(f"path exists {path}")

    def priortize_words(self):

        replacement = ""
        count = 0
        with open(ALLOWED_STRINGS_FILE) as allowed_words_file:
            with open(COMMON_WORDS_FILE_PATH) as common_words_file, mmap.mmap(common_words_file.fileno(), 0,
                                                                              access=mmap.ACCESS_READ) as s:
                for line in allowed_words_file:
                    word_on_line = line.split(',')[1]
                    if s.find(str.encode(word_on_line)) != -1:
                        changes = line.replace(line, f"1,{word_on_line}")
                        count += 1
                    else:
                        changes = line.replace(line, f"0,{word_on_line}")
                    replacement += changes
        self.logger.info(f"found {count} common words")
        fout = open(NEW_ALLOWED_STRINGS_FILE, "w")
        fout.write(replacement)
        fout.close()

    def __init__(self):

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
            handlers=[
                logging.FileHandler("debug.log"),
                logging.StreamHandler()
            ]
        )

        self.logger = logging.getLogger()

        self.check_files(COMMON_WORDS_FILE_PATH)
        self.check_files(ALLOWED_STRINGS_FILE)


if __name__ == '__main__':
    h = Handler()
    h.priortize_words()
