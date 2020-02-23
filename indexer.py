import posting as posting
import bs4 as bs
from bs4 import BeautifulSoup
import os  # allows us to get the directories and file names
import json
import nltk
from bs4.element import Comment
from collections import defaultdict
nltk.download('stopwords')
nltk.download('punkt')
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer

currentDocId = 0
currentFileNum = 0
if os.path.isdir('./DocIdMap'):
    currentIndexFile = open('./DocIdMap/' + str(currentFileNum) + '.txt', 'a')
else:
    os.mkdir(os.getcwd() + '/' + 'DocIdMap')
    currentIndexFile = open('./DocIdMap/' + str(currentFileNum) + '.txt', 'a')

#https://stackoverflow.com/questions/22036975/storing-dictionary-as-value-on-another-dictionary-in-python
def multi_level_dict():
    return defaultdict(multi_level_dict)

words = {}

#comment
def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True


# source: https://stackoverflow.com/questions/1936466/beautifulsoup-grab-visible-webpage-text
def text_from_html(soup1):
    texts = soup1.findAll(text=True)
    visible_texts = filter(tag_visible, texts)
    return u" ".join(t.strip() for t in visible_texts)


# if this line is causing errors but you have nltk installed
# open idle and do 'import nltk' then 'nltk.download('punkt')
def extractHtmlFromJson(filePath):
    global currentDocId
    global currentIndexFile
    global currentFileNum
    

    if currentDocId % 500 == 0:
        #Close the current file
        currentIndexFile.close()
        #Open a new file
        currentFileNum += 1
        currentIndexFile = open('./DocIdMap/' + str(currentFileNum) + '.txt', 'a')
        print('Opened a new file: ' + str(currentFileNum) + '.txt')

    json_data = open(filePath)
    # print('Loading data from: ' + filePath)
    # { url, content, encoding }
    print(filePath)
    data = json.load(json_data)
    currentIndexFile.write(str(currentDocId) + ',' + str(data['url']) + '\n')
    # load the html into BeautifulSoup
    soup = BeautifulSoup(data['content'], features='lxml')

    # strip out the javscript and some style tags from the html file
    for garbage in soup(['script', 'style']):
        garbage.decompose()

    tokenizer = RegexpTokenizer(r'\w+')
    tokens = tokenizer.tokenize(text_from_html(soup))
    for word in tokens:
        if word.lower() in words:
            words[word.lower()]['postings'][currentDocId]['count'] += 1
            words[word.lower()]['count'] += 1
        else:
            newPosting = posting.Posting(currentDocId, 0, 1)
            words[word.lower()] = {}
            words[word.lower()]['postings'] = {}
            words[word.lower()]['postings'][currentDocId] = newPosting.__dict__
            words[word.lower()]['count'] = 1

    #print(words)


# runs through all directories and prints out a list of files within them.
def traverseDirectories():
    global currentDocId
    for (root, dirs, files) in os.walk('./DEV', topdown=True):
        for file in files:
            if dirs == 'DocIdMap':
                continue
            extractHtmlFromJson(root + '/' + file)
            currentDocId += 1

def run():
    #traverseDirectories()
    extractHtmlFromJson('DEV/aiclub_ics_uci_edu/8ef6d99d9f9264fc84514cdd2e680d35843785310331e1db4bbd06dd2b8eda9b.json')


if __name__ == "__main__":
    run()
