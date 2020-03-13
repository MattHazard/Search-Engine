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
    idf = log10(N / (df + 1))
    return tf * idf


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

        if len(words.keys()) > 400000 or sys.getsizeof(words) > 8000000:
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
                                                                          'count'] / len(stemmedTokens)
            else:
                newPosting = posting.Posting(currentDocId, 0, 1)
                words[word.lower()]['postings'][currentDocId] = newPosting.__dict__
                # set up the tf
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
                    else:
                        # this line
                        currCharDict[val] = {}
                        currCharDict[val]['postings'] = {}
                        currCharDict[val]['count'] = 0
                        for m, value in enumerate(currIndexDict[val]['postings']):
                            newPosting = posting.Posting(value, 0, currIndexDict[val]['postings'][value]['count'])
                            currCharDict[val]['postings'][value] = newPosting.__dict__
                            currCharDict[val]['count'] += 1
                with open('./finalIndexes/' + currChar + '.pickle', 'wb') as hand:
                    pickle.dump(currCharDict, hand, protocol=pickle.HIGHEST_PROTOCOL)
            j += 1

        k = 0
        while k < 11:
            if k != 10:
                currCharDict = loadall('./finalIndexes/' + str(k) + '.pickle', 'wb')
                for k, val in enumerate((list(currIndexDict.keys()))):
                    if str(val[0]).isalpha():
                        continue
                    if val in currCharDict:
                        for m, value in enumerate(currIndexDict[val]['postings']):
                            newPosting = posting.Posting(value, 0, currIndexDict[val]['postings'][value]['count'])
                            currCharDict[val]['postings'][value] = newPosting.__dict__
                            currCharDict[val]['count'] += 1
                    else:
                        # this line
                        currCharDict[val] = {}
                        currCharDict[val]['postings'] = {}
                        currCharDict[val]['count'] = 0
                        for m, value in enumerate(currIndexDict[val]['postings']):
                            newPosting = posting.Posting(value, 0, currIndexDict[val]['postings'][value]['count'])
                            currCharDict[val]['postings'][value] = newPosting.__dict__
                            currCharDict[val]['count'] += 1
                with open('./finalIndexes/' + str(k) + '.pickle', 'wb') as hand:
                    pickle.dump(currCharDict, hand, protocol=pickle.HIGHEST_PROTOCOL)
            else:
                currCharDict = loadall('./finalIndexes/sym.pickle', 'wb')
                for k, val in enumerate((list(currIndexDict.keys()))):
                    if str(val[0]).isalnum():
                        continue
                    if val in currCharDict:
                        for m, value in enumerate(currIndexDict[val]['postings']):
                            newPosting = posting.Posting(value, 0, currIndexDict[val]['postings'][value]['count'])
                            currCharDict[val]['postings'][value] = newPosting.__dict__
                            currCharDict[val]['count'] += 1
                    else:
                        # this line
                        currCharDict[val] = {}
                        currCharDict[val]['postings'] = {}
                        currCharDict[val]['count'] = 0
                        for m, value in enumerate(currIndexDict[val]['postings']):
                            newPosting = posting.Posting(value, 0, currIndexDict[val]['postings'][value]['count'])
                            currCharDict[val]['postings'][value] = newPosting.__dict__
                            currCharDict[val]['count'] += 1
                with open('./finalIndexes/sym.pickle', 'wb') as hand:
                    pickle.dump(currCharDict, hand, protocol=pickle.HIGHEST_PROTOCOL)
            k += 1
        i += 1

def run():
    # print("Testing Tf-Idf for doc that has tf of 0.03 (3/100) and appears 1000 times out of 10,000,000 size corpus" + str(getTfIdf(.03, 10000000, 1000)))
    traverseDirectories()
    with open('./indexes/' + str(currPickleFile) + '.pickle', 'wb') as handle:
        pickle.dump(words, handle, protocol=pickle.HIGHEST_PROTOCOL)
    d1 = {}
    d2 = {}
    #finalIndex()
    # print("Please enter your search query:")
    # que = input()
    # query = que.split(' ')
    # li = []
    # for i in query:
    #     d = {}
    #     if str(i[0]).isalpha():
    #         words = loadall('finalIndexes/' + str(i[0]).lower() + '.pickle')
    #     else:
    #         words = loadall('finalIndexes/numsyms.pickle')
    #     #print(words[stemmer.stem(i.lower())]['postings'])
    #     for j in words[stemmer.stem(i.lower())]['postings']:
    #         d[j] = 1
    #     li.append(d)
    # new = {}
    # for i in li:
    #     for j in i:
    #         if j in new.keys():
    #             new[j] += 1
    #         else:
    #             new[j] = 1
    # urlL = []
    # for i in new:
    #     if new[i] is len(li):
    #         urlL.append(getUrlFromDocId(int(i)))
    # print(urlL)
    # exit()

    # words = loadall('pickle.pickle')
    # print("Please enter your search query:")
    # que = input()
    # query = que.split(' ')
    # li = []
    # for i in query:
    #     d = {}
    #     for j in words[stemmer.stem(i.lower())]['postings']:
    #         d[j] = 1
    #     li.append(d)
    # new = {}
    # for i in li:
    #     for j in i:
    #         if j in new.keys():
    #             new[j] += 1
    #         else:
    #             new[j] = 1
    # urlL = []
    # for i in new:
    #     if new[i] is len(li):
    #         urlL.append(getUrlFromDocId(int(i)))
    # print(urlL)
    # extractTokensFromJson('DEV/scale_ics_uci_edu/d93a8cb31884b6fcb38d121d07176dc6752e5bf1889b3b8fa313672028a65824.json')
    # extractTokensFromJson('DEV/dynamo_ics_uci_edu/0c961803ef7f746bd7a4f5faf3e134546dec9a75719c214bfea2ee2652e5f241.json')
    # extractTokensFromJson('DEV/cml_ics_uci_edu/0f32f6f497d71106ff8e3a26fdf59a538771b01bed110afc8cbdc23ba804818a.json')
    ###Loads file after it has been generated.
    # d1 = loadall('./indexes/0.pickle')
    # d2 = loadall('./indexes/2.pickle')
    # print(len(d1.keys()))
    # print(len(d2.keys()))
    # d1.update(d2)
    # print(len(d1.keys()))

    # print(len(words.keys()))


if __name__ == "__main__":
    run()
