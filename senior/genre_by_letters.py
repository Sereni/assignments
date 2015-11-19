# coding=utf-8
# encoding=utf-8
import numpy as np
import re
from matplotlib import pyplot as plt

PUNCT = '.,?! )(-"'  # close enough
VOWELS = u'уеыаоэёяию'


class Corpus():

    def __init__(self, path):

        self.text = open(path).read().lower()
        self.sentences = [sentence for sentence in re.split(r'(?:[.]\s*){3}|[.?!]', self.text) if len(sentence) > 1]

        # compute all the things!
        # I started having fun with list comprehensions, but it quickly got out of hand...
        # if stuff's too slow, will stick everything into one for-loop.

        # length of sentences in letters
        self.sentence_lengths = [len([char for char in sentence if char not in PUNCT]) for sentence in self.sentences]

        # number of different letters in the sentence
        self.sentence_letters = [len(set(char for char in sentence if char not in PUNCT)) for sentence in self.sentences]

        # number of vowels in a sentence
        self.sentence_vowels = [len([char for char in sentence if char in VOWELS]) for sentence in self.sentences]

        # median of letters in a word
        self.median_letters = [np.median([len(word.strip(PUNCT)) for word in sentence.split()]) for sentence in self.sentences]

        # median of vowels in a word
        self.median_vowels = [np.median([len([char for char in word if char in VOWELS]) for word in sentence.split()]) for sentence in self.sentences]

        # and join
        self.data = np.array(list(zip(self.sentence_lengths,
                                  self.sentence_letters,
                                  self.sentence_vowels,
                                  self.median_letters,
                                  self.median_vowels,
                                      )))


def main():
    # cwd = os.getcwd()
    articles = Corpus('corpus1.txt')
    anna = Corpus('corpus2.txt')
    plt.figure()
    plt.plot(articles.data[:, 0], articles.data[:, 3], 'or',
             anna.data[:, 0], anna.data[:, 3], 'xb')
    plt.show()

    # # see all plots
    # for i in range(4):
    #     for j in range(i+1, 5):
    #         plt.plot(articles.data[:, i], articles.data[:, j], 'or', anna.data[:, i], anna.data[:, j], 'xb')
    #         plt.show()


if __name__ == '__main__':
    main()