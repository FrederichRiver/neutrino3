#!/usr/bin/python3
from setuptools import setup, find_packages
from dev_global.env import GITHUB_URL, EMAIL
from venus import __version__ as v
setup(
        name='venus',
        version=f"{v[0]}.{v[1]}.{v[2]}",
        packages=find_packages(),
        install_requires=['sqlalchemy>=1.3.16', 'pandas>=1.0.5', 'lxml', 'requests'],
        author='Fred Monster',
        author_email=EMAIL,
        url=GITHUB_URL,
        license='LICENSE',
        description='None'
        )
