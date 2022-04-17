#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
import os

from setuptools import setup


def read(fname):
    file_path = os.path.join(os.path.dirname(__file__), fname)
    return codecs.open(file_path, encoding="utf-8").read()


setup(
    name="pytest-leak-finder",
    version="0.1.0",
    author="Martín Gaitán",
    author_email="gaitan@gmail.com",
    maintainer="Martín Gaitán",
    maintainer_email="gaitan@gmail.com",
    license="MIT",
    url="https://github.com/mgaitan/pytest-leak_finder",
    description="Find the previous test that makes another to fail",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    py_modules=["pytest_leak_finder"],
    python_requires=">=3.5",
    install_requires=["pytest>=3.5.0"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Pytest",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
    ],
    entry_points={
        "pytest11": [
            "leak_finder = pytest_leak_finder",
        ],
    },
)
