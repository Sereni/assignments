__author__ = 'Sereni'

import urllib.request as url
import lxml.etree as et
from io import StringIO
import bz2
import os


def fetch_urls():
    with url.urlopen('https://dumps.wikimedia.org/backup-index.html') as response:
        html = response.read().decode('utf-8')
    parser = et.HTMLParser()
    root = et.parse(StringIO(html), parser)
    urls = [node.text for node in root.findall(".//li/a")]

    return urls


def find_articles(path):
    """
    @param path: path to xml file
    @return: list of article titles
    """
    titles = []
    with open(path, 'rb') as xml:
        context = et.iterparse(xml, tag="{http://www.mediawiki.org/xml/export-0.10/}title")
        for event, element in context:
            titles.append(element.text)
    return titles


def decompress(path):
    """
    Iteratively decompress data from file and write to anoter file.
    """
    with open(path, 'rb') as archive, open(path + '.decompressed', 'wb') as new:
        decompressor = bz2.BZ2Decompressor()
        for line in archive:  # hope doesn't put it in memory
            new.write(decompressor.decompress(line))

    return path + '.decompressed'


def load_dump():
    code = input("Enter language code: ")
    dump_name = '%swiki' % code
    urls = fetch_urls()

    if dump_name in urls:
        link = 'https://dumps.wikimedia.org/%s/latest/%s-latest-pages-articles.xml.bz2' % (dump_name, dump_name)
        path = os.path.join(os.getcwd(), link.split('/')[-1])
        if not os.path.exists(path):
            size = int(url.urlopen(link).info()['Content-Length'])
            if size > 50*1024*1024:
                choice = query_yes_no("You are about to download a large file (%d bytes). Continue?" % size,
                                      default="no")
                if choice:
                    path, message = url.urlretrieve(link, link.split('/')[-1])
                else:
                    exit()
            else:
                path, message = url.urlretrieve(link, link.split('/')[-1])

    else:
        raise Exception("No wiki found for this code.")
    return path


def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        print(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            print("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")

archive_path = load_dump()
xml_path = decompress(os.path.join(os.getcwd(), archive_path))

with open('article_names.txt', 'w') as names:
    names.write('\n'.join(sorted(find_articles(xml_path))))