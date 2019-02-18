#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, Extension, find_packages
import numpy
import os
import sys
from subprocess import check_output

if sys.argv[-1] != 'test':
    #Grab and write the gitVersion from 'git describe'.
    gitVersion = ''
    gitPath = ''

    # get git describe if in git repository
    print('Fetching most recent git tags')
    if os.path.exists('./.git'):
        try:
            # if we are in a git repo, fetch most recent tags
            check_output(["git fetch --tags"], shell=True)
        except Exception as e:
            print('Unable to fetch most recent tags')

        try:
            ls_proc = check_output(["git describe --tags"], shell=True, universal_newlines=True)
            gitVersion = ls_proc
            print('Checking most recent version')
        except Exception as e:
            print('Unable to get git tag and hash')
    # if not in git repo
    else:
        print('Not in git repository')
        gitVersion = ''

    # get current working directory to define git path
    gitPath = os.getcwd()

    # git untracked file to store version and path
    fname = os.path.abspath(os.path.expanduser('./katana/gitinfo.py'))

    with open(fname,'w') as f:
        nchars = len(gitVersion) - 1
        f.write("__gitPath__='{0}'\n".format(gitPath))
        f.write("__gitVersion__='{0}'\n".format(gitVersion[:nchars]))
        f.close()

setup(
    author="Micah Sandusky",
    author_email='micah.sandusky@ars.usda.gov',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: CCO 1.0',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    description="Downscaling of atmospheric wind simulations using WindNinja for water resource modeling",
    license="CCO 1.0",
    # long_description=readme + '\n\n' + history,
    include_package_data=True,
    package_data={'katana':['./CoreConfig.ini',
				  './recipes.ini']},
    keywords='katana',
    name='katana',
    packages=['katana'],
    test_suite='tests',
    # tests_require=test_requirements,
    url='https://github.com/usdaarsnwrc/katana',
    version='0.3.1',
    zip_safe=False,
    scripts=['scripts/run_katana'],
)
