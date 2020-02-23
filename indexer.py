import posting as posting
import bs4 as bs
from bs4 import BeautifulSoup
import os  # allows us to get the directories and file names
import json
import nltk

#if this line is causing errors but you have nltk installed
#open idle and do 'import nltk' then 'nltk.download('punkt')
from nltk.tokenize import word_tokenize
def extractHtmlFromJson(filePath):
    json_data = open(filePath)
    #print('Loading data from: ' + filePath)
    try:
        # { url, content, encoding }
        data = json.load(json_data)
        #load the html into BeautifulSoup
        soup = BeautifulSoup(data['content'])

        #strip out the javscript and some style tags from the html file
        for garbage in soup(['script', 'style']):
            garbage.decompose()
        text = soup.get_text() 
        listOfTokens = word_tokenize(text)

        print(listOfTokens)
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
