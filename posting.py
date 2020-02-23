#Class to hold the information for every document read.
class Posting:
    def __init__(self, docid, tfidf):
        self.docid = docid
        self.tfidf = tfidf