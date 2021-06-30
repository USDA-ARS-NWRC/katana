#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

setup(
    author="USDA ARS NWRC",
    author_email='snow@ars.usda.gov',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: CCO 1.0',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    description="Downscaling of atmospheric wind simulations using WindNinja \
        for water resource modeling",
    license="CCO 1.0",
    include_package_data=True,
    package_data={'katana': ['./CoreConfig.ini',
                             './recipes.ini']},
    keywords='katana',
    name='katana',
    packages=find_packages(include=['katana', 'katana.*']),
    test_suite='tests',
    url='https://github.com/usdaarsnwrc/katana',
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'run_katana=katana.framework:cli',
        ]
    },
    use_scm_version={
        "local_scheme": "node-and-date"
    },
    setup_requires=['setuptools_scm'],
)
