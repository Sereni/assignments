__author__ = 'Sereni'

import lxml.etree as et
import csv
import re
import os
from collections import Counter


def count_links(string, expression):
    return len(expression.findall(string))


def count_tokens(string):
    return len(string.split())


def parse_dump(path):
    """
    @param path: path to uncompressed dump file
    """
    # set the defaults
    namespace = "{http://www.mediawiki.org/xml/export-0.10/}"
    line = []
    counter = Counter()
    output = open('info.csv', 'w')

    # compile regex
    link_exp = re.compile('\[\[\w+\]\]')

    with open(path, 'rb') as xml:

        # set up csv writer
        writer = csv.writer(output, delimiter=',')

        # iterparse the dump
        context = et.iterparse(xml)
        for event, element in context:

            # get article name
            if element.tag == namespace + "title":
                line.append(element.text)
            elif element.tag == namespace + "text":

                if element.text:  # apparently, there are empty elements

                    # count outgoing links
                    line.append(str(count_links(element.text, link_exp)))

                    # count tokens
                    line.append(str(count_tokens(element.text)))

                else:
                    line += [0, 0]

            element.clear()

            # write line to csv
            if len(line) == 3:  # sigh
                writer.writerow(line)
                line = []

    output.close()
    print(len(counter))
    with open('freq.txt', 'w') as freq:
        freq.write('\n'.join(['%s,%s' % (word, str(count)) for word, count in counter]))

path = input('Enter path to dump: ')

if os.path.exists(path):
    parse_dump(path)
else:
    raise FileExistsError("File does not exist: %s" % path)