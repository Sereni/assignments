__author__ = 'Sereni'
import os
import sqlite3
import lxml.etree as et
from collections import Counter


def update_freq(text, db):
    counter = Counter([word.strip('.,?!:;-)("\'][\\|{}').lower() for word in text.split()])
    for word, count in counter.items():

        if '|' in word or ':' in word or '<' in word or '>' in word or '#' in word or not word:
            continue

        # get current count
        queryset = db.execute('SELECT * FROM freq WHERE token=?', (word,))
        result = queryset.fetchone()
        if result:
            token, frequency = result

            # update count
            db.execute('UPDATE freq SET frequency=? WHERE token=?', (frequency+count, token))

        else:
            db.execute('INSERT INTO freq VALUES (?,?)', (word, count))
        # todo bulk update?

    db.commit()


def parse_dump(path, db):
    """
    @param path: path to uncompressed dump file
    """
    # set the defaults
    namespace = "{http://www.mediawiki.org/xml/export-0.10/}"

    with open(path, 'rb') as xml:

        # iterparse the dump
        context = et.iterparse(xml)
        for event, element in context:

            if element.tag == namespace + "text":

                if element.text:
                    update_freq(element.text, db)

            element.clear()

# create database
if not os.path.exists(os.path.join(os.getcwd(), 'freq.db')):

    # create file
    open(os.path.join(os.getcwd(), 'freq.db'), 'a').close()

    # create connection
    conn = sqlite3.connect('freq.db')

    # create table
    conn.cursor().execute('CREATE TABLE freq (token, frequency)')

else:
    conn = sqlite3.connect('freq.db')


path = input('Enter path to dump: ')

if os.path.exists(path):
    parse_dump(path, conn)
else:
    raise FileExistsError("File does not exist: %s" % path)