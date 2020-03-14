from nltk.stem import PorterStemmer
from nltk.tokenize import TweetTokenizer


######################################
# Gets input and runs through stemmer.
# Returns a list of stemmed tokens.
######################################
from indexer import loadall, stemmer, getUrlFromDocId
import time
words = {}
#stemmer = PorterStemmer()

# def makequery():
#     query = input("Search: ")
#     stemmer = PorterStemmer()
#     tokenizer = TweetTokenizer()
#
#     tokens = tokenizer.tokenize(query)
#     stemmedTokens = []
#
#     for token in tokens:
#         stemmedTokens.append(stemmer.stem(token))
#
#     return stemmedTokens


def search(query):
    # for token in query:
    # Load the in the appropriate indices, read the postings for the words
    # do and operation on all the postings by doc id to find docs with all the tokens
    # Those urls are contenders
    # Don't need tf-idf working just yet.
    tic = time.perf_counter()
    query = que.split(' ')
    d = {}
    for i in query:
        temp = loadall('finalIndexes/' + str(i[0]).lower() + '.pickle')
        for val in temp[stemmer.stem(i.lower())]['postings']:
            if val in d:
                d[val] += temp[stemmer.stem(i.lower())]['postings'][val]['tfidf']
            else:
                d[val] = temp[stemmer.stem(i.lower())]['postings'][val]['tfidf']
        sort = sorted(d.items(), key=lambda x: x[1], reverse=True)
        for i, val in enumerate(sort):
            if i == 10:
                return
            else:
                print(getUrlFromDocId(val[0]))



    # li = []
    # for i in query:
    #     d = {}
    #     if str(i[0]).isalpha():
    #         words = loadall('finalIndexes/' + str(i[0]).lower() + '.pickle')
    #     else:
    #         words = loadall('finalIndexes/numsyms.pickle')
    #     # print(words[stemmer.stem(i.lower())]['postings'])
    #     for j in words[stemmer.stem(i.lower())]['postings']:
    #         d[j] = 1
    #     li.append(d)
    # new = {}
    # for i in li:
    #     print(i)
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
    toc = time.perf_counter()
    print('Query performed in ' + str(toc - tic) + 'seconds')


if __name__ == "__main__":
    print("Please enter your search query:")
    que = input()
    search(que)
