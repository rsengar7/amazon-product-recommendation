import sys
from re import sub
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

'''
Pre-processing of the Text Data
'''

class PreProcessing():
    ''' Constructor Initialization '''
    def __init__(self):
        self.sub = sub
        self.stemmer = WordNetLemmatizer()
        self.stopwords = list(set(stopwords.words('english')))
        

    def __str__(self):
        return self.__class__.__name__

    def clean_text(self, text):
        if isinstance(text, str):
            ''' Pre-Processing of the text '''
            text = self.sub(r"can't", "cannot", text)
            text = self.sub(r"won't", "will not", text)
            text = self.sub(r"want's", "wants", text)
            text = self.sub(r"when'd", "when did", text)
            text = self.sub(r"can'tif", "cannot if", text)
            text = self.sub(r"y'know", "you know", text)
            text = self.sub(r"y'all", "you all", text)
            text = self.sub(r"y'think", "you think", text)
            text = self.sub(r"d'you", "do you", text)
            text = self.sub(r"\'s", " is", text)
            text = self.sub(r"\'d", " had", text)
            text = self.sub(r"n't", " not", text)
            text = self.sub(r"\'ve", " have", text)
            text = self.sub(r"\'ll", " will", text)
            text = self.sub(r"\'m", " am", text)
            text = self.sub(r"\'re", " are", text)
            text = self.sub(r"\'ve", " have", text)
            text = self.sub(r"can’t", "cannot", text)
            text = self.sub(r"won’t", "will not", text)
            text = self.sub(r"want’s", "wants", text)
            text = self.sub(r"when’d", "when did", text)
            text = self.sub(r"can’tif", "cannot if", text)
            text = self.sub(r"y’know", "you know", text)
            text = self.sub(r"y’all", "you all", text)
            text = self.sub(r"y’think", "you think", text)
            text = self.sub(r"d’you", "do you", text)
            text = self.sub(r"\’s", " is", text)
            text = self.sub(r"\’d", " had", text)
            text = self.sub(r"n’t", " not", text)
            text = self.sub(r"\’ve", " have", text)
            text = self.sub(r"\’ll", " will", text)
            text = self.sub(r"\’m", " am", text)
            text = self.sub(r"\’re", " are", text)
            text = self.sub(r"\’ve", " have", text)
            text = text.replace(":"," ")
            text = text.replace("?","")
    
            return text

    # Stemming of words
    def word_stemmer(self, text):
        if isinstance(text, str):
            text = " ".join([self.stemmer.lemmatize(word, pos="v") for word in text.split(" ")])
            return text
        else:
            return ""
            
    # Remove Punctuations from String
    def remove_punctuations(self, text):
        if isinstance(text, str):
            return self.sub(r'[^\w\s]', '', text)
        else:
            return ""

    # Fill Missing Values with empty string
    def missing_values(self, reviews):
        if isinstance(reviews, str):
            return reviews if reviews != "" else ""
        else:
            return ""
