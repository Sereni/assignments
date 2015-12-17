import math
import os
import lxml.etree as et
from sklearn.grid_search import GridSearchCV
from sklearn.svm import SVC
from sklearn.naive_bayes import MultinomialNB
from pymystem3 import Mystem
from pymorphy2 import MorphAnalyzer
from pymorphy2.tokenizers import simple_word_tokenize
from scipy.sparse import hstack, vstack, coo_matrix
from collections import Counter

DEFAULTS = {
    'A': 0,
    'ADV': 0,
    'ADVPRO': 0,
    'ANUM': 0,
    'APRO': 0,
    'COM': 0,
    'CONJ': 0,
    'INTJ': 0,
    'NUM': 0,
    'PART': 0,
    'PR': 0,
    'S': 0,
    'SPRO': 0,
    'V': 0,
}


class Corpus(object):
    def __init__(self, directory):
        """
        :param directory: path to the directory containing corpus files
        """
        self.documents = []
        self.pos_data = []
        self.index = {}
        self.idf = {}  # yay to silent changes. no more tfidf included.
        self.tfidf = []  # just kidding, returned it after an hour, but now it's a list
        self.data = []

        for root, dirs, files in os.walk(directory):
            for f in files:
                if f.startswith('.'):
                    continue
                with open(os.path.join(root, f)) as document:
                    doc = Document(document)
                    self.add(doc)

        # do all the things
        self.build_pos()
        self.build_index()
        self.build_idf()

    def add(self, document):
        self.documents.append(document)

    def build_pos(self):

        m = Mystem()
        counter = Counter(DEFAULTS)

        for doc in self.documents:

            # parse with mystem
            data = m.analyze(doc.text)

            # get POS and count for each sentence
            pos = [word.get('analysis', None)[0]['gr'].split('(')[0].split(',')[0].split('=')[0]
                   for word in data if word.get('analysis', None)]
            counter.update(pos)

            # append to dataset
            self.pos_data.append([counter[key] for key in sorted(counter)])

            # reset counter
            counter = Counter(DEFAULTS)

    def build_index(self):
        for document in self.documents:
            for term, count in document.lemmas.items():
                try:
                    self.index[term].add(document.name)
                except KeyError:
                    self.index[term] = {document.name}

    def build_idf(self):
        self.idf = {key: math.log(len(self.documents)/len(self.index[key])) for key, value in self.index.items()}


class Document(object):
    def __init__(self, docfile):
        self.name = os.path.basename(docfile.name)

        self.text = self.parse(docfile)

        self.tokens = set(self.tokenize(self.text))
        self.lemmas = self.lemmatize(self.tokens)

    def parse(self, document):
        """
        :param document: newspaper article file object
        :param return: text contents of the article
        """
        try:
            root = et.parse(document)
            text_node = root.find('TEXT')
            if text_node:
                text = et.tostring(text_node, method='text', encoding='utf-8').decode()
            else:
                text = document.read()  # plain text
            return text

        except et.XMLSyntaxError:
            return document.read()


    def tokenize(self, text):
        return simple_word_tokenize(text)

    def lemmatize(self, tokens):
        """
        :param tokens: a list of tokens to lemmatize
        """
        analyzer = MorphAnalyzer()
        return Counter([analyzer.parse(token)[0].normal_form for token in tokens if len(token) > 1])


def make_tfidf(corpora):
    """
    Make a tf-idf table for each document in the corpus using lemmas from all corpora
    """

    # build joint wordlist
    joint_wordlist = set()
    for corpus in corpora:
        joint_wordlist = joint_wordlist.union(set([word for word, docs in corpus.index.items()]))

    joint_wordlist = list(joint_wordlist)  # fix lemma positions

    for corpus in corpora:
        for document in corpus.documents:

            document_tfidf = []
            for lemma in joint_wordlist:
                count = document.lemmas.get(lemma, 0)
                idf = corpus.idf.get(lemma, 0)
                document_tfidf.append(count*idf)  # store lemmas positionally

            corpus.tfidf.append(document_tfidf)  # documents are positionally aligned with pos_data


def main():

    corpus1 = Corpus('tfidf_corpus/06')
    corpus2 = Corpus('tfidf_corpus/sovsport')
    testing_corpus = Corpus('tfidf_corpus/testing')  # articles from rbc in a separate folder

    make_tfidf([corpus1, corpus2, testing_corpus])
    corpus1.data = hstack([coo_matrix(corpus1.pos_data), coo_matrix(corpus1.tfidf)])
    corpus2.data = hstack([coo_matrix(corpus2.pos_data), coo_matrix(corpus2.tfidf)])
    testing_corpus.data = hstack([coo_matrix(testing_corpus.pos_data), coo_matrix(testing_corpus.tfidf)])

    features = vstack([corpus1.data, corpus2.data])
    target = [0] * corpus1.data.shape[0] + [1] * corpus2.data.shape[0]

    params = {
        'C': (1.0, 2.0, 3.0)
    }

    cls = GridSearchCV(SVC(), params)
    cls.fit(features, target)
    print('Best score (SVC): ')
    print(cls.best_score_)

    bayes = GridSearchCV(MultinomialNB(), {})  # use default smoothing
    bayes.fit(features, target)
    print('Best score (Bayes): ')
    print(bayes.best_score_)  # по-моему, он переучился =\

    if cls.best_score_ > bayes.best_score_:
        test_cls = cls  # is this even legal?
    else:
        test_cls = bayes

    testing_data = hstack([coo_matrix(testing_corpus.pos_data), coo_matrix(testing_corpus.tfidf)])
    right = []
    wrong = []

    for i in range(len(testing_corpus.documents)):
        category = test_cls.predict(testing_data.getrow(i))
        if category != 0:
            wrong.append(corpus1.documents[-i].text)
        else:
            right.append(corpus1.documents[-i].text)

    print('Верные: ')
    print('\n'.join(right[:3]))
    print()
    print('Неверные: ')
    print('\n'.join(wrong))  # will probably have fewer than 3 in wrong

if __name__ == '__main__':
    main()