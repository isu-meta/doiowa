#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Ryan Wolfslayer, Iowa State University"

import asyncio
from concurrent.futures import ThreadPoolExecutor
from urllib.request import urlopen

from lxml import etree

parser = etree.XMLParser(remove_blank_text=True)


@asyncio.coroutine
def harvest(domain, verb, oai=None, idx=None, *args):
    url = '{}?verb={}&resumptionToken={}'.format(domain, verb, oai)
    response = yield from loop.run_in_executor(executor, urlopen, url)
    document = etree.parse(response, parser)
    print('  {}'.format(url))
    uni = str(domain).replace(".", "").replace("/", "").replace("http", "").replace(":", "").replace("-", "")
    filename = '{}{}_{}'.format(uni, str(verb), oai.split('/')[2])

    try:
        xml_outfile = 'outfiles/directharvest/{}.xml'.format(filename)
        document.write(xml_outfile, pretty_print=True, xml_declaration=True, encoding='utf-8')

    except Exception:
        try:
            xml_outfile = 'outfiles/directharvest/{}.xml'.format(filename)
            document.write(xml_outfile, pretty_print=True, xml_declaration=True, encoding='utf-8')

        except Exception as e:
            print("Error at position {}, records may have been skipped".format(str(int(oai / 100))))
            print("{}; Impacted Records: {}".format(e, url))


if __name__ == "__main__":
    import asyncio
    from concurrent.futures import ThreadPoolExecutor
    import glob
    import os
    import time
    import pandas as pd
    from lxml.etree import parse
    from doiowa.control import Variable
    from doiowa.validation import Validation, crossref_validate
    import subprocess

    print(os.getcwd())

    # initial runs were resulting in stack overflow error
    # REGISTRANT -- institution
    # Variables can be filled out in place of form.xml
    root = parse('infiles/configuration.xml')
    total = int(root.xpath('count(//doi_run)'))
    count = 0
    t1 = time.time()
    for c in (range(total)):
        count += 1
        registrant = root.xpath('doi_run[@sequence={}]/institution/registrant/text()'.format(count))[0]
        registrant_acronym = root.xpath('doi_run[@sequence={}]/institution/registrant_acronym/text()'.format(count))[0]
        registrant_city = root.xpath('doi_run[@sequence={}]/institution/registrant_city/text()'.format(count))[0]

        # DEPOSITOR -- person
        depositor = root.xpath('doi_run[@sequence={}]/person/depositor/text()'.format(count))[0]
        depositor_email = root.xpath('doi_run[@sequence={}]/person/depositor_email/text()'.format(count))[0]

        # URI
        domain = root.xpath('doi_run[@sequence={}]/uri/repository_url/text()'.format(count))[0]
        doi_prefix = root.xpath('doi_run[@sequence={}]/uri/doi_prefix/text()'.format(count))[0]

        # COLLECTION -- dissertation, conference, report-paper, journal
        # Collection abbreviations can be found through http://[repository_url]/do/oai/?verb=ListSets
        collection_type = root.xpath('doi_run[@sequence={}]/collection/collection_type/text()'.format(count))[0]
        collection_abbreviation = \
            root.xpath('doi_run[@sequence={}]/collection/collection_abbreviation/text()'.format(count))[0]

        try:
            filter1 = root.xpath('doi_run[@sequence={}]/filter/text()'.format(count))[0]
        except Exception:
            filter1 = None
        
        try:
            journal_abbrev = root.xpath('doi_run[@sequence={}]/journal_abbreviation/text()'.format(count))[0]
        except Exception:
            journal_abbrev = None
        
        try:
            issn = root.xpath('doi_run[@sequence={}]/issn/text()'.format(count))[0]
        except Exception:
            issn = None
        
        try:
            lt100 = root.xpath('doi_run[@sequence={}]/small/text()'.format(count))[0]
        except Exception:
            lt100 = False

        # -------------------------------------------------------------------------------------------------------------

        print('starting {}/{} ...'.format(count, total))
        doi = Variable(domain=domain, collection_abbreviation=collection_abbreviation)
        doi.xsltvariable(registrant=registrant, registrant_acronym=registrant_acronym, registrant_city=registrant_city,
                         depositor=depositor, depositor_email=depositor_email, doi_prefix=doi_prefix,
                         collection_type=collection_type, journalabbrev=journal_abbrev, issn=issn)

        # run and return oaiowa
        oaurl = doi.oaiowa_variables(filter=filter1)
        
        if lt100 == False:
            # asynchronous harvesting
            executor = ThreadPoolExecutor(10)
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            tasks = [asyncio.async(harvest(domain=oaurl[0] + 'do/oai/', verb=oaurl[1], oai=z, idx=i)) for i, z in
                     enumerate(oaurl[2])]

            loop.run_until_complete(asyncio.wait(tasks))
            loop.close()
        else:
            pass

        # for type_split
        if collection_type == 'dissertation':
            doi.mergeandwalk(type_split=True, cwalk=True, kind=collection_type)
        else:
            doi.mergeandwalk(type_split=False, cwalk=False, kind=collection_type)

        # validation
        counter = 0
        for file in glob.glob('outfiles/merged_xml/crossref*.xml'):
            csvname = os.path.basename(file.replace('.xml', ''))
            counter += 1
            batchfile = root.xpath('doi_run[@sequence={}]/bepress_batch/text()'.format(count))[0]
            subprocess.call(['runvalfunc', '{}'.format(batchfile), '{}'.format(file), '{}'.format(collection_type),
                             '{}'.format(counter), '{}'.format(csvname)], shell=True)

        print('complete {}/{} ...'.format(count, total))
        print('harvest runtime:', time.time() - t1)
            
