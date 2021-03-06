from nltk.stem import PorterStemmer
from nltk.tokenize import TweetTokenizer

######################################
# Gets input and runs through stemmer.
# Returns a list of stemmed tokens.
######################################
from indexer import loadall, stemmer, getUrlFromDocId
import time

words = {}


# Search takes the raw query and returns the most relevant urls according to the heuristic
# Currently it returns the top 10 results but that can be changed by changing the I value
def search(query):
    if query == '':
        print('Query was empty')
        return
    tic = time.perf_counter()
    query = que.split(' ')
    d = {}
    currChar = ''
    for i in query:
        if currChar != str(i[0]).lower():
            temp = loadall('finalIndexes/' + str(i[0]).lower() + '.pickle')
        currChar = str(i[0]).lower()
        if stemmer.stem(i.lower()) not in temp.keys():
            continue
        for val in temp[stemmer.stem(i.lower())]['postings']:
            if val in d:
                d[val] += temp[stemmer.stem(i.lower())]['postings'][val]['tfidf']
            else:
                d[val] = temp[stemmer.stem(i.lower())]['postings'][val]['tfidf']
        sort = sorted(d.items(), key=lambda x: x[1], reverse=True)
        for i, val in enumerate(sort):
            if i == 10:
                toc = time.perf_counter()
                print('Query performed in ' + str(toc - tic) + 'seconds')
                return
            else:
                print(getUrlFromDocId(val[0]))
    toc = time.perf_counter()
    print('No results found')
    print('Query performed in ' + str(toc - tic) + 'seconds')


if __name__ == "__main__":
    print("Please enter your search query:")
    que = input()
    search(que)
