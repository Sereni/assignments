import os
import lxml.etree as et
import math
from collections import Counter
from pymorphy2 import MorphAnalyzer
from pymorphy2.tokenizers import simple_word_tokenize
from operator import itemgetter


class Corpus(object):
    def __init__(self, directory):
        """
        :param directory: path to the directory containing corpus files
        """
        self.documents = []
        self.index = {}
        self.idf = {}
        self.tfidf = {}

        for root, dirs, files in os.walk(directory):
            for f in files:
                if f.startswith('.'):
                    continue
                with open(os.path.join(root, f)) as document:
                    doc = Document(document)
                    self.add(doc)

    def add(self, document):
        self.documents.append(document)

    def build_index(self):
        for document in self.documents:
            for term, count in document.lemmas.items():
                try:
                    self.index[term].add(document.name)
                except KeyError:
                    self.index[term] = {document.name}

    def build_idf(self):
        self.idf = {key: math.log(len(self.documents)/len(self.index[key])) for key, value in self.index.items()}

    def build_tfidf(self):
        for document in self.documents:
            for lemma, count in document.lemmas.items():
                self.tfidf['{0}: {1}'.format(document.name, lemma)] = count * self.idf[lemma]


class Document(object):
    def __init__(self, docfile):
        self.name = os.path.basename(docfile.name)
        try:
            self.text = self.parse(docfile)
            self.tokens = set(self.tokenize(self.text.decode()))
            self.lemmas = self.lemmatize(self.tokens)
        except et.XMLSyntaxError:
            self.text = b''
            self.tokens = set([])
            self.lemmas = Counter([])

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
        return Counter([analyzer.parse(token)[0].normal_form for token in tokens if len(token) > 1])


def main():
    corpus = Corpus(os.path.join(os.getcwd(), 'tfidf_corpus'))
    corpus.build_index()
    corpus.build_idf()
    corpus.build_tfidf()
    ranked = sorted([(key, value) for key, value in corpus.tfidf.items()], key=itemgetter(1), reverse=True)[:10]
    print([word for (word, score) in ranked])

if __name__ == '__main__':
    main()