import nltk
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
d
ef printDebug(str):
	if(DEBUG == True):
		print(str)

def openAndReadFile(filename):
	data = ''
	with open(filename, 'r') as myfile:
		data=myfile.read().replace('\n', '')
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


def main():
	print("")
	printDebug("Opening file: test.html")
	data = openAndReadFile('test.html')
	
	printDebug("Extracting Text from file...")
	textFromFile = text_from_html(data)

	printDebug("Stripping Bad Chars...")
	strippedTextFromFile = re.sub(r'[\W_]+', ' ', textFromFile)
	
	printDebug("Tokenizing...")
	tokens = nltk.word_tokenize(strippedTextFromFile)
	print("Tokens: ", end = "")
	print(tokens)


main()