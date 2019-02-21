from __future__ import print_function
import nltk
import math
import lxml
import re, os, sys
import pickle
import string
import json
from pprint import pprint
from bs4 import BeautifulSoup
from bs4.element import Comment
from collections import defaultdict

DEBUG = False;
#nltk.download('punkt')
def printDebug(str):
	if(DEBUG == True):
		print(str)

def openAndReadFile(filename):
	data = ''
	with open(filename, 'r') as myfile:
		data=myfile.read()#.replace('\n', '')
	myfile.close()
	return data

def tag_visible(element):
    if(element.parent.name in ['style', 'script', 'head', 'meta', '[document]']):
        return False
    if(isinstance(element, Comment)):
        return False
    return True

def text_from_html(body):
    soup = BeautifulSoup(body, 'lxml')
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)  
    return u" ".join(t.strip() for t in visible_texts)

def computeTF(tokenDict, text): # frequency of tokens in doc / total num of words
	tfDict = {}
	count = len(text)
	for token, num in tokenDict.items():
		roundedNum = "{0:.8f}".format(num / float(count))
		tfDict[token] = roundedNum
	return tfDict

def computeIDF(documentList): # log(numDocuments/numDocuments containing token i)
	idfDict = {}
	count = len(documentList)

	return None

def printDict(d):
	for k, v in sorted(d.items()):
		print(str(k) + ": " + str(v))

def saveDictToFile(d, filename):
	with open(filename, 'wb') as myfile:
		pickle.dump(d, myfile)
	myfile.close()

def loadFileToDict(filename):
	with open(filename, 'rb') as myfile:
		return pickle.load(myfile)

def writeHumanReadableDictToFile(d):
	printDebug("Writing Human Readable Dict to file...")
	with open('humanReadDict.txt', 'w') as file:
		pprint(d, stream=file)

	    #file.write(json.dumps(d))

def mainWithLoad():
	invertedIndex = loadFileToDict("savedFile")
	writeHumanReadableDictToFile(invertedIndex)
	#printDict(invertedIndex)

def main():
	invertedIndex = defaultdict(dict)
	dirPath = os.path.dirname(os.path.realpath(__file__))
	webpageDir = dirPath+"/WEBPAGES_RAW/"
	printDebug("Opening dir: " + webpageDir);
	for dir in range(1):
		for file in range(500):
			tempDict = defaultdict(int)
			printDebug("Opening and Reading: " + str(dir) + '/' + str(file))
			data = openAndReadFile(webpageDir + str(dir) + '/' + str(file))

			printDebug("Extracting Text from file...")
			textFromFile = text_from_html(data)

			printDebug("Stripping Bad Chars...")
			strippedTextFromFile = re.sub(r'[\W_|^\d]+', ' ', textFromFile)

			printDebug("Tokenizing...")
			tokens = nltk.word_tokenize(strippedTextFromFile)
			for t in tokens:
				if( type(t) != 'unicode'):
					tempDict[t] += 1
			tfDict = computeTF(tempDict, tokens)
			for t in tokens:
				invertedIndex[t][str(dir) + "/" + str(file)] =  tfDict[t]
			#print("Tokens: " + str(tokens))
	printDebug("Inverted Index: ")
	saveDictToFile(invertedIndex, "savedFile")
	#printDict(invertedIndex)

if __name__ == '__main__':
	main()
	mainWithLoad()


# You are not required to use a database. The other option could be storing that
# dictionary into a file and then load that file again into a dictionary in memory
# when you start your retrieval component. The easiest path for doing this would 
# be through serializing/de-serializing the dictionary using the pickle library in python