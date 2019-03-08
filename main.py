# coding=utf-8
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
import math
import time
import operator
from tkinter import *
from urllib.request import urlopen
import requests
import webbrowser

DEBUG = True;

#nltk.download('punkt')

class Term:
	def __init__(self, wordName):
		self.word = wordName
		self.rawDocumentCount = 0
		self.documentFreq = 0
		self.termFreq = 0
		self.postingList = set()


	def __str__(self):
		return self.word

	def setAttributes(self, tf="def", docFreq="def", docCount="def"):
		if(tf != "def"):
			self.termFreq = tf
		if(docFreq != "def"):
			self.documentFreq = docFreq
		if(docCount != "def"):
			self.rawDocumentCount = docCount

	def incrementDocFreq(self):
		self.documentFreq+=1

	def calcInverseDocFreq(self, corpusSize):
		return math.log(corpusSize/self.documentFreq,10)
	
	def calcTermFreqWeight(self):
		if(self.termFreq == 0):
			return 0
		else:
			return 1 + math.log(self.termFreq,10)

	def calcTF_IDFWeight(self, corpusSize):
		return self.calcInverseDocFreq(corpusSize) * self.calcTermFreqWeight()

class Document:
	def __init__(self, docId):
		self.documentId = docId
		self.allTermsInDoc = {}

	def __str__(self):
		return self.documentId

	def addToDoc():
		return 0



class InvertedIndex:
	def __init__(self, name):
		self.name = name
		self.readableIndex = defaultdict(dict)
		self.allTerms = defaultdict(dict)

	def fillOutQueryInfo(self, query, allDocsLen):
		wordBreakDown = defaultdict(int)
		weights = []
		toRet = defaultdict(dict)
		for word in query.split():
			wordBreakDown[word] += 1#termFreq
		for word in query.split():
			if(word in self.allTerms):
				tempTerm = Term(word)	#ctermFreq          documentFreq
				tempTerm.setAttributes(wordBreakDown[word], self.allTerms[word].documentFreq)
				weights.append(tempTerm.calcTF_IDFWeight(allDocsLen))
				toRet[str(tempTerm)] = tempTerm.calcTF_IDFWeight(allDocsLen)


		divideBy = naturalize(weights)
		for k,v in toRet.items():
			toRet[k] = toRet[k]/divideBy
		return toRet

	def calculateScore(self, query, document):
		totalScore = 0
		for word in query:
			if(word in self.readableIndex[document]):
				totalScore+=self.readableIndex[document]
		return totalScore

def naturalize(weights):
	toRet = []
	for w in weights:
		toRet.append(w**2)
	return math.sqrt(sum(toRet)) 	

def printDebug(str):
	if(DEBUG == True):
		print(str)

def openAndReadFile(filename):
	data = ''
	print (filename)
	with open(filename, 'r', encoding='utf8') as myfile:
		data=myfile.read()
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
	#tfDict = defaultdict(dict)

	count = len(text)
	for token, num in tokenDict.items():
		roundedNum = "{0:.6f}".format(num / float(count))
		tfDict[token] = [roundedNum, num]
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

def loadSavedFileToHumanReadableDict():
	invertedIndex = loadFileToDict("savedFile")
	writeHumanReadableDictToFile(invertedIndex)
	printDict(invertedIndex)

