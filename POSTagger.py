'''
Created on May 8, 2014

@author: Dani
'''
from collections import defaultdict


import nltk


myDict = defaultdict(str)

def POSTag(docs):
    print "Tagging..."
    for doc in docs:                       
        vocab = doc['Description']+' '+doc['Title']
        print ( type(vocab) ) 
        #Converting to lowercase
        vocab = vocab.lower()
        #tokenize
        tokens = nltk.word_tokenize(vocab)
        #Removing punctuation
        vocabTagged = nltk.pos_tag(tokens)
        for key, val in vocabTagged:
            myDict[key] += val
        
    return myDict

