# IF YOU HAVE ANY QUESTIONS ABOUT THE IMPLEMENTATION, we can clear things up in the interview
# I have provided basic explanations of functions in the comments throughout the files
# -Matthew Mueller

import gc
import posting as posting
from bs4 import BeautifulSoup
import os  # allows us to get the directories and file names
import json
import pickle
from bs4.element import Comment
import nltk

nltk.download('punkt')
from nltk.stem import PorterStemmer
from nltk.tokenize import TweetTokenizer
from math import log10
import sys
import string

currPickleFile = 0
currentDocId = 1
currentFileNum = 0
words = {}
stemmer = PorterStemmer()
count_in_doc = {}

# Here we create all the folders needed for the indexing
if os.path.isdir('./DocIdMap'):
    currentIndexFile = open('./DocIdMap/' + str(currentFileNum), 'a')
else:
    os.mkdir(os.getcwd() + '/' + 'DocIdMap')
    currentIndexFile = open('./DocIdMap/' + str(currentFileNum) + '.txt', 'a')

if os.path.isdir('./indexes'):
    pass
else:
    os.mkdir(os.getcwd() + '/' + 'indexes')

if os.path.isdir('./finalIndexes'):
    pass
else:
    os.mkdir(os.getcwd() + '/' + 'finalIndexes')
    i = 0
    empty = {}
    while i < 27:
        if i != 26:
            with open('./finalIndexes/' + string.ascii_lowercase[i] + '.pickle', 'wb') as handle:
                pickle.dump(empty, handle, protocol=pickle.HIGHEST_PROTOCOL)
        i += 1
    j = 0
    while j < 11:
        if j != 10:
            with open('./finalIndexes/' + str(j) + '.pickle', 'wb') as handle:
                pickle.dump(empty, handle, protocol=pickle.HIGHEST_PROTOCOL)
        else:
            with open('./finalIndexes/sym.pickle', 'wb') as handle:
                pickle.dump(empty, handle, protocol=pickle.HIGHEST_PROTOCOL)
        j += 1


def createEntry(dict, word):
    global currentDocId
    newPosting = posting.Posting(currentDocId, 0, 1)
    dict[word.lower()] = {}
    dict[word.lower()]['postings'] = {}
    dict[word.lower()]['postings'][currentDocId] = newPosting.__dict__
    dict[word.lower()]['count'] = 1


###################################################
# loads all pickle dicts in a file to be loaded to
# a single dictionary.
# Ex: dict = loadall(a.txt)
###################################################
def loadall(filename):
    global words
    tempDict = {}
    with open(filename, 'rb') as fr:
        try:
            while True:
                tempDict = pickle.load(fr)
        except EOFError:
            pass
    return tempDict


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
    idf = log10(N / df)
    return (1 + log10(tf)) * idf


###################################################
# Takes a list of tokens and updates the posting
# dictionary.
###################################################
def processTokens(tokens):
    global currentDocId
    global words
    global currPickleFile

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

        if len(words.keys()) > 500000 or sys.getsizeof(words) > 8000000:
            with open('./indexes/' + str(currPickleFile) + '.pickle', 'wb') as handle:
                pickle.dump(words, handle, protocol=pickle.HIGHEST_PROTOCOL)
            words = {}
            currPickleFile += 1

        if word.lower() in words:
            if currentDocId in words[word.lower()]['postings']:
                words[word.lower()]['postings'][currentDocId]['count'] += 1
                #############################
                ## I think tf needs to be calculated while postings are being created
                ## but we can calculate the full tf-idf when we get a query?
                ## Once we have everything indexed we will have the df (words[word.lower()]['count']) and the N (size of corpus)
                ## When we get a query we can just get the tf-idf while we are searching for the words?
                #############################
                # update tf
                words[word.lower()]['postings'][currentDocId]['tf'] = words[word.lower()]['postings'][currentDocId][
                    'count']
            else:
                newPosting = posting.Posting(currentDocId, 0, 1)
                words[word.lower()]['postings'][currentDocId] = newPosting.__dict__
                # set up the tf
                words[word.lower()]['postings'][currentDocId]['tf'] = 1
            words[word.lower()]['count'] += 1
        else:
            newPosting = posting.Posting(currentDocId, 0, 1)
            words[word.lower()] = {}
            words[word.lower()]['postings'] = {}
            words[word.lower()]['postings'][currentDocId] = newPosting.__dict__
            words[word.lower()]['count'] = 1
            # set up the tf
            words[word.lower()]['postings'][currentDocId]['tf'] = 1


###################################################
# Extracts all the words from an html file and
# sends passes them to the token processor.
###################################################
def extractTokensFromJson(filePath):
    global currentDocId

    json_data = open(filePath)
    data = json.load(json_data)
    updateDocIdMap(str(data['url']))
    soup = BeautifulSoup(data['content'], features='lxml')
    text = soup.get_text(" ", strip=True)

    tokenizer = TweetTokenizer()
    tokens = tokenizer.tokenize(text)

    processTokens(tokens)

    currentDocId += 1


###################################################
# Need to get this part finished ASAP so we can
# start using our index. Having trouble using
# this dict of dicts.
###################################################
# def writeIndex():
#     #We want to split up the files a,b,..z, numeric
#     for word in words:
#         if word[0].isalpha() == True:
#             #print("Posting for word: " + word + " is " + str(words[word.lower()]['postings']))
#             print(word + " df = " + str(words[word.lower()]['count']))
#         else:
#             print("Not alpha? : " + word[0])


###################################################
# runs through all directories and prints out a
# list of files within them.
###################################################
def traverseDirectories():
    global currentDocId
    for (root, dirs, files) in os.walk('./DEV', topdown=True):
        for file in files:
            extractTokensFromJson(root + '/' + file)


###################################################
# Runs the indexer.
###################################################

# Here we run through and rearrange the index files into more useful files that we will use for our query
# Sounds a bit inefficient but it is actually very fast
def finalIndex():
    files = next(os.walk(os.getcwd() + '/indexes'))[2]
    numF = len(files)
    i = 0
    # sum = 0
    # n = 0
    # while n < 27:
    #     if n != 26:
    #         currChar = string.ascii_lowercase[n]
    #         test = loadall('./finalIndexes/' + str(currChar) + '.pickle')
    #         sum += len(test)
    #     else:
    #         test = loadall('./finalIndexes/numsyms.pickle')
    #         sum += len(test)
    #     n += 1
    # print(sum)
    # exit()
    # print(test)
    # exit()
    # print(numF)
    while i < numF:
        currIndexDict = loadall('./indexes/' + str(i) + '.pickle')
        # print(list(currIndexDict.keys())[0])
        j = 0
        while j < 27:
            # print(currChar)
            if j != 26:
                currChar = string.ascii_lowercase[j]
                currCharDict = loadall('./finalIndexes/' + currChar + '.pickle')
                for k, val in enumerate((list(currIndexDict.keys()))):
                    if str(val[0]) != str(currChar):
                        continue
                    if val in currCharDict:
                        for m, value in enumerate(currIndexDict[val]['postings']):
                            newPosting = posting.Posting(value, 0, currIndexDict[val]['postings'][value]['count'])
                            currCharDict[val]['postings'][value] = newPosting.__dict__
                            currCharDict[val]['count'] += 1
                            currCharDict[val]['postings'][value]['tf'] = currIndexDict[val]['postings'][value]['tf']
                    else:
                        # this line
                        currCharDict[val] = {}
                        currCharDict[val]['postings'] = {}
                        currCharDict[val]['count'] = 0
                        for m, value in enumerate(currIndexDict[val]['postings']):
                            newPosting = posting.Posting(value, 0, currIndexDict[val]['postings'][value]['count'])
                            currCharDict[val]['postings'][value] = newPosting.__dict__
                            currCharDict[val]['count'] += 1
                            currCharDict[val]['postings'][value]['tf'] = currIndexDict[val]['postings'][value]['tf']
                with open('./finalIndexes/' + currChar + '.pickle', 'wb') as hand:
                    pickle.dump(currCharDict, hand, protocol=pickle.HIGHEST_PROTOCOL)
            j += 1

        a = 0
        while a < 11:
            if a != 10:
                currCharDict = loadall('./finalIndexes/' + str(a) + '.pickle')
                for k, val in enumerate((list(currIndexDict.keys()))):
                    if str(val[0]) != str(a):
                        continue
                    if val in currCharDict:
                        for m, value in enumerate(currIndexDict[val]['postings']):
                            newPosting = posting.Posting(value, 0, currIndexDict[val]['postings'][value]['count'])
                            currCharDict[val]['postings'][value] = newPosting.__dict__
                            currCharDict[val]['count'] += 1
                            currCharDict[val]['postings'][value]['tf'] = currIndexDict[val]['postings'][value]['tf']
                    else:
                        # this line
                        currCharDict[val] = {}
                        currCharDict[val]['postings'] = {}
                        currCharDict[val]['count'] = 0
                        for m, value in enumerate(currIndexDict[val]['postings']):
                            newPosting = posting.Posting(value, 0, currIndexDict[val]['postings'][value]['count'])
                            currCharDict[val]['postings'][value] = newPosting.__dict__
                            currCharDict[val]['count'] += 1
                            currCharDict[val]['postings'][value]['tf'] = currIndexDict[val]['postings'][value]['tf']
                with open('./finalIndexes/' + str(a) + '.pickle', 'wb') as hand:
                    pickle.dump(currCharDict, hand, protocol=pickle.HIGHEST_PROTOCOL)
            else:
                currCharDict = loadall('./finalIndexes/sym.pickle')
                for k, val in enumerate((list(currIndexDict.keys()))):
                    if str(val[0]).isalnum():
                        continue
                    if val in currCharDict:
                        for m, value in enumerate(currIndexDict[val]['postings']):
                            newPosting = posting.Posting(value, 0, currIndexDict[val]['postings'][value]['count'])
                            currCharDict[val]['postings'][value] = newPosting.__dict__
                            currCharDict[val]['count'] += 1
                            currCharDict[val]['postings'][value]['tf'] = currIndexDict[val]['postings'][value]['tf']
                    else:
                        # this line
                        currCharDict[val] = {}
                        currCharDict[val]['postings'] = {}
                        currCharDict[val]['count'] = 0
                        for m, value in enumerate(currIndexDict[val]['postings']):
                            newPosting = posting.Posting(value, 0, currIndexDict[val]['postings'][value]['count'])
                            currCharDict[val]['postings'][value] = newPosting.__dict__
                            currCharDict[val]['count'] += 1
                            currCharDict[val]['postings'][value]['tf'] = currIndexDict[val]['postings'][value]['tf']
                with open('./finalIndexes/sym.pickle', 'wb') as hand:
                    pickle.dump(currCharDict, hand, protocol=pickle.HIGHEST_PROTOCOL)
            a += 1
        i += 1


