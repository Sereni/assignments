__author__ = 'Sereni'
import os
from collections import deque
import cProfile
import time
import re

GROUPING_SPACE_REGEX = re.compile('([^\w_-]|[+])', re.U)


# copied from pymorphy2
def simple_word_tokenize(text):
    """
    Split text into tokens. Don't split by hyphen.
    """
    return [t for t in GROUPING_SPACE_REGEX.split(text)
            if t and not t.isspace()]


class Query():

    def __init__(self, path):
        self.terms = self.read_query(path)

    @staticmethod
    def read_query(query):
        """
        @query: path to query file, one term per line
        @return: a list of query terms
        """
        return open(query).read().split('\n')


class Corpus():

    def __init__(self, path):
        self.lines = self.get_lines(path)
        self.index = {}
        self.rhyme_index = {}

    @staticmethod
    def get_lines(path):  # uh, note that's exactly the same as read_query
        """
        @path: path to corpus file
        @return: a list of lines
        An empty line goes at the end to prevent index errors.
        It also allows to remove 2 if-checks from lookup.
        """
        return open(path).read().split('\n') + ['']

    def build_index(self):

        for i in range(len(self.lines)):

            # todo that's one place to optimize, but only if preprocessing counts
            tokens = simple_word_tokenize(self.lines[i])

            # pre-evaluate add method
            # can't say if helps much =\
            add = set.add

            for token in tokens:
                try:
                    add(self.index[token], i)
                except KeyError:
                    self.index[token] = {i}

    @staticmethod
    def last_word(line):
        """
        @line: a string of text
        @return: last word of the line split off by space and clear of punctuation
        """
        punctuation = '.,?!:;-)"\''  # good enough
        return line.rstrip(punctuation).split(' ')[-1]

    @staticmethod
    def is_rhyme(a, b):
        """
        @a, b: str
        @return: bool
        """
        return a[-3:] == b[-3:]

    def build_rhyme_index(self):

        # move add function to local space
        add = set.add

        # set up a sliding window of words
        window = deque([self.last_word(self.lines[i]) for i in [0, 1, 2]],  # that's last words of first 3 lines
                       maxlen=3)

        for i in range(3, len(self.lines)):

            # compare 1st item against 2nd and 3rd
            for j in [1, 2]:
                if self.is_rhyme(window[0], window[j]):

                    # update the index
                    try:
                        add(self.rhyme_index[window[0]], window[j])
                    except KeyError:  # fixme try-except takes lots of time, want a better way
                        self.rhyme_index[window[0]] = {window[j]}

                    # add the reverse entry as well
                    try:
                        add(self.rhyme_index[window[j]], window[0])
                    except KeyError:
                        self.rhyme_index[window[j]] = {window[0]}

            # slide the window
            # because of maxlen in deque, the first word pops out
            window.append(self.last_word(self.lines[i]))  # doesn't consider the last line, but eh, it's empty

            # todo consider adding checks to slide the window 2-3 items forward
            # wonder what's more expensive

    def get_rhymes(self, term):
        return ', '.join(list(self.rhyme_index.get(term, [])))

    def search(self, query):
        """
        @query: string to search for
        @return: indices of lines where the string has been found
        """
        return self.index.get(query, [])

    def get_context(self, i):
        """
        @i: line id
        @return: string of lines i-1, i and i+1 (if available)
        """
        # added a fake empty line to our corpus, so this always works
        prev_line = self.lines[i-1]
        next_line = self.lines[i+1]

        return '%s\n%s\n%s' % (prev_line, self.lines[i], next_line)

    def get_snippets(self, query):
        """
        @query: search string
        @return: list of 3-line snippets
        """
        ids = self.search(query)
        return '\n\n'.join([self.get_context(i) for i in ids])


def snippet_search(corpus, query):
    """
    @corpus: Corpus object
    @query: Query object
    @return: list of snippets
    """
    return [corpus.get_snippets(term) for term in query.terms]


def rhyme_search(corpus, query):
    """
    @corpus: Corpus object
    @query: Query object
    @return: list of rhyming words
    """
    return [(term, corpus.get_rhymes(term)) for term in query.terms]


def main():

    # make default paths, since no specs...
    cwd = os.getcwd()
    corpus_path = os.path.join(cwd, 'long_poem.txt')
    query_path = os.path.join(cwd, 'query')

    # if run standalone, prompt for files
    if not os.path.exists(corpus_path):
        corpus_path = input('Default corpus file not found ("long_poem.txt"). '
                            'Enter full path to the corpus file: ')
    if not os.path.exists(query_path):
        query_path = input('Default query file not found ("query"). Enter full path to the query file: ')

    # process corpus file
    corpus = Corpus(corpus_path)
    corpus.build_index()
    corpus.build_rhyme_index()

    # timing starts
    start_time = time.clock()

    # read query
    query = Query(query_path)

    # perform search
    snippets = snippet_search(corpus, query)
    snippet_time = time.clock()

    rhymes = rhyme_search(corpus, query)
    finish_time = time.clock()

    # write results
    with open('snippets.txt', 'w') as f:
        f.write('\n'.join(snippets))

    with open('rhymes.txt', 'w') as f1:
        f1.write('\n'.join(['%s: %s' % (term, rhyme) for (term, rhyme) in rhymes]))

    # report time
    print('snippet search: ', snippet_time-start_time)
    print('rhyme search: ', finish_time-snippet_time)


# todo another speedup: search, remove duplicates, get context
# leave for now, depends on output requirements. probably not much win anyway

if __name__ == '__main__':
    main()
    # cProfile.run('main()')