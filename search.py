from nltk.stem import PorterStemmer
from nltk.tokenize import TweetTokenizer


######################################
# Gets input and runs through stemmer.
# Returns a list of stemmed tokens.
######################################
from indexer import loadall, stemmer, getUrlFromDocId

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
    query = que.split(' ')
    li = []
    for i in query:
        d = {}
        if str(i[0]).isalpha():
            words = loadall('finalIndexes/' + str(i[0]).lower() + '.pickle')
        else:
            words = loadall('finalIndexes/numsyms.pickle')
        # print(words[stemmer.stem(i.lower())]['postings'])
        for j in words[stemmer.stem(i.lower())]['postings']:
            d[j] = 1
        li.append(d)
    new = {}
    for i in li:
        for j in i:
            if j in new.keys():
                new[j] += 1
            else:
                new[j] = 1
    urlL = []
    for i in new:
        if new[i] is len(li):
            urlL.append(getUrlFromDocId(int(i)))
    print(urlL)


if __name__ == "__main__":
    print("Please enter your search query:")
    que = input()
    search(que)
