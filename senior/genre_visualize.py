from matplotlib import mlab
from matplotlib import pyplot as plt
import numpy as np
import re
from pymystem3 import Mystem
import os

PUNCT = '.,?! )(-"'  # close enough
VOWELS = u'уеыаоэёяию'

FEATURES = [
            'длина предложения в буквах',
            'количество разных букв в предложении',
            'количество гласных в предложении',
            'медиана длины слова',
            'медиана количества гласных в слове',
            'число прилагательных',
            'число наречий',
            'число местоимений',
            'число существительных',
            'число глаголов',
            'длина предложения в словах',
            'средняя длина слова',
            'медианная длина слова'
]


class Corpus():
    def __init__(self, path):

        self.text = open(path).read().lower()
        self.sentences = [sentence for sentence in re.split(r'(?:[.]\s*){3}|[.?!]', self.text) if
                          len(sentence) > 1]
        self.pos_data = []

        # compute all the things!
        # I started having fun with list comprehensions, but it quickly got out of hand...
        # if stuff's too slow, will stick everything into one for-loop.

        # length of sentences in letters
        self.sentence_lengths = [len([char for char in sentence if char not in PUNCT]) for sentence in
                                 self.sentences]

        # number of different letters in the sentence
        self.sentence_letters = [len(set(char for char in sentence if char not in PUNCT)) for sentence in
                                 self.sentences]

        # number of vowels in a sentence
        self.sentence_vowels = [len([char for char in sentence if char in VOWELS]) for sentence in self.sentences]

        # median of letters in a word
        self.median_letters = [np.median([len(word.strip(PUNCT)) for word in sentence.split()]) for sentence in
                               self.sentences]

        # median of vowels in a word
        self.median_vowels = [
            np.median([len([char for char in word if char in VOWELS]) for word in sentence.split()]) for sentence
            in self.sentences]

        # word length params
        self.sentlens = [[len(word) for word in sentence.split()] for sentence in self.sentences if len(sentence) > 1]

        m = Mystem()
        counter = [0, 0, 0, 0, 0]

        for sentence in self.sentences:

            # parse with mystem
            # count adjectives A, nouns S, verbs V, adverbs ADV, pronouns PR
            data = m.analyze(sentence)
            for word in data:
                analysis = word.get('analysis', None)
                if analysis:
                    best = analysis[0]
                    gr = best['gr']
                    if 'S' in gr:
                        counter[3] += 1
                    elif 'ADV' in gr:
                        counter[1] += 1
                    elif 'A' in gr:
                        counter[0] += 1
                    elif 'V' in gr:
                        counter[4] += 1
                    elif 'PR' in gr:
                        counter[2] += 1

            self.pos_data.append(counter)
            counter = [0, 0, 0, 0, 0]

        # and join
        self.data = np.array(list(zip(self.sentence_lengths,
                                      self.sentence_letters,
                                      self.sentence_vowels,
                                      self.median_letters,
                                      self.median_vowels,
                                      [item[0] for item in self.pos_data],
                                      [item[1] for item in self.pos_data],
                                      [item[2] for item in self.pos_data],
                                      [item[3] for item in self.pos_data],
                                      [item[4] for item in self.pos_data],
                                      [len(sentence) for sentence in self.sentlens],
                                      [np.mean(sentence) for sentence in self.sentlens],
                                      [np.median(sentence) for sentence in self.sentlens]
                                      )))


def make_graph(x, y, len1, len2, data, path):
    """
    Write graph with selected coordinates to file
    :param x: index of parameter to plot on the first coordinate
    :param y: index of parameter to plot on the second coordinate
    :param len1: length of first dataset
    :param len2: length of second dataset
    :param data: PCA dataset
    :param path: path to output file
    """
    plt.figure()
    plt.plot(data[:len1, x], data[:len1, y], 'or',
             data[len1:len1+len2, x], data[len1:len1+len2, y], 'xb',
             data[len1+len2:, x], data[len1+len2:, y], 'dg')
    plt.savefig(path, format='png')
    plt.close()


def main():

    # initialize corpora
    articles = Corpus('corpus1.txt')
    anna = Corpus('corpus2.txt')
    sonets = Corpus('corpus3.txt')

    # create image folder if necessary
    imgpath = os.path.join(os.getcwd(), 'images')
    if not os.path.exists(imgpath):
        os.mkdir(imgpath)

    # make data stack and apply PCA
    data = np.vstack((articles.data, anna.data, sonets.data))
    p = mlab.PCA(data)
    len1 = len(articles.data)
    len2 = len(anna.data)

    # plot pairs of features on separate graphs
    for i in range(12):
        for j in range(i+1, 13):
            make_graph(i, j, len1, len2, data=p.Y,
                       path=os.path.join(os.getcwd(), 'images', '%s-%s' % (i, j)))

    with open('svd_results', 'w') as f:
        f.write('eigenvalues:\n')
        f.write('\n'.join([str(item) for item in p.s]))
        f.write('\n')
        f.write('weight vectors:\n')
        f.write('\n'.join(['\t'.join([str(item) for item in row]) for row in p.Wt]))

    sorted_feat = sorted(zip(p.Wt[0], FEATURES), key=lambda x: abs(x[0]))
    print(sorted_feat[-3:])


if __name__ == '__main__':
    main()