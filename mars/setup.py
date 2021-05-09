#!/usr/bin/python3
from setuptools import setup, find_packages
from mars import __version__ as v
setup(
        name='mars',
        version=v,
        packages=find_packages(),
        # install_requires=['psutil>=5.7.0',],
        author='Fred Monster',
        author_email='hezhiyuan_tju@163.com',
        url='https://github.com/FrederichRiver/neutrino',
        license='LICENSE',
        description='None'
        )
