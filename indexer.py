import posting as posting
import bs4 as bs
import os  # allows us to get the directories and file names
import json

def extractHtmlFromJson(filePath):
    json_data = open(filePath)
    encoding_types = {}
    #print('Loading data from: ' + filePath)
    try:
        data = json.load(json_data)
        #print(data['url'])
        #print(data['encoding'])
        print(data['content']) # <-- Tokenize this
         
    except ValueError as e:
        return

# runs through all directories and prints out a list of files within them.
def traverseDirectories():
    for (root, dirs, files) in os.walk('./DEV', topdown=True):
        for file in files:
            extractHtmlFromJson(root + '/' + file)

def run():
        traverseDirectories()
            
run()
