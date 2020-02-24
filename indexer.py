import posting as posting
from bs4 import BeautifulSoup
import os  # allows us to get the directories and file names
import json
import pickle
from bs4.element import Comment
import nltk
nltk.download('punkt')
from nltk.stem import PorterStemmer
from nltk.tokenize import RegexpTokenizer
from nltk.tokenize import TweetTokenizer

currentDocId = 1
currentFileNum = 0
words = {}
stemmer = PorterStemmer()

if os.path.isdir('./DocIdMap'):
    currentIndexFile = open('./DocIdMap/' + str(currentFileNum) + '.txt', 'a')
else:
    os.mkdir(os.getcwd() + '/' + 'DocIdMap')
    currentIndexFile = open('./DocIdMap/' + str(currentFileNum) + '.txt', 'a')

# comment
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
        # Close the current file
        currentIndexFile.close()
        # Open a new file
        currentFileNum += 1
        currentIndexFile = open('./DocIdMap/' + str(currentFileNum) + '.txt', 'a')

    json_data = open(filePath)
    # print('Loading data from: ' + filePath)
    # { url, content, encoding }
    # print(filePath)
    data = json.load(json_data)
    currentIndexFile.write(str(currentDocId) + ',' + str(data['url']) + '\n')
    # load the html into BeautifulSoup
    soup = BeautifulSoup(data['content'], features='lxml')
    text = soup.get_text()

    # strip out the javscript and some style tags from the html file
    #for garbage in soup(['script', 'style']):
        #garbage.decompose()

    #tokenizer = RegexpTokenizer(r'\w+')
    tokenizer = TweetTokenizer()
    tokens = tokenizer.tokenize(text)

    stemmedTokens = []
    for word in tokens:
        stemmedTokens.append(stemmer.stem(word))

    for word in stemmedTokens:
        badchar = 0
        for c in word.lower():
            if not c.isalnum() or not c.isascii():
                badchar = 1
                break
        if badchar == 1:
            continue
        if word.lower() in words:
            if currentDocId in words[word.lower()]['postings']:
                words[word.lower()]['postings'][currentDocId]['count'] += 1
            else:
                newPosting = posting.Posting(currentDocId, 0, 1)
                words[word.lower()]['postings'][currentDocId] = newPosting.__dict__
            words[word.lower()]['count'] += 1
        else:
            newPosting = posting.Posting(currentDocId, 0, 1)
            words[word.lower()] = {}
            words[word.lower()]['postings'] = {}
            words[word.lower()]['postings'][currentDocId] = newPosting.__dict__
            words[word.lower()]['count'] = 1

    # print(words)


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
    #extractHtmlFromJson('DEV/aiclub_ics_uci_edu/8ef6d99d9f9264fc84514cdd2e680d35843785310331e1db4bbd06dd2b8eda9b.json')
    #extractHtmlFromJson('DEV/chenli_ics_uci_edu/7ed296f06e2b7cfe46dcbbf81e75aacc93144bcd79e7d8201be8fe8bd376fdb6.json')
    #extractHtmlFromJson('DEV/chenli_ics_uci_edu/b800d3dc96be1cd9836ce799dc4e86db7ea1dfa27597ce9fd8ca186af928d583.json')

    traverseDirectories()

    ###Generates file that is easily readable with pickle
    with open('index.pickle', 'wb') as handle:
      pickle.dump(words, handle, protocol=pickle.HIGHEST_PROTOCOL)

    #print(words)
    print(currentDocId)
    print(len(words.keys()))

    ###Loads file after it has been generated.
    #with open('index.pickle', 'rb') as handle:
        #loadedwords = pickle.load(handle)
    #print(loadedwords)


if __name__ == "__main__":
    run()
