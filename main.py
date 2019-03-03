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
		self.mainIndex = defaultdict(dict)
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
			if(word in readableIndex[document]):
				totalScore+=readableIndex[document]
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
	#printDict(invertedIndex)




def makeBasicInvertedIndex():
	dirRange = 1
	fileRange = 100
	wholeCorpusSize = fileRange*dirRange
	invertedIndex = defaultdict(dict)
	
	invIndex = InvertedIndex("Yes")
	dirPath = os.path.dirname(os.path.realpath(__file__))
	webpageDir = dirPath+"/WEBPAGES_RAW/"
	printDebug("Opening dir: " + webpageDir);
	for dir in range(75,76):
		for file in range(100,109):
			wholeCorpusSize+=1
			tempDict = defaultdict(int)
			printDebug("Opening and Reading: " + str(dir) + '/' + str(file))
			data = openAndReadFile(webpageDir + str(dir) + '/' + str(file))

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
			for t in tokensFiltered:
				tempTerm = Term(t)
				tempTerm.setAttributes(tempDict[t])	
				tempTerm.incrementDocFreq()
				tempTerm.postingList.add(str(dir) + "/" + str(file))
				invIndex.readableIndex[str(dir) + "/" + str(file)][t] =  tempTerm.calcTermFreqWeight()
				invIndex.allTerms[t] = tempTerm
	saveDictToFile(invIndex.readableIndex, "savedFile")
	bestDocs = {}
	allDocWeights = {}
	finalToRet = {}
	for docName in invIndex.readableIndex.keys(): #Get every document
		#Get query values/table
		temp = invIndex.fillOutQueryInfo("computer Eppstein", wholeCorpusSize)
		for q in temp:
			if(q in invIndex.readableIndex[docName]):#for each query in doc
				finalToRet[docName] = temp[q] #get the weights for queries
				allDocWeights[docName] = invIndex.readableIndex[docName][q]#getTheWieght for doc

	weights = allDocWeights.values();
	divideBy = naturalize(weights)

	for k,v in allDocWeights.items():
		finalToRet[k] = finalToRet[k]*allDocWeights[k]/divideBy
 
	print(sorted(finalToRet.items(), key=operator.itemgetter(1))[0:10])




def main():
	makeBasicInvertedIndex()
	loadSavedFileToHumanReadableDict()


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