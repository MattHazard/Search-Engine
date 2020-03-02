from nltk.stem import PorterStemmer
from nltk.tokenize import TweetTokenizer
######################################
# Gets input and runs through stemmer.
# Returns a list of stemmed tokens.
######################################
def makequery():
    query = input("Search: ")
    stemmer = PorterStemmer()
    tokenizer = TweetTokenizer()

    tokens = tokenizer.tokenize(query)
    stemmedTokens = []

    for token in tokens:
        stemmedTokens.append(stemmer.stem(token))
    
    return stemmedTokens

def search(query):
    for token in query:
        # Load the in the appropriate indices, read the postings for the words
        # do and operation on all the postings by doc id to find docs with all the tokens
        # Those urls are contenders
        # Don't need tf-idf working just yet.
        
if __name__ == "__main__":
    query = makequery()
    search(query)
