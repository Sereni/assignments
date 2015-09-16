__author__ = 'Sereni'
# get a corpus
# tokenize and stem
# lemmatize
# remove stopwords -- document it
# make an index; sort by term first, then doc id

# unrelated task: search any engine with boolean and text query; compare results, describe

import os
import lxml.etree as et
from pymorphy2 import MorphAnalyzer
from pymorphy2.tokenizers import simple_word_tokenize


class Corpus(object):

    def __init__(self, directory, stopwords):
        """
        :param directory: path to the directory containing corpus files
        :param stopwords: path to stopword file
        """
        self.documents = []
        self.stopwords = self.get_stopwords(stopwords)
        self.index = {}

        for root, dirs, files in os.walk(directory):
            for f in files:
                if f.startswith('.'):
                    continue
                with open(os.path.join(root, f)) as document:
                    doc = Document(document)
                    self.add(doc)

    def get_stopwords(self, path):
        with open(path) as f:
            return set(f.read().split('\n'))

    def remove_stopwords(self):
        for document in self.documents:
            document.lemmas = document.lemmas.difference(self.stopwords)

    def add(self, document):
        self.documents.append(document)

    def build_index(self):
        for document in self.documents:
            for term in document.lemmas:
                try:
                    self.index[term].add(document.name)
                except KeyError:
                    self.index[term] = {document.name}

    def print_index(self, path):
        """
        :param path: path to write the index
        """
        f = open(path, 'w')
        for term, documents in sorted(self.index.items()):
            f.write('{0}: {1}\n'.format(term, ', '.join(documents)))


class Document(object):

    def __init__(self, docfile):
        self.name = os.path.basename(docfile.name)
        try:
            self.text = self.parse(docfile)
            self.tokens = set(self.tokenize(self.text.decode()))
            self.lemmas = self.lemmatize(self.tokens)
        except et.XMLSyntaxError:  # prepare to evacuate soul
            self.text = b''
            self.tokens = set([])
            self.lemmas = set([])

    def parse(self, document):
        """
        :param document: newspaper article file object
        :param return: text contents of the article
        """
        root = et.parse(document)
        text_node = root.find('TEXT')
        text = et.tostring(text_node, method='text', encoding='utf-8')
        return text

    def tokenize(self, text):
        return simple_word_tokenize(text)

    def lemmatize(self, tokens):
        """
        :param tokens: a list of tokens to lemmatize
        """
        analyzer = MorphAnalyzer()
        return {analyzer.parse(token)[0].normal_form for token in tokens}

corpus = Corpus(os.path.join(os.getcwd(), '2015'), os.path.join(os.getcwd(), 'stopwords_ru'))
corpus.remove_stopwords()  # which proves this method actually belongs to the Document
corpus.build_index()
corpus.print_index(os.path.join(os.getcwd(), 'index'))