#!/usr/bin/python
# -*- coding: utf-8 -*-
from doiowa.validation import Validation, crossref_validate
import os
import pandas as pd
import glob
from sys import argv


def main(batchfile, file, collection_type, counter, csvname, *args):
    val = Validation(bepress_revise=batchfile, infile=file,
                     top_elem=collection_type, sequence=counter)
    # val.report_duplicates(sequester=False)
    if int(counter) > 1:
        val.reduce_xml(cdir=False)
    else:
        val.reduce_xml(cdir=True)
    currentdir = os.getcwd()
    os.chdir(currentdir + '/outfiles/complete')
    result = [crossref_validate(x)
              for x in glob.glob('*.xml', recursive=False)]

    while True:
        try:
            pd.concat(result, sort=False).to_csv('crossrefErrors_{}.csv'.format(csvname), index=False,
                                                 columns=['filename', 'line', 'type', 'description'])
            break

        except ValueError:
            print('No Files in Directory')
            break

        except PermissionError:
            print(input(
                '   #PermissionsError, please close crossrefErrors_{}.csv to continue'.format(csvname)))
            print('             ...retrying...')


if __name__ == "__main__":
    import sys
    import threading

    # initial runs were resulting in stack overflow error
    sys.setrecursionlimit(100000)
    threading.stack_size(200000000)
    thread = threading.Thread(target=main, args=[*argv[1:]])
    thread.start()
