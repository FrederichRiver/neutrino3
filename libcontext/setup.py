#!/usr/bin/python3
from setuptools import setup, find_packages
from dev_global.env import GITHUB_URL, EMAIL

v = (2, 14, 60)

setup(
        name='libcontext',
        version=f"{v[0]}.{v[1]}.{v[2]}",
        packages=find_packages(),
        install_requires=[],
        author='Fred Monster',
        author_email=EMAIL,
        url=GITHUB_URL,
        license='LICENSE',
        description='None'
        )
