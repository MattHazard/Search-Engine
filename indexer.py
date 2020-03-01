import posting as posting
from bs4 import BeautifulSoup
import re
import os  # allows us to get the directories and file names
import json
import pickle
from bs4.element import Comment
import nltk
nltk.download('punkt')
from nltk.stem import PorterStemmer
from nltk.tokenize import RegexpTokenizer
from nltk.tokenize import TweetTokenizer
from math import log10

currentDocId = 1
currentFileNum = 0
words = {}
stemmer = PorterStemmer()
count_in_doc = {}

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


###################################################
# Returns the url associated with a document id
###################################################
def getUrlFromDocId(docId):
    try:
        fileNumber = docId // 500
        startId = fileNumber * 500
        urlLine = docId - startId
        if fileNumber == 0:
            urlLine -= 1
        file = open('./DocIdMap/' + str(fileNumber), 'r')
        for x in range(urlLine):
            file.readline()
        return file.readline()
    except:
        print("Error occured while trying to get URL from DocId!")

###################################################
# Adds a url to the doc id index. 
# Creates a new file if the doc id goes above
# specified threshold. 
###################################################
def updateDocIdMap(url):
    global currentDocId
    global currentIndexFile
    global currentFileNum
    if currentDocId % 500 == 0:
        # Close the current file
        currentIndexFile.close()
        # Open a new file
        currentFileNum += 1
        currentIndexFile = open('./DocIdMap/' + str(currentFileNum), 'a')
    currentIndexFile.write(url + '\n')

###################################################
# Calculates the tf-idf score.
###################################################
def getTfIdf(tf, N, df):
    idf = log10(N/(df+1))
    return tf * idf

###################################################
# Takes a list of tokens and updates the posting
# dictionary.
###################################################
def processTokens(tokens):
    global currentDocId

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
                #############################
                # I think tf needs to be calculated while postings are being created
                # but we can calculate the full tf-idf when we get a query?
                # Once we have everything indexed we will have the df (words[word.lower()]['count']) and the N (size of corpus)
                # When we get a query we can just get the tf-idf while we are searching for the words?
                ############################
                #update tf
                words[word.lower()]['postings'][currentDocId]['tf'] = words[word.lower()]['postings'][currentDocId]['count'] / len(stemmedTokens)
            else:
                newPosting = posting.Posting(currentDocId, 0, 1)
                words[word.lower()]['postings'][currentDocId] = newPosting.__dict__
                #set up the tf
                words[word.lower()]['postings'][currentDocId]['tf'] = 1 / len(stemmedTokens)
            words[word.lower()]['count'] += 1
        else:
            newPosting = posting.Posting(currentDocId, 0, 1)
            words[word.lower()] = {}
            words[word.lower()]['postings'] = {}
            words[word.lower()]['postings'][currentDocId] = newPosting.__dict__
            words[word.lower()]['count'] = 1

            # set up the tf
            words[word.lower()]['postings'][currentDocId]['tf'] = 1 / len(stemmedTokens)

###################################################
# Extracts all the words from an html file and
# sends passes them to the token processor.
###################################################
def extractTokensFromJson(filePath):
    global currentDocId

    json_data = open(filePath)
    data = json.load(json_data)
    updateDocIdMap(str(data['url'])) 
    soup = BeautifulSoup(data['content'], 'html5lib')#features='lxml')
    text = soup.get_text(" ", strip=True)
    
    tokenizer = TweetTokenizer()
    tokens = tokenizer.tokenize(text)
    
    processTokens(tokens)

###################################################
# runs through all directories and prints out a 
# list of files within them.
###################################################
def traverseDirectories():
    global currentDocId
    for (root, dirs, files) in os.walk('./DEV', topdown=True):
        for file in files:
            extractTokensFromJson(root + '/' + file)
            currentDocId += 1

###################################################
# Runs the indexer.
###################################################
def run():
    traverseDirectories()

    ###Generates file that is easily readable with pickle
    with open('index.pickle', 'wb') as handle:
      pickle.dump(words, handle, protocol=pickle.HIGHEST_PROTOCOL)

    ###Loads file after it has been generated.
    #with open('index.pickle', 'rb') as handle:
        #loadedwords = pickle.load(handle)
    #print(loadedwords)


if __name__ == "__main__":
    run()
