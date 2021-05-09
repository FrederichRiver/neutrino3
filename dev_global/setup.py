#!/usr/bin/python3
from setuptools import setup, find_packages
from dev_global import __version__ as v
setup(
        name='dev_global',
        version=v,
        packages=find_packages(),
        author='Fred Monster',
        author_email='hezhiyuan_tju@163.com',
        url='https://github.com/FrederichRiver/neutrino2',
        license='LICENSE',
        description='None'
        )
