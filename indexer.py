import posting as posting
import bs4 as bs
import os  # allows us to get the directories and file names

def test():
    for (root, dirs, files) in os.walk('./DEV', topdown=True):
        for file in files:
            print('Tokenize and index me: ' + str(root) + str(file))

def run():
        test()

run()
