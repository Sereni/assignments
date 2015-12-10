import re
from sklearn.grid_search import GridSearchCV
from sklearn.svm import SVC
from pymystem3 import Mystem
from collections import Counter

# эта штука выполняется очень-очень долго
# если надоело, можно ограничить количество предложений тут
limit = 10000

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

class Corpus():

    def __init__(self, path, doc_id, limit):
        """
        :param doc_id: numerical id of a document, pass manually
        """

        self.text = open(path).read().lower().replace('\n', '.')
        # need a better regex
        self.sentences = [sentence for sentence in re.split(r'(?:[.]\s*){3}|[.?!]', self.text) if sentence and len(sentence.split()) > 2]
        self.pos_data = []
        self.testing_data = []
        self.id = doc_id

        m = Mystem()
        counter = Counter(DEFAULTS)

        if not limit or limit > len(self.sentences):
            limit = len(self.sentences)

        for sentence in self.sentences[:limit]:

            # parse with mystem
            data = m.analyze(sentence)

            # get POS and count for each sentence
            pos = [word.get('analysis', None)[0]['gr'].split('(')[0].split(',')[0].split('=')[0]
                   for word in data if word.get('analysis', None)]
            counter.update(pos)

            # append to dataset
            self.pos_data.append([counter[key] for key in sorted(counter)])

            # reset counter
            counter = Counter(DEFAULTS)


def main():
    anna = Corpus('corpus2.txt', 0, limit=limit)
    capital = Corpus('capital', 1, limit=limit)

    features = anna.pos_data[:-100] + capital.pos_data[:-100]
    target = [anna.id] * (len(anna.pos_data)-100) + [capital.id] * (len(capital.pos_data)-100)

    params = {
        'C': (1.0, 2.0, 3.0)
    }

    cls = GridSearchCV(SVC(), params)
    cls.fit(features, target)
    print('Best score: ')
    print(cls.best_score_)

    testing_data = anna.pos_data[-100:]
    right = []
    wrong = []

    for i in range(100):
        category = cls.predict(testing_data[i])
        if category != 0:
            wrong.append(anna.sentences[-i])
        else:
            right.append(anna.sentences[-i])

        if len(wrong) > 2 and len(right) > 3:
            break  # found enough

    print('Верные: ')
    print('\n'.join(right[:3]))
    print()
    print('Неверные: ')
    print('\n'.join(wrong[:3]))

if __name__ == '__main__':
    main()
