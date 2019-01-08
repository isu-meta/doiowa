#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Ryan Wolfslayer, Iowa State University"

# Assigns variables to transformations, serves as intermediary for oaiowa variabls, and executes merge and crosswalk

import os

from doiowa.oaiowa import *
from doiowa.citationFinder import citefind

curr_dir = os.getcwd()


class Variable(object):
    '''
        Ensures user input is a correctly formatted OAI-PMH query before
        calling the various methods from oaiowa.

        PARAMETERS
        ----------
        domain: string
            The repository domain. For Iowa State this would be http://lib.dr.iastate.eduself.
            This is equivalent to OAIXML's domain parameter

        collection_abbreviation: string
            Pass in the abbreviation for the desired collection. Whatever is passed in
            will be reformatted with 'publication:{}' to conform with bepress's queries
    '''
    def __init__(self, domain, collection_abbreviation):
        if domain.endswith('/'):
            self.domain = domain
        else:
            self.domain = domain + '/'

        if collection_abbreviation.startswith('publication:'):
            set = self.ctype
        else:
            self.ctype = 'publication:{}'.format(collection_abbreviation)

    def xsltvariable(self, registrant, registrant_acronym, registrant_city, depositor, depositor_email, doi_prefix,
                     collection_type, journalabbrev, issn):
        '''
            Formats the variables in the primary xslt script, iacrossref-v12.xsl.
            For normal doiowa usage, these parameters are stored under
            'infiles/configuration.xml'.

            PARAMETERS
            -----------
            +--------------------+------------+----------------------------------------------------+
            | **Name**           | **Format** | **Description**                                    |
            +--------------------+------------+----------------------------------------------------+
            | registrant         | string     | Name of the registering institution or department  |
            +--------------------+------------+----------------------------------------------------+
            | registrant_acronym | string     | Acronym of the registering institution             |
            +--------------------+------------+----------------------------------------------------+




        '''

        root = etree.parse('transformations/iacrossref-v12.xsl')

        d = {'doctype': collection_type, 'acronym': self.ctype.replace('publication:',''), 'doi_prefix': doi_prefix,
             'registrant': registrant, 'registrant_acronym': registrant_acronym, 'location': registrant_city,
             'depositor': depositor, 'email': depositor_email, 'website': self.domain, 'journal_abbrev':journalabbrev, 'issn':issn}

        for key, value in d.items():
            root.find('//xsl:variable[@name="{}"]/xsl:text'.format(key),
                      namespaces={"xsl": "http://www.w3.org/1999/XSL/Transform"}).text = value

        root.write('transformations/iacrossref-v12.xsl', pretty_print=True, xml_declaration=True, encoding='utf-8')

    def oaiowa_variables(self, filter=False):
        oa = OAIXML(domain=self.domain, set=self.ctype, filter=filter)
        return oa.returnvar()

    def mergeandwalk(self, type_split=False, cwalk=True, kind=None):
        output_filename = 'bepress_do_{}.xml'.format(self.ctype).replace(':', '_')
        # merged files
        createdir(name='outfiles/merged_xml')
        merge(filename='outfiles/merged_xml/{}'.format(output_filename))

        if type_split == True:
            typesplit('{}/outfiles/merged_xml/{}'.format(curr_dir, output_filename),
                      '{}/outfiles/merged_xml/bepress_rtd.xml'.format(curr_dir), type='rtd')
            typesplit('{}/outfiles/merged_xml/{}'.format(curr_dir, output_filename),
                      '{}/outfiles/merged_xml/bepress_etd.xml'.format(curr_dir), type='etd')

            if cwalk == True:
                # rtd as doi prefix
                root = etree.parse('transformations/iacrossref-v12.xsl')
                root.find('//xsl:variable[@name="acronym"]/xsl:text',
                          namespaces={"xsl": "http://www.w3.org/1999/XSL/Transform"}).text = 'rtd'
                root.write('transformations/iacrossref-v12.xsl', pretty_print=True, xml_declaration=True,
                           encoding='utf-8')
                crosswalk('outfiles/merged_xml/bepress_rtd.xml', 'outfiles/merged_xml/crossref_rtd.xml')
                # etd as doi prefix
                root.find('//xsl:variable[@name="acronym"]/xsl:text',
                          namespaces={"xsl": "http://www.w3.org/1999/XSL/Transform"}).text = 'etd'
                root.write('transformations/iacrossref-v12.xsl', pretty_print=True, xml_declaration=True,
                           encoding='utf-8')

                crosswalk('outfiles/merged_xml/bepress_etd.xml', 'outfiles/merged_xml/crossref_etd.xml')
            else:
                pass
        else:
            if kind=='journal':
                citefind('outfiles/merged_xml/{}'.format(output_filename), outfile='transformations/citationsfound.xml', ns='bepress')
                crosswalk('outfiles/merged_xml/{}'.format(output_filename), 'outfiles/merged_xml/doi2.xml')
                remtag('outfiles/merged_xml/doi2.xml', 'outfiles/merged_xml/crossref_doi.xml')
            elif kind=='conference':
                crosswalk('outfiles/merged_xml/{}'.format(output_filename), 'outfiles/merged_xml/doi2.xml')
                conference_tags('outfiles/merged_xml/doi2.xml', 'outfiles/merged_xml/doi3.xml')
                remtag('outfiles/merged_xml/doi3.xml', 'outfiles/merged_xml/crossref_doi.xml')
            else:
                crosswalk('outfiles/merged_xml/{}'.format(output_filename), 'outfiles/merged_xml/crossref_doi.xml')
