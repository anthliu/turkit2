# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='turkit2',
    version='0.0.1',
    description='Flexible Human Computation on Boto3',
    long_description=readme,
    author='Anthony Liu',
    author_email='anthliu@umich.edu',
    url='https://github.com/anthliu/turkit2',
    license=license,
    packages=find_packages(exclude=('tests', 'docs', 'examples'))
)
