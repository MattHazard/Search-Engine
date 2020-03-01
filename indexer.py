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

# returns the url associated with the document id given
def getUrlFromDocId(docId):
    try:
        fileNumber = docId // 500
        startId = fileNumber * 500
        urlLine = docId - startId
        if fileNumber == 0:
            urlLine -= 1
        file = open('./DocIdMap/' + str(fileNumber) + '.txt', 'r')
        for x in range(urlLine):
            file.readline()
        return file.readline()
    except:
        print("Error occured while trying to get URL from DocId!")

def updateDocIdMap(url):
    global currentDocId
    global currentIndexFile
    global currentFileNum
    if currentDocId % 500 == 0:
        # Close the current file
        currentIndexFile.close()
        # Open a new file
        currentFileNum += 1
        currentIndexFile = open('./DocIdMap/' + str(currentFileNum) + '.txt', 'a')
    currentIndexFile.write(url + '\n')

# if this line is causing errors but you have nltk installed
# open idle and do 'import nltk' then 'nltk.download('punkt')
def extractHtmlFromJson(filePath):
    global currentDocId

    json_data = open(filePath)
    data = json.load(json_data)
    updateDocIdMap(str(data['url'])) 
    soup = BeautifulSoup(data['content'], features='lxml')
    text = soup.get_text()
    
    for garbage in soup(['script', 'style']):
        garbage.decompose()

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
                print("New posting inserted: " + word.lower() + " - " + str(newPosting))
            words[word.lower()]['count'] += 1
        else:
            newPosting = posting.Posting(currentDocId, 0, 1)
            print("New posting inserted: " + word.lower() + " - " + str(newPosting))
            words[word.lower()] = {}
            words[word.lower()]['postings'] = {}
            words[word.lower()]['postings'][currentDocId] = newPosting.__dict__
            words[word.lower()]['count'] = 1


# runs through all directories and prints out a list of files within them.
def traverseDirectories():
    global currentDocId
    for (root, dirs, files) in os.walk('./DEV', topdown=True):
        for file in files:
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
    #print(currentDocId)
    #print(len(words.keys()))

    ###Loads file after it has been generated.
    #with open('index.pickle', 'rb') as handle:
        #loadedwords = pickle.load(handle)
    #print(loadedwords)


if __name__ == "__main__":
    run()
