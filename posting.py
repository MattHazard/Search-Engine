# Class to hold the information for every document read.
class Posting:
    def __init__(self, docid, tfidf, count):
        self.docid = docid
        self.tfidf = tfidf
        self.count = count
    def __str__(self):
        return f'{self.docid},{self.tfidf},{self.count}'
