import posting as posting
import bs4 as bs
import os  # allows us to get the directories and file names


# returns all of the sites in a directory
def getSites(directory):
    print(directory)
    return list()


# returns all of the directories in a directory
def getDirectories(directory):
    return os.listdir(directory)


# returns the HTML content of a page (JSON parse completed)
def getPageContent(site):
    print(site)
    return ''


# returns the DEV folder, used a function so that it works on windows, mac, linux..
def startingDirectory():
    # Formats the path correctly for Windows or some unix-like system
    if os.name == 'nt':
        return os.getcwd() + '\\DEV\\'
    else:
        return os.getcwd() + '/DEV/'


def run():
    directories = getDirectories(startingDirectory())
    for dir in directories:
        print(dir)


run()
