# Doiowa

A library to manage the registration and maintenance of DOIs at the Iowa
State University Library.

**Please note:** This library is currently undergoing a significant rewrite
and reorganization with the goal of making it more flexible, maintainable,
and portable. During this process this README file and the documentation
it links to may fall out of sync with actual usage. Efforts will be made to
keep this document as current as possible.

## Requirements

Requires [Python](https://www.python.org/) version 3.7 or higher.

### Python libraries

- [crossrefapi](https://github.com/fabiobatalha/crossrefapi)
- [lxml](https://lxml.de/)
- [pandas](http://pandas.pydata.org/)
- [requests](https://2.python-requests.org/en/master/)
- [tika](https://github.com/chrismattmann/tika-python)

### Non-Python Requirements

**Note:** The following non-Python requirements are only needed if you're
working with bepress Digital Commons collections.

- [Java 7+](https://www.java.com/en/) (Required by tika)
- [SaxonHE 9.8+ for the .NET platform](https://www.saxonica.com/download/dotnet.xml)

## Getting Started

Clone the repository and create a virtual environment.

```console
C:\your\dir> git clone https://github.com/wryan14/doiowa.git
C:\your\dir\doiowa> cd doiowa
C:\your\dir\doiowa> python -m venv "doi_env"
C:\your\dir\doiowa> doi_env\Scripts\activate
C:\your\dir\doiowa> pip install -r requirements.txt
```

## Basic Usage

To harvest metadata from a source and generate an XML file to submit
to the Crossref API, use the `harvest` command followed by the target
collection:

```console
C:\your\dir\doiowa> python doiowa.py harvest cpn
```

Current supported collection names are `cpn`. **Do not run** `harvest`
against a collection that has already been harvested as this script does
not currently check to see if a DOI has been previously generated for an
object. Such functionality will be implemented in the future.

To register one or more DOIs, use the `register` command followed by the
XML file containing the DOIs and associated metadata, your Crossref username
and password:

```console
C:\your\dir\doiowa> python doiowa.py register new_dois.xml username password
```

To check on the status of a submission, use the `check` command followed
by either the XML file submitted or the DOI batch ID of the submission and
your Crossref username and password:

```console
C:\your\dir\doiowa> python doiowa.py check new_dois.xml username password
```

or:

```console
C:\your\dir\doiowa> python doiowa.py check new-dois-0001 username password
```

## Set and Workflow for Creating DOIs for Digital Commons Collections

### Step 1

Complete [configuration.xml](infiles/configuration.xml)

| Element | Child Element | Attribute | Description | Required |
|----------------------|-------------------------|-----------|------------------------------------------------------------------------|------------------------------------|
| doi_run |  | sequence | numbered order for multiple transformations | TRUE |
| institution | registrant |  | name of registering institution | TRUE |
| institution | registrant_acronym |  | acronym of registering institution | TRUE |
| institution | registrant_city |  | city of registering institution | TRUE |
| person | depositor |  | name of person depositing metadata | TRUE |
| person | depositor_email |  | email address of person depositing metadata | TRUE |
| uri | repository_url |  | base url of repository. e.g. https://lib.dr.iastate.edu/ | TRUE |
| uri | doi_prefix |  | doi prefix. e.g. 10.31274 | TRUE |
| collection | collection_type |  | choose journal, dissertation, report-paper, or conference | TRUE |
| collection | collection_abbreviation |  | bepress collection abbreviation as found via oai-pmh | TRUE |
| bepress_batch |  |  | batch_revise xls report from bepress | TRUE |
| filter |  |  | oai-pmh formatted date filter e.g.from=2018-11-11&amp;until=2018-12-12 | FALSE |
| journal_abbreviation |  |  | title abbreviation for journals | True for journals; Otherwise False |
| issn |  |  | issn for journals | True for journals; Otherwise False |
| small |  |  | make True if oai-pmh harvest < 100 records | TRUE |

### Step 2

Replace [fake_farmprogressreports_august.xls](infiles/fake_farmprogressreports_august.xls)
with the target bepress_batch XSL.

### Step 3

Run the code

```console
C:\your\dir\doiowa> python harvester.py
```

### Step 4

Upload to CrossRef

```console
C:\your\dir\doiowa> python doiowa.py register path\to\file.xml username password
```

## Supplemental Files

### suppdata.xml

Currently doiowa supports journals, conferences, report-papers, and dissertations.
Conferences require [suppdata.xml](transformations/suppdata.xml) be stored in the
transformations directory.  This file should include conference event metadata.

## Documentation

Documentation of the doiowa library, its modules, objects, and functions is
available as HTML in the doc directory. [Explore the documentation online](http://htmlpreview.github.io/?https://github.com/isu-meta/doiowa/blob/master/doc/doiowa/index.html).

**Please note:** The following documentation is largely out of date and not
maintained by the the Iowa State University Library. However, it may have
further details relevant to generating DOIs for bepress Digital Commons
collections. [Doiowa legacy documentation](https://mddocs.readthedocs.io/en/latest/doiowa.html)
