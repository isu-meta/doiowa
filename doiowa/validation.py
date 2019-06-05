#!/usr/bin/python
# -*- coding: utf-8 -*-
    
import os
import time

from lxml import etree, html
from lxml.etree import parse
import pandas as pd
import requests

from doiowa.oaiowa import createdir, convert_elems_to_html_table, remove_elem_by_keys, split_large_xml_file

class Validation():
    # class requires bepress batch_revise spreadsheet
    def __init__(self, bepress_revise, infile, top_elem, sequence):
        self.bepress = bepress_revise
        self.root = parse(os.getcwd() + '/' + infile)
        self.df = pd.read_excel(bepress_revise).reset_index(drop=True)
        self.sequence = sequence
        self.element = top_elem

    def report_duplicates(self, sequester=True, report=True, outputmethod='csv', cdir=True):
        duplicate_report = []
        dups = self.df[self.df[['title', 'author1_lname']].duplicated(keep=False) == True].sort_values('title').rename(
            columns={'author1_lname': 'author'})
        dups['location'] = 'BePress Batch'
        duplicate_report.append(dups)

        # crossref uses elements like <crossref:dissertation>, elem will most often be the collection type
        transform = etree.XSLT(convert_elems_to_html_table(elems=self.element))
        ht = pd.read_html(str(transform(self.root)), header=0)[0]
        dups_ht = ht[ht[['title', 'author']].duplicated(keep='first') == True].reset_index().sort_values('title')
        dups_ht['location'] = 'CrossRef XML'
        duplicate_report.append(dups_ht)
        result = pd.DataFrame()

        if cdir == True:
            createdir('outfiles/reports')
        else:
            pass

        if report == True:
            pd.concat(duplicate_report, sort=False).to_csv('outfiles/reports/duplicateReport.csv', index=False,
                                                           columns=['author', 'title', 'context_key', 'location',
                                                                    'doi'], mode='w')

            # including doi data with BePress data
            result = pd.merge(self.df, ht[['doi', 'context_key']], on='context_key').sort_values('title',
                                                                                                 ascending=False)
            # items found in BePress Excel but were not harvested during OAI_PMH
            self.df[(~self.df.title.isin(result.title))].to_csv('outfiles/reports/noharvestReport.csv')
        else:
            pass

        if sequester == True:
            # removes the first instance of a duplicate, and may not catch items duplicated more than once
            kvalues = ' or '.join(["crossref:publisher_item/crossref:item_number/text() = '{}'".format(x) for x in
                                   dups_ht['context_key'].values.tolist()])
            transform_dup = etree.XSLT(remove_elem_by_keys(elem=self.element, keyvalues=kvalues))
            self.root = transform_dup(self.root)
            ht = ht[~ht['context_key'].isin(dups_ht['context_key'].values.tolist())]

        else:
            pass

        corder = list(self.df.columns.values)
        corder = corder.append('doi')

        if outputmethod == 'csv':
            result.to_csv('outfiles/reports/doiIncluded.csv', index=False, columns=corder)

        else:
            pass

    def reduce_xml(self, batchsize=5000, cdir=True):
        transform_even = etree.XSLT(split_large_xml_file(split_type='even', elem=self.element))
        transform_odd = etree.XSLT(split_large_xml_file(split_type='odd', elem=self.element))
        roots = [self.root]

        while int(roots[-1:][0].xpath('count(//foo:{})'.format(self.element),
                                      namespaces={"foo": "http://www.crossref.org/schema/4.3.7"})) > batchsize:
            reduce = [(transform_odd(x), transform_even(x)) for x in roots]
            roots = [x for y in reduce for x in y]

        # create directory
        if cdir == True:
            createdir('outfiles/complete')
        else:
            pass

        for count, x in enumerate(roots):
            # (x.xpath('count(//foo:{})'.format(self.element), namespaces={"foo": "http://www.crossref.org/schema/4.3.7"}))
            x.write('outfiles/complete/crossref_{}_{}_{}.xml'.format(self.element, self.sequence, str(count + 1)),
                    xml_declaration=True,
                    pretty_print=True,
                    encoding='utf-8',
                    method='xml')


def crossref_validate(filename):
    # this function sends xml as a post request to crossref for validation, errors will be presented in validationReport.csv
    # change into directory
    with open(filename, 'rb') as f:
        r = requests.post('https://apps.crossref.org/XSDParse/', files={filename: f})
        time.sleep(3)

        err_df = pd.DataFrame([x.strip()[1:].replace('\n', '').split(':', 3) for x in
                               ' '.join(html.fromstring(r.text).xpath(
                                   '//div[@id="mainContent2"]/div/table/tr/td/text()')).split('[Error]')[
                               1:]], columns=['line', 'column', 'type', 'description'])
        err_df['description'] = err_df.description.apply(lambda z: z.split('Parsing is complete')[0])
        err_df['filename'] = filename.replace('.xml', '')

        if len(err_df) == 0:
            print(' {} - Valid'.format(filename))


        else:
            print(' {} - see crossrefErrors.csv'.format(filename))
            return err_df
