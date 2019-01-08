#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Ryan Wolfslayer, Iowa State University"

import os
import re
from sys import argv

import pandas as pd
import requests
from crossref.restful import Works
from lxml import etree as et
from lxml.etree import parse
from tika import parser


# functions
def getyear(x):
    try:
        return x['date-parts'][0][0]
    except Exception:
        return ''


def gettitle(x):
    try:
        return x[0]
    except Exception:
        return ''


def getsurname(x):
    try:
        return x[0]['family']
    except Exception:
        return ''


def firstpage(x):
    try:
        return re.search(r'\d{1,4}(?=\-|[ ]|$)', x).group()

    except Exception:
        return ''


def issuefunc(x):
    try:
        return x['issue']

    except Exception:
        return ''

def citefind(file=None, outfile='citationsfound.xml', ns='crossref'):
    root = parse(file)
    if ns == 'crossref':
        urls = root.xpath('//foo:resource/text()', namespaces={"foo": "http://www.crossref.org/schema/4.3.7"})
    elif ns == 'bepress':
        urls = root.xpath('//fulltext-url/text()')
    else:
        return 'Currently only support bepress schema or crossref'

    count = 0
    allcitations = et.Element('root')
    for url in urls:
        count += 1
        r = requests.get(url, stream=True)
        with open('metadata.pdf', 'wb') as f:
            f.write(r.content)
            f.close()

        raw = parser.from_file('metadata.pdf')
        f = raw['content'].encode()
        zfind = re.findall(r'(?i)doi:.+?(?= |$)', str(f))
        print(len(zfind), url)
        if len(zfind) > 0:
            dois = [y.replace('\\n', '').replace(' ', '').replace('doi:', '').strip('.') for y in zfind]
            dfli = []
            works = Works()
            for item in dois:
                d = works.doi(item)
                df = pd.Series(d).to_frame()
                dfli.append(df.transpose())

            cr = pd.concat(dfli)
            cr = cr.reset_index(drop=True)
            cr['year'] = cr.created.apply(lambda x: getyear(x))
            cr['journaltitle'] = cr['container-title'].apply(lambda x: gettitle(x))
            cr['surname'] = cr['author'].apply(lambda x: getsurname(x))
            try:
                cr['fpage'] = cr['page'].apply(lambda x: firstpage(x))
            except KeyError:
                cr['fpage'] = ''
            cr['issues'] = cr['journal-issue'].apply(lambda x: issuefunc(x))

            xml = cr[['DOI', 'ISSN', 'journaltitle', 'surname', 'volume', 'issues', 'fpage', 'year']]
            tree = et.SubElement(allcitations, 'citationlist')
            tree.set('file', url)
            for row in xml.iterrows():
                citation = et.SubElement(tree, 'citation')
                citation.set('key', 'key-{}'.format(str(row[1]['DOI'])))

                issn = et.SubElement(citation, 'issn')
                try:
                    issn.text = str(row[1]['ISSN'][0])
                    try:
                        issn = et.SubElement(citation, 'issn')
                        issn.text = str(row[1]['ISSN'][1])
                    except IndexError:
                        pass
                except TypeError:
                    pass

                journal_titlex = et.SubElement(citation, 'journal_title')
                journal_titlex.text = str(row[1]['journaltitle'])

                authorx = et.SubElement(citation, 'author')
                authorx.text = str(row[1]['surname'])

                volumex = et.SubElement(citation, 'volume')
                volumex.text = str(row[1]['volume'])

                issuex = et.SubElement(citation, 'issue')
                issuex.text = str(row[1]['issues'])

                first_pagex = et.SubElement(citation, 'first_page')
                first_pagex.text = str(row[1]['fpage'])

                cYearx = et.SubElement(citation, 'cYear', )
                cYearx.text = str(row[1]['year'])


        else:
            continue

        with open(outfile, 'wb') as fi:
            fi.write(et.tostring(allcitations, pretty_print=True, xml_declaration=True))
            fi.close()

