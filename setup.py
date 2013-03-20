#!/usr/bin/env python

#
# Imports
#

# System Imports
from distutils.core import setup

#
# Setup
#

setup(
    # Metadata
    name='mfgames-font',
    version='0.0.0.0',
    description='Utilities for working with fonts.',
    author='Dylan R. E. Moonfire',
    author_email="contact@mfgames.com",
    url='http://mfgames.com/mfgames-font-python',
    classifiers=[
        "Development Status :: 1 - Planning",
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Topic :: Artistic Software",
        "Topic :: Office/Business",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],

    # Scripts
    scripts=[
        'src/mfgames-font',
        ],

    # Packages
    packages=[
        "mfgames_font",
        ],
    package_dir = {'': 'src'}
    )