def makeBasicInvertedIndex(query, invIndex):
	dirRange = 74
	fileRange = 500
	wholeCorpusSize = fileRange*dirRange
	
	dirPath = os.path.dirname(os.path.realpath(__file__)) + "WEBPAGES_RAW/"
	webpageDir = "C:\\Users/marky/Downloads/Webpages/WEBPAGES_RAW/"
	printDebug("Opening dir: " + dirPath);
	for dir in range(dirRange):
		for file in range(fileRange):
			wholeCorpusSize+=1
			tempDict = defaultdict(int)
			printDebug("Opening and Reading: " + str(dir) + '/' + str(file))
			data = openAndReadFile(dirPath + str(dir) + '/' + str(file))

			printDebug("Extracting Text from file...")
			textFromFile = text_from_html(data)

			printDebug("Stripping Bad Chars...")
			strippedTextFromFile = re.sub(r'[\W_|^\d]+', ' ', textFromFile)

			printDebug("Tokenizing...")
			tokens = nltk.word_tokenize(strippedTextFromFile)
			tokensFiltered = []
			for t in tokens:
				try:
					t.encode('ascii')
					tokensFiltered.append(t)
				except:
					printDebug("Not ascii")

			for t in tokensFiltered:
				tempDict[t] += 1

			tfDict = computeTF(tempDict, tokensFiltered)
			#printDebug(tfDict)
			#printDebug(sorted(tokensFiltered))
			for t in tokensFiltered:
				tempTerm = Term(t)
				tempTerm.setAttributes(tempDict[t])	
				tempTerm.incrementDocFreq()
				tempTerm.postingList.add(str(dir) + "/" + str(file))
				invIndex.readableIndex[str(dir) + "/" + str(file)][t] =  tempTerm.calcTermFreqWeight()
				invIndex.allTerms[t] = tempTerm
	saveDictToFile(invIndex.readableIndex, "savedFile")
	saveDictToFile(invIndex.allTerms, "allTermsFile")
	return wholeCorpusSize
	

def getTheGoods(query, invIndex,wholeCorpusSize):
	bestDocs = {}
	allDocWeights = {}
	finalToRet = {}
	for docName in invIndex.readableIndex.keys(): #Get every document
		#Get query values/table
		temp = invIndex.fillOutQueryInfo(query, wholeCorpusSize)
		for q in temp:
			if(q in invIndex.readableIndex[docName]):#for each query in doc
				finalToRet[docName] = temp[q] #get the weights for queries
				allDocWeights[docName] = invIndex.readableIndex[docName][q]#getTheWieght for doc

	weights = allDocWeights.values();
	divideBy = naturalize(weights)

	for k,v in allDocWeights.items():
		finalToRet[k] = finalToRet[k]*allDocWeights[k]/divideBy
	print("HERE")
	print(sorted(finalToRet.items(), reverse = True, key=operator.itemgetter(1))[0:20])
	return finalToRet


def loadItemsIntoInvIndex(invIndex):
	invIndex.readableIndex  =  loadFileToDict("savedFile")
	invIndex.allTerms = loadFileToDict("allTermsFile")

def link_exists(url):
	#link = http.client.HTTPConnection(url)
	try:
		#print(requests.head("http://" + url, allow_redirects  =True).status_code)
		return requests.head("http://" + url,allow_redirects  =True).status_code != 404
	except:
		return True

def queryReport(finalToRet):
	dirPath = os.path.dirname(os.path.realpath(__file__))
	ret = []
	with open(dirPath+"/WEBPAGES_RAW/bookkeeping.json") as f:
		data = json.load(f)
	counter = 0
	for item in (sorted(finalToRet.items(), reverse = True, key=operator.itemgetter(1))[0:40]):
		if link_exists(data[item[0]]):
			ret.append(data[item[0]])
			counter += 1
			if counter == 20:
				return ret
	#return [data[item[0]] for item in (sorted(finalToRet.items(), reverse = True, key=operator.itemgetter(1))[0:40]) if link_exists(data[item[0]])]
	#counter = 1
	#for item in (sorted(finalToRet.items(), reverse = True, key=operator.itemgetter(1))[0:20]):
	#	print(str(counter) + ". " + "key: " + item[0] + " url: " + data[item[0]])
	#	counter += 1

open_web_browser = lambda url: (lambda x: webbrowser.open_new(url))

def startSearch(entry, invIndex, frame):
	finalToRet = getTheGoods(entry.get(), invIndex, 500)
	top20 = queryReport(finalToRet)
	for i in range(len(top20)):
		link = Label(frame, text=top20[i], fg="blue", cursor = "hand2", width=75, anchor = W )
		link.grid(row=i+2,column = 0, sticky=W)
		link.bind("<Button>", open_web_browser(top20[i]))
