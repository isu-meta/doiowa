# Doiowa

A library to manage the registration and maintenance of DOIs at the Iowa
State University Library.

## Requirements

Requires [Python](https://www.python.org/) version 3.7 or higher.

### Python libraries

- [crossrefapi](https://github.com/fabiobatalha/crossrefapi)
- [lxml](https://lxml.de/)
- [requests](https://2.python-requests.org/en/master/)

## Getting Started

To get started, download doiowa, create a virtual environment for it, and
install external requirements.

### Downloading/Cloning this Repository

[Download](https://github.com/isu-meta/doiowa/archive/master.zip) or clone
the repository and create a virtual environment.

If you [download doiowa](https://github.com/isu-meta/doiowa/archive/master.zip),
extract the zip file and go to the doiowa directory via the Command Prompt.

To clone the repository using git, run the following commands in the Command
Prompt.

```console
C:\your\dir> git clone https://github.com/isu-meta/doiowa.git
C:\your\dir\> cd doiowa
```

### Creating a Virtual Environment and Installing requirements

To finish setting up doiowa, run the following commands in the Command Prompt.

```console
C:\your\dir\doiowa> python -m venv "doi_env"
C:\your\dir\doiowa> doi_env\Scripts\activate
C:\your\dir\doiowa> pip install -r requirements.txt
```

## Basic Usage

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

## Documentation

Documentation of the doiowa library, its modules, objects, and functions is
available as HTML in the doc directory. [Explore the documentation online](http://htmlpreview.github.io/?https://github.com/isu-meta/doiowa/blob/master/doc/doiowa/index.html).
