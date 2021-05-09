#!/usr/bin/python3
from setuptools import setup, find_packages
from dev_global.env import GITHUB_URL, EMAIL

v = (1, 4, 12)

setup(
        name='libspider',
        version=f"{v[0]}.{v[1]}.{v[2]}",
        packages=find_packages(),
        install_requires=['requests'],
        author='Fred Monster',
        author_email=EMAIL,
        url=GITHUB_URL,
        license='LICENSE',
        description='None'
        )