#RUN LIKE THIS:
#python3 main.py [load|*] QUERY WORDS
def main():
	queryStr = ""
	if(len(sys.argv) < 3):
		print("Not enough arguments! Please put query!")
		sys.exit(0)

	for arg in sys.argv[2:]:
		queryStr+=(" " + arg)
	print(queryStr)

	wholeCorpSize = 500;
	invIndex = InvertedIndex("Yes")

	if(sys.argv[1] != 'load'):
		wholeCorpSize = makeBasicInvertedIndex(queryStr, invIndex)
	else:
		loadItemsIntoInvIndex(invIndex)

#	print(invIndex.readableIndex)
	#finalToRet = getTheGoods(queryStr, invIndex, 500) #DOES THE COSINE SHIT
	#loadSavedFileToHumanReadableDict()

	#GUI
	root = Tk()
	root.title("Search Engine")
	frame = Frame(root)

	labelText = StringVar()
	label = Label(frame, text="CS121 Search Engine")
	button = Button(frame, text="Search", command=lambda: startSearch(entry, invIndex, frame))
	entry = Entry(frame, width=50)
	entry.grid(row=1, pady=10, sticky=W, padx = 5)
	button.grid(row=1, column=1, pady=10, sticky=W, padx = 5)
	label.grid(row = 0)
	frame.pack()
	root.mainloop()
	#queryReport(finalToRet)


if __name__ == '__main__':
	start_time = time.time()
	main()
	print("--- %s seconds ---" % (time.time() - start_time))


 
 
 
 
 
# if __name__ == '__main__':
#     with open('C:/Users/james/PycharmProjects/searchenginebasicreport/savedFile', 'rb') as handle:
#         invertedIndex = pickle.loads(handle.read())
 
#     with open('C:/Projects/SearchEngineBasic-master/WEBPAGES_RAW/bookkeeping.json') as f:
#         data = json.load(f)
#     responses = ["Informatics", "Mondego", "Irvine"]
#     print("\n\n")
#     for response in responses:
#         sorted_keys = sorted(invertedIndex[response].keys(), reverse=True,
#                              key=lambda y: (invertedIndex[response][y]))
#         sortedKeyCounter = 0
#         print("Top 5 URLS for " + response)
#         for key in sorted_keys:
#             print(str(sortedKeyCounter + 1) + ".    " + data[key])
#             # print(key + " " + invertedIndex[response][key])
#             sortedKeyCounter += 1
#             if sortedKeyCounter == 5:
#                 break
#         print("\n\n")
 
#     print("\n\n"
#           "Some interesting metrics..."
#           "\nThe number of documents is:   " +str(37497) +
#           "\nThe number of tokens is:      " + str(len(invertedIndex)) +
#           "\nThe size of the file is:      277MB"
#           )


# You are not required to use a database. The other option could be storing that
# dictionary into a file and then load that file again into a dictionary in memory
# when you start your retrieval component. The easiest path for doing this would 
# be through serializing/de-serializing the dictionary using the pickle library in python

# Extra	credit	will	be	given	for	ideas	that	improve	the	quality	of	the	retrieval,	so	you	may	add	more	
# metadata	to	your	index,	if	you	think	it	will	help	improve	the	quality	of	the	retrieval.	For	this,	instead	
# of	storing	a	simple	TF‐IDF	count	for	every	page,	you	can	store	more	information	related	to	the	page	
# (e.g.	position	of	the	words	in	the	page).	To	store	this	information,	you	need	to	design	your	index	in	
# such	a	way	that	it	can	store	and	retrieve	all	this	metadata	efficiently.	Your	index	lookup	during	search	
# should	not	be	horribly	slow,	so	pay	attention	to	the	structure	of	your	index	



	# def calculateCosineScore(query):
	# 	scores = {}
	# 	length = []
	# 	for term in query:
	# 		currScore = 0
	# 		if(term in readableIndex[document]):
	# 			currScore+=readableIndex[document][term] #calc wt
	# 		for doc in mainIndex[document].postingList:
	# 			scores[doc]+=