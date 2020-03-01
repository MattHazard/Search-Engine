# Class to hold the information for every document read.
class Posting:
    def __init__(self, docid, tfidf, count):
        self.docid = docid
        self.tfidf = tfidf
        self.count = count
        self.tf = 0

    def updateTf(self, wordsInD):
        tf = count / wordsInD

    def __str__(self):
        return f'{self.docid},{self.tfidf},{self.count}'