# Calculating all the TFIDF values at the end
# Very fast
def calcTFIDF():
    sum = 0
    n = 0
    while n < 36:
        if n < 26:
            currChar = string.ascii_lowercase[n]
            test = loadall('./finalIndexes/' + str(currChar) + '.pickle')
            sum += len(test)
        else:
            test = loadall('./finalIndexes/' + str(n - 26) + '.pickle')
            sum += len(test)
        n += 1
    n = 0
    while n < 36:
        if n < 26:
            currChar = string.ascii_lowercase[n]
            test = loadall('./finalIndexes/' + str(currChar) + '.pickle')
            for k, val in enumerate((list(test.keys()))):
                test[val]['df'] = len(test[val]['postings'])
                for m, ins in enumerate((list(test[val]['postings'].keys()))):
                    test[val]['postings'][ins]['tfidf'] = getTfIdf(test[val]['postings'][ins]['tf'], sum,
                                                                   test[val]['df'])
            with open('./finalIndexes/' + currChar + '.pickle', 'wb') as hand:
                pickle.dump(test, hand, protocol=pickle.HIGHEST_PROTOCOL)
        else:
            test = loadall('./finalIndexes/' + str(n - 26) + '.pickle')
            for k, val in enumerate((list(test.keys()))):
                test[val]['df'] = len(test[val]['postings'])
                for m, ins in enumerate((list(test[val]['postings'].keys()))):
                    test[val]['postings'][ins]['tfidf'] = getTfIdf(test[val]['postings'][ins]['tf'], sum,
                                                                   test[val]['df'])
            with open('./finalIndexes/' + str(n - 26) + '.pickle', 'wb') as hand:
                pickle.dump(test, hand, protocol=pickle.HIGHEST_PROTOCOL)
        n += 1


def run():
    traverseDirectories()
    with open('./indexes/' + str(currPickleFile) + '.pickle', 'wb') as handle:
        pickle.dump(words, handle, protocol=pickle.HIGHEST_PROTOCOL)
    finalIndex()
    calcTFIDF()


if __name__ == "__main__":
    run()
