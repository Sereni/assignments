from pymystem3 import Mystem
import re
import numpy as np
from matplotlib import mlab
from matplotlib import pyplot as plt


class Corpus():

    def __init__(self, path):

        self.text = open(path).read().lower()
        self.sentences = [sentence for sentence in re.split(r'(?:[.]\s*){3}|[.?!]', self.text) if len(sentence) > 1]
        self.pos_data = []

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

        self.data = np.array(self.pos_data)


def main():
    articles = Corpus('corpus1.txt')
    anna = Corpus('corpus2.txt')

    data = np.vstack((articles.data, anna.data))
    p = mlab.PCA(data)
    n = len(articles.data)

    plt.figure()
    plt.plot(p.Y[:n, 0], p.Y[:n, 1], 'or',
             p.Y[n:, 0], p.Y[n:, 1], 'xb',)
    plt.show()

    # по графику видим, что выборки практически неразличимы по этим параметрам
    # нужное пороговое значение не находится

if __name__ == '__main__':
    main()