#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

def readme():
    with open('README.rst') as f:
        return f.read()

requirements = [
    'pyproj==1.9.5.1',
    'matplotlib==2.0.2',
    'numpy==1.13.1',
    'pandas==0.20.1',
    'Click>=6.0',
    'requests==2.14.2',
]

setup(
    name='movementtypes',
    version='0.1.0',
    entry_points='''
        [console_scripts]
        mvtypes=movementtypes.cli:main
    ''',
    packages=find_packages(),
    license='MIT',
    author='Huang-Sin Syu, Tyng-Ruey Chuang',
    author_email='sheu781230@gmail.com, trc@iis.sinica.edu.tw',
    url='https://github.com/gipong/movementtypes.git',
    long_description=readme(),
    install_requires=requirements,
    include_package_data=True,
    zip_safe=False,
)