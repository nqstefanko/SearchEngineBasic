from __future__ import print_function
import nltk
import math
import lxml
import re, os, sys
import pickle
import string
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
		tfDict[token] = num / float(count)
	return tfDict

def computeIDF(documentList): # log(numDocuments/numDocuments containing token i)
	idfDict = {}
	count = len(documentList)

	return None

def printDict(d):
	for k, v in sorted(d.items()):
		print(str(k) + ": " + str(v))

def saveDictToFile(d, filename):
	with open(filename, 'w') as myfile:
		pickle.dump(d, myfile)
	myfile.close()

def loadFileToDict(filename):
	with open(filename, 'r') as myfile:
		return pickle.load(myfile)

def mainWithLoad():
	invertedIndex = loadFileToDict("myIndex")
	#printDict(invertedIndex)

def main():
	invertedIndex = defaultdict(list)
	printDebug("Opening dir: C:/Users/marky/Downloads/webpages/WEBPAGES_RAW/")
	for dir in range(74):
		for file in range(500):
			tempDict = defaultdict(int)
			data = openAndReadFile('C:/Users/marky/Downloads/webpages/WEBPAGES_RAW/' + str(dir) + '/' + str(file))

			printDebug("Extracting Text from file...")
			textFromFile = text_from_html(data)

			printDebug("Stripping Bad Chars...")
			strippedTextFromFile = re.sub(r'[\W_]+', ' ', textFromFile)

			printDebug("Tokenizing...")
			tokens = nltk.word_tokenize(strippedTextFromFile)
			for t in tokens:
				tempDict[t] += 1
			tfDict = computeTF(tempDict, tokens)
			for t in tokens:
				invertedIndex[t].append((str(dir) + "/" + str(file), tfDict[t]))
			#print("Tokens: " + str(tokens))
	print("Inverted Index: ")
	saveDictToFile(invertedIndex, "myIndex")
	#printDict(invertedIndex)

if __name__ == '__main__':
	#main()
	mainWithLoad()