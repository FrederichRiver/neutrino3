#!/usr/bin/python38
"""
global environment varibles

"""

PYTHON_VERSION = 3.8
LOCAL_TIME_ZONE = 'Beijing'
TIME_FMT = '%Y-%m-%d'
LOG_TIME_FMT = "%Y-%m-%d %H:%M:%S"

GITHUB_URL = "https://github.com/FrederichRiver/neutrino2"
EMAIL = "hezhiyuan_tju@163.com"


"""
if os.getenv('SERVER') == 'MARS':
    ROOT_PATH = '/root/'
    SOFT_PATH = '/opt/neutrino/'
else:
    ROOT_PATH = '/home/friederich/Dev/neutrino2/'
    SOFT_PATH = '/home/friederich/Dev/neutrino2/'
"""
ROOT_PATH = '/root/'
SOFT_PATH = '/opt/neutrino/'

PID_FILE = '/tmp/neutrino.pid'
RESTFUL_PID_FILE = '/tmp/restful.pid'

# if os.getenv('MODE') == 'test':
#    LOG_FILE = '/home/friederich/Dev/neutrino2/neutrino.log'
# else:
#    LOG_FILE = SOFT_PATH + 'neutrino.log'

LOG_FILE = SOFT_PATH + 'log/neutrino.log'
TASK_FILE = SOFT_PATH + 'config/task.json'
CONF_FILE = SOFT_PATH + 'config/conf.json'
HEAD_FILE = SOFT_PATH + 'config/header.json'
COOKIE_FILE = SOFT_PATH + 'config/cookie.json'
SQL_FILE = SOFT_PATH + 'config/sql.json'
RESTFUL_FILE = SOFT_PATH + 'log/restful.log'
MANUAL = SOFT_PATH + 'config/Neutrino'

DOWNLOAD_PATH = '/home/fred/stock_data'
