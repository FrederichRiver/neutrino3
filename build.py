#!/usr/bin/python38
import os

PROJ_PATH = '/home/friederich/Dev/neutrino2'
# Test
lib_list = ['dev_global', 'libstrategy', 'libnlp', 'mars', 'libcontext', 'service_api', 'libmysql_utils', 'libbasemodel', 'libtask', 'libspider']
for lib in lib_list:
    # go into library directory
    os.chdir(f"{PROJ_PATH}/{lib}")
    # run setup script
    os.system("python3 setup.py sdist")
    # remove egg-info file in package
    # os.system(f"rm -r {lib}.egg-info")
    # cp package in lib/dist into root path
    os.system(f"cp -r dist/ {PROJ_PATH}/")
    # remove lib/dist
    os.system("rm -r dist/")
