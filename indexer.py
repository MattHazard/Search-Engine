import posting as posting
import bs4 as bs
from bs4 import BeautifulSoup
import os  # allows us to get the directories and file names
import json
import nltk
from bs4.element import Comment

nltk.download('stopwords')
nltk.download('punkt')
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer


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


# if this line is causing errors but you have nltk installed
# open idle and do 'import nltk' then 'nltk.download('punkt')
def extractHtmlFromJson(filePath):
    json_data = open(filePath)
    print('Loading data from: ' + filePath)
    # { url, content, encoding }
    data = json.load(json_data)
    # load the html into BeautifulSoup
    soup = BeautifulSoup(data['content'])

    # strip out the javscript and some style tags from the html file
    for garbage in soup(['script', 'style']):
        garbage.decompose()

    tokenizer = RegexpTokenizer(r'\w+')
    tokens = tokenizer.tokenize(text_from_html(soup))

    print(tokens)


# runs through all directories and prints out a list of files within them.
def traverseDirectories():
    for (root, dirs, files) in os.walk('./DEV', topdown=True):
        for file in files:
            extractHtmlFromJson(root + '/' + file)


def run():
    traverseDirectories()


if __name__ == "__main__":
    run()
