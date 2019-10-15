#!/usr/bin/env python

from distutils.core import setup
from io import open
import setuptools

with open("README.md", encoding="utf-8") as f:
    README = f.read()
with open("changelog.md", encoding="utf-8") as f:
    CHANGELOG = f.read()

setup(name='azure-cosmos',
      version='3.1.2',
      description='Azure Cosmos Python SDK',
      long_description=README + "\n\n" + CHANGELOG,
      long_description_content_type="text/markdown",
      author="Microsoft",
      author_email="askdocdb@microsoft.com",
      maintainer="Microsoft",
      maintainer_email="askdocdb@microsoft.com",
      url="https://github.com/Azure/azure-documentdb-python",
      license='MIT',
      install_requires=['six >=1.6', 'requests>=2.10.0'],
      classifiers=[
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Software Development :: Libraries :: Python Modules'
      ],
      packages=setuptools.find_packages(exclude=['test', 'test.*']))
