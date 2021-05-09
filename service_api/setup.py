#!/usr/bin/python3
from setuptools import setup, find_packages
from service_api import __version__ as v
setup(
        name='service_api',
        version=f"{v[0]}.{v[1]}.{v[2]}",
        packages=find_packages(),
        author='Fred Monster',
        author_email='hezhiyuan_tju@163.com',
        url='https://github.com/FrederichRiver/neutrino',
        license='LICENSE',
        description='None'
        )
