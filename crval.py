#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Ryan Wolfslayer, Iowa State University"
# command line tool that runs with ../Scripts/validate.bat
# validate csv=True dir=True
from doiowa.validation import crossref_validate
import glob
import os
from sys import argv
import pandas as pd


def main(item, dir=False, *args):
    print('request sent...')
    csvname = 'qcrossrefErrors.csv'
    curdir = os.getcwd()
    if dir == 'True' or dir == True:
        os.chdir(curdir + '/' + item)
        result = [crossref_validate(x) for x in glob.glob('*.xml')]
        os.chdir(curdir)
        while True:
            try:
                pd.concat(result, sort=False).to_csv(csvname, index=False,
                                                     columns=['filename', 'line', 'type', 'description'])
                break

            except ValueError:
                print('No Files in Directory')
                break

            except PermissionError:
                print(input('   #PermissionsError, please close {}'.format(csvname)))
                print('             ...retrying...')

    else:
        try:
            result = crossref_validate(item)
            if result.empty:
                result = ''
            else:
                result.to_csv(csvname, index=False)
        except TypeError:
            result = ''

    print('done.')


if __name__ == "__main__":
    main(*argv[1:])
