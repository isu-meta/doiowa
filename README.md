Doiowa
=======

BePress to CrossRef doi minting for Iowa State University.


Getting Started
----------------

Clone the repository and create an anaconda environment.

``` {.sourceCode .console}
$ git clone https://github.com/wryan14/doiowa.git
$ cd doiowa
$ conda create -n "doi_env" python=3.6.1
$ activate doi_env
$ pip install -r requirements.txt
```

### Step 1. 

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


### Step 2. 
Replace [fake_farmprogressreports_august.xls](infiles/fake_farmprogressreports_august.xls) with the target BePress batch revise file.

### Step 3 (optional). 
Add [validate.bat](batch/validate.bat]) to PATH. 

### Step 4. 
Run the code

``` {.sourceCode .console}
$ python harvester.py
```

### Step 5. 
Upload to CrossRef 

``` {.sourceCode .console}
$ python upload.py path/to/file.xml filename 
```

Supplemental Files
-------------------

### suppdata.xml

Currently doiowa supports journals, conferences, report-papers, and disserations. Conferences require [suppdata.xml](transformations/suppdata.xml) be stored in the transformations directory.  This file should include conference event metadata. 

### validate.bat 

If [validate.bat](batch/validate.bat) is in PATH, generate a validation report via CrossRef's API.

``` {.sourceCode .console}
$ validate target_file.xml
```


