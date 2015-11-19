# coding=utf-8
# build dictionary from file
# accept single words from console
# return 3 closest words by Levenshtein distance

from operator import itemgetter

keystring = 'йцукенгшщзхъ~фывапролджэ~ячсмитьбю'
RIGHT = dict(zip(keystring, keystring[1:]))
LEFT = dict(zip(keystring[1:], keystring))


def build_dictionary(path):
    """
    :param path: path to word list
    :return list of words
    :type path: str
    :type return: list
    Read words from list. Assume one word per line.
    """
    return open(path).read().split()


def distance(k1, k2):
    """
    Return distance coefficient for 2 letters
    0.5 for adjacent letters in the same row, 1 for the rest
    """
    left = LEFT.get(k1, None)
    right = RIGHT.get(k1, None)
    if k2 == left or k2 == right:
        return 0.5
    else:
        return 1

    # fixme works on p3, doesnt on p2, fails string comparisons


def levenshtein(s, d):
    """
    Compute Levenshtein distance between two strings
    Adjacent substitutions cost 0.5

    >>> levenshtein('слон', 'сдон')
    0.5

    >>> levenshtein('see', 'hear')
    3

    >>> levenshtein('pirate', 'private')
    2

    >>> levenshtein('lord', 'board')
    2
    """

    m = len(s)
    n = len(d)

    matrix = []
    for i in range(n+1):
        matrix.append([0]*(m+1))

    for i in range(n+1):
        matrix[i][0] = i
    for j in range(m+1):
        matrix[0][j] = j

    for i in range(1, m+1):
        for j in range(1, n+1):
            if s[i-1] == d[j-1]:
                matrix[j][i] = matrix[j-1][i-1]
            else:

                # if doing substitution, check letters for adjacency
                if matrix[j-1][i-1] < matrix[j][i-1] and matrix[j-1][i-1] < matrix[j-1][i]:
                    matrix[j][i] = distance(s[i-1], d[j-1]) + matrix[j-1][i-1]

                else:  # use add/remove weight = 1
                    matrix[j][i] = 1 + min(
                        matrix[j][i-1],
                        matrix[j-1][i]
                    )

    return matrix[n][m]


def get_neighbors(n, item, dictionary):
    """
    :param n: number of neighbors to return
    :param item: word
    :param dictionary: list of available words
    Return item's n nearest neighbors from the dictionary.
    If more than n neighbors receive the same score, return first n.
    """
    nearest = []
    for entry in dictionary:
        distance = levenshtein(item, entry)

        # slots open
        if len(nearest) < n:

            # add new neighbor and sort the list
            nearest.append((entry, distance))
            nearest = sorted(nearest, key=itemgetter(1))

        else:

            # new neighbor closer than the farthest so far
            if distance < nearest[-1][1]:
                nearest.pop()
                nearest.append((entry, distance))
                nearest = sorted(nearest, key=itemgetter(1))  # fixme spawn fewer lists?

    return nearest


def main():
    dictionary = build_dictionary('words.txt')

    try:
        word = raw_input('Введите слово: ')
    except NameError:  # python 3
        word = input('Введите слово: ')

    neighbors = get_neighbors(3, word, dictionary)
    for item in neighbors:
        print(item[0])

if __name__ == '__main__':
    main()