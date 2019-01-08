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

### Step 1. Complete [configuration.xml](infiles/configuration.xml)

| Element              | Child Element           | Attribute | Description                                                                                | Required                           |
|----------------------|-------------------------|-----------|--------------------------------------------------------------------------------------------|------------------------------------|
| doi_run              |                         | sequence  | Doiowa can run multiple transformations, add the ordered number to the sequence attribute. | TRUE                               |
| institution          | registrant              |           | Name of registering institution                                                            | TRUE                               |
| institution          | registrant_acronym      |           | Acronym of registering institution                                                         | TRUE                               |
| institution          | registrant_city         |           | City of registering institution                                                            | TRUE                               |
| person               | depositor               |           | Name of person depositing metadata                                                         | TRUE                               |
| person               | depostior_email         |           | Email address of person depositing metadata                                                | TRUE                               |
| uri                  | repository_url          |           | Base url of repository. e.g. https://lib.dr.iastate.edu/                                   | TRUE                               |
| uri                  | doi_prefix              |           | CrossRef Assigned doi prefix. e.g. 10.31274                                                | TRUE                               |
| collection           | collection_type         |           | Supported Options: journal, dissertation, report-paper, conference                         | TRUE                               |
| collection           | collection_abbreviation |           | BePress Repository abbreviation                                                            | TRUE                               |
|                      |                         |           |                                                                                            |                                    |
|                      |                         |           | as searchable via oai-pmh e.g. farmprogressreports                                         |                                    |
| bepress_batch        |                         |           | batch_revise report from bepress.                                                          | TRUE                               |
|                      |                         |           |                                                                                            |                                    |
|                      |                         |           | e.g. infiles/farmprogressreports_august.xls                                                |                                    |
| filter               |                         |           | oai-pmh formatted date filter e.g.from=2018-11-11&until=2018-12-12                         | FALSE                              |
| journal_abbreviation |                         |           | Include if collection_type = journal                                                       | True for journals; Otherwise False |
| issn                 |                         |           | Include if collection_type = journal, otherwise issn                                       | True for journals; Otherwise False |
|                      |                         |           |                                                                                            |                                    |
|                      |                         |           | will be noissn.                                                                            |                                    |
| small                |                         |           | True if oai-pmh harvest < 100 records                                                      | TRUE                               |

### Step 2. Replace [fake_farmprogressreports_august.xls](infiles/fake_farmprogressreports_august.xls) with the target BePress batch revise file.

### Step 3 (optonal). Add [validate.bat](batch/validate.bat]) to PATH. 

### Step 4. Run the code

``` {.sourceCode .console}
$ python harvester.py
```

### Step 5. Upload to CrossRef 

``` {.sourceCode .console}
$ python upload.py path/to/xml.xml filename 
```
