#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2018 Hon Fah Chong <hfchong@data.gov.sg>
# License: Apache 2.0
"""
Setup script for k-shortest-path
You can install k-shortest-path with
pipenv install
pip install .
"""
from setuptools import setup, find_packages

setup(name='kspath',
      version='0.1.0',
      description='Implements algorithms for the K shortest path problem.',
      author='Chong Hon Fah',
      author_email='hfchong@data.gov.sg',
      license='Apache License 2.0',
      packages=find_packages(exclude=['tests']),
      install_requires=["networkx>=2.1",
                        "numpy>=1.13.3",
                        "pandas>=0.21.0",
                        "scikit-learn>=0.19.1"],
      url='https://github.com/datagovsg/k-shortest-path',
      classifiers=['Programming Language :: Python :: 3'],
      zip_safe=False)
