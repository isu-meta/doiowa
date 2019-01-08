#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
__author__ = 'Ryan Wolfslayer, Iowa State University'

# Program to assist with collecting variables for harvesting OAI
# produces first 100 results and returns tokens for remaining results
# includes additional functions and xslt scripts used throughout the DOIowa project
    
import glob
import math
import os
import shutil
import subprocess
from urllib.request import urlopen

from lxml import etree

parser = etree.XMLParser(remove_blank_text=True)


class OAIXML(object):
    """
        Initiaties OAI-PMH Harvesting.  
        
        PARAMETERS
        ----------
        domain: string 
            The respository domain. For Iowa State that would be http://lib.dr.iastate.edu/
        
        verb: string 
            Add the desired OAI-PMH verb. 
        
        prefix: string 
            Add the desired OAI-PMH prefix; like dc or document-export 
        
        set: string 
            Add the desired collection name like publication:ans_air
        
        filter: string 
            Add the OAI-PMH argument for start and end dates 
        
        fullquery: string 
            Use if you want to submit a query directly.
        
        
    """
    def __init__(self, domain=None, verb='ListRecords', prefix='document-export', set=None, filter=False,
                 fullquery=None):
        self.domain = domain
        self.verb = verb
        self.prefix = prefix
        self.filter = filter
        self.set = set

        if domain.startswith('http'):
            self.domain = domain
        else:
            self.domain = 'https://{}'.format(domain)
        if self.domain.endswith('/'):
            pass
        else:
            self.domain = domain + '/'

        # initial query
        if fullquery:
            self.query = fullquery
        elif filter == False:
            self.query = '{}do/oai/?verb={}&metadataPrefix={}&set={}'.format(self.domain, self.verb,
                                                                             self.prefix, self.set)
        else:
            self.query = '{}do/oai/?verb={}&metadataPrefix={}&set={}&{}'.format(self.domain, self.verb,
                                                                                self.prefix, self.set,
                                                                                self.filter)
        print(self.query)
        self.initdoc = etree.parse(urlopen(self.query), parser)
        try:
            self.count = int(math.ceil(int(self.initdoc.xpath('//@completeListSize')[0]) / 100))
            self.token = \
            self.initdoc.xpath('//foo:resumptionToken/text()', namespaces={"foo": "http://www.openarchives.org/OAI/2.0/"})[
                0]
        except IndexError:
            self.count=0
            self.token=None

        if self.count > 1:
            tokenstring = '/{}/'.join(self.token.split('/100/'))

            self.oai_urls = list(tokenstring.format(n * 100) for n in range(1, self.count))
        else:
            self.oai_urls = None

        try:
            dire = str(self.set)
        except Exception:
            dire = str('default')

        createdir('outfiles/directharvest')
        initfile = 'outfiles/directharvest/01_initialFile.xml'
        self.initdoc.write(initfile, pretty_print=True, xml_declaration=True, encoding='utf-8')

    
    def returnvar(self):
        return [self.domain, self.verb, self.oai_urls]


# assorted functions, requires java be in PATH

def createdir(name):
    from time import gmtime, strftime
    # create directory
    direc = os.getcwd() + '/' + name.replace(':', '_')
    current_time = str(strftime("%Y-%m-%d %H:%M:%S", gmtime())).replace(':', '_').replace(' ', '_')
    try:
        os.mkdir(direc)
    except Exception:
        os.mkdir(direc + '/' + str(current_time))
        [shutil.move(file, direc + '/' + str(current_time)) for file in glob.glob(direc + '/' + '*.xml')]
        [shutil.move(file, direc + '/' + str(current_time)) for file in glob.glob(direc + '/' + '*.csv')]    


def crosswalk(infile, outfile):
    current_path = os.getcwd()
    subprocess.call(["java", "-jar", "{}/transformations/saxon9.jar".format(current_path),
                     "-o:{}/{}".format(current_path, outfile),
                     "-s:{}/{}".format(current_path, infile),
                     "{}/transformations/iacrossref-v12.xsl".format(current_path)
                     ], shell=True)

def remtag(infile, outfile):
    current_path = os.getcwd()
    subprocess.call(["java", "-jar", "{}/transformations/saxon9.jar".format(current_path),
                     "-o:{}/{}".format(current_path, outfile),
                     "-s:{}/{}".format(current_path, infile),
                     "{}/transformations/removetag.xsl".format(current_path)
                     ], shell=True)

def conference_tags(infile, outfile):
    current_path = os.getcwd()
    subprocess.call(["java", "-jar", "{}/transformations/saxon9.jar".format(current_path),
                     "-o:{}/{}".format(current_path, outfile),
                     "-s:{}/{}".format(current_path, infile),
                     "{}/transformations/c_tags.xsl".format(current_path)
                     ], shell=True)
             
def merge(root=True, filename='default.xml'):
    current_path = os.getcwd()
    subprocess.call(["java", "-jar", "{}/transformations/saxon9.jar".format(current_path),
                     "-o:{}".format(filename),
                     "-s:{}/outfiles/directharvest/01_initialFile.xml".format(current_path),
                     "{}/transformations/merge.xsl".format(current_path)
                     ], shell=True)
    if root == True:
        roottag(filename)
    else:
        pass


