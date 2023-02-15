#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from setuptools import setup

version = "0.2.0"
readme = open("README.md", encoding="utf-8").read()
changes = open("CHANGELOG.md", encoding="utf-8").read()

long_description = f"{readme}\n\n{changes}"


setup(
    name="pytest-leak-finder",
    version=version,
    author="Martín Gaitán",
    author_email="gaitan@gmail.com",
    maintainer="Martín Gaitán",
    maintainer_email="gaitan@gmail.com",
    license="MIT",
    url="https://github.com/mgaitan/pytest-leak-finder",
    description="Find the test that's leaking before the one that fails",
    long_description=long_description,
    long_description_content_type="text/markdown",
    py_modules=["pytest_leak_finder"],
    python_requires=">=3.7",
    install_requires=["pytest>=3.5.0"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Pytest",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
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
