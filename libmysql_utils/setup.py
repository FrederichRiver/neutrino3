#!/usr/bin/python3
from setuptools import setup, find_packages
from dev_global.env import GITHUB_URL

v = (2, 4, 13)

setup(
        name='libmysql_utils',
        version=f"{v[0]}.{v[1]}.{v[2]}",
        packages=find_packages(),
        author='Fred Monster',
        author_email='hezhiyuan_tju@163.com',
        url=GITHUB_URL,
        license='LICENSE',
        description='None',
        )