def nodups(filename):
    current_path = os.getcwd()
    subprocess.call(["java", "-jar", "{}/transformations/saxon9.jar".format(current_path),
                     "-o:{}".format(filename.replace('.xml', '_dedup.xml')),
                     "-s:{}".format(filename),
                     "{}/transformations/merge.xsl".format(current_path)
                     ], shell=True)


def roottag(file):
    tree = etree.parse(file)
    root = tree.getroot()
    # BePress uses a 'documents' root, so it makes sense to write this into the code.
    # If you need to change the rootname do so here.
    newroot = etree.Element('documents')
    newroot.insert(0, root)
    tree = (etree.ElementTree(tree.getroot()))
    tree.write(file, xml_declaration=True, encoding='utf-8', method='xml')


def typesplit(infile, outfile, type=None):
    current_path = os.getcwd()

    if type == "rtd":
        subprocess.call(["java", "-jar", "{}/transformations/saxon9.jar".format(current_path),
                         "-o:{}".format(outfile),
                         "-s:{}".format(infile), "{}/transformations/rtd_split.xsl".format(current_path)
                         ], shell=True)
    elif type == "etd":
        subprocess.call(["java", "-jar", "{}/transformations/saxon9.jar".format(current_path),
                         "-o:{}".format(outfile),
                         "-s:{}".format(infile), "{}/transformations/etds_split.xsl".format(current_path)
                         ], shell=True)

    else:
        print("No transformation occurred, please enter type=etd or type=rtd")


# in code xlst 1.0 scripts
    
def xslt4(elems):
    '''Converts select crossref xml elements to an html table'''
    if elems == 'conference':
        elems = 'conference_paper'
    elif elems == 'journal':
        elems = 'journal_article'
    elif elems == 'report-paper':
        elems = 'report-paper/crossref:report-paper_metadata'
    else:
        pass
    xslt_root = etree.XML('''\
    <xsl:stylesheet version="1.0"
        xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
        xmlns:crossref="http://www.crossref.org/schema/4.3.7"
        exclude-result-prefixes="crossref">
        <xsl:output method="html"/>
        <xsl:template match="/">
            <table>
                <tr>
                    <th class="column">title</th>
                    <th class="column">author</th>
                    <th class="column">context_key</th>
                    <th class="column">doi</th>
                </tr>
                <xsl:apply-templates
                    select="//crossref:{}" />
            </table>
        </xsl:template>
        <xsl:template match="crossref:{}">
            <tr>
                <td>
                    <xsl:value-of select="./crossref:titles/crossref:title" />
                </td>
                <td>
                    <xsl:value-of
                        select="(./crossref:person_name/crossref:surname)[1]" />
                </td>
                <td>
                    <xsl:value-of
                        select="./crossref:publisher_item/crossref:item_number" />
                </td>
                <td>
                    <xsl:value-of select="concat('https://doi.org/',./crossref:doi_data/crossref:doi)" />
                </td>
            </tr>
        </xsl:template>
    </xsl:stylesheet>'''.format(elems, elems))

    return xslt_root


# xslt to remove crossref elements with a certain context_key
def xslt5(elem, keyvalues):
    '''removes a desired element that contains a certain context_key'''
    xslt_root = etree.XML('''\
    <xsl:stylesheet version="1.0"
        xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
        xmlns:crossref="http://www.crossref.org/schema/4.3.7">
        <xsl:template match="/ | node() | @*">
            <xsl:copy>
                <xsl:apply-templates select="node() | @*" />
            </xsl:copy>
        </xsl:template>
        <xsl:template
            match="crossref:{}[{}]" />
        <xsl:template match="text()" priority="2">
            <xsl:value-of select="normalize-space(.)" />
        </xsl:template>
    </xsl:stylesheet>
    '''.format(elem, keyvalues))

    return xslt_root
    

def xslt6(elem, split_type=None):
    '''
        If the resulting XML file becomes too large for crossref, 
        this xslt script will split one file into two.
    '''
    if split_type == 'odd':
        x = '!='
    else:
        x = '='
    xslt_root = etree.XML('''\
        <xsl:stylesheet version="1.0"
        xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
        xmlns:crossref="http://www.crossref.org/schema/4.3.7">
    
    
        <xsl:output method="xml" encoding="utf-8" indent="yes" />
    
        <!-- Identity template : copy all text nodes, elements and attributes -->
        <xsl:template match="@*|node()">
            <xsl:copy>
                <xsl:apply-templates select="@*|node()" />
            </xsl:copy>
        </xsl:template>
        <xsl:template match="crossref:body">
        <crossref:body>
            <xsl:for-each select="crossref:{}/crossref:titles">
                <xsl:choose>
                    <xsl:when
                        test="position() mod 2{}0">
                        <xsl:copy-of select="parent::node()" />
                    </xsl:when>
                    <xsl:otherwise />
                </xsl:choose>
            </xsl:for-each>
        </crossref:body>
        </xsl:template>
        <xsl:template match="text()" priority="2">
            <xsl:value-of select="normalize-space(.)" />
        </xsl:template>
        </xsl:stylesheet>'''.format(elem, x))
    return xslt_root

        