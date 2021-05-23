from libmysql_utils.mysql8 import mysqlHeader
from dev_global.path import CONF_FILE
from libutils.utils import read_json


_IP = read_json("IP", CONF_FILE)
GLOBAL_HEADER = mysqlHeader(acc='stock', pw='stock2020', db='stock', host=_IP[1])
REMOTE_HEADER = mysqlHeader(acc='stock', pw='stock2020', db='stock', host=_IP[1])
ROOT_HEADER = mysqlHeader(acc='root', pw='6414939', db='stock', host=_IP[1])
TASK_HEADER = mysqlHeader(acc='task', pw='task2020', db='task', host=_IP[1])
LOCAL_HEADER = mysqlHeader('stock', 'stock2020', 'stock')
VIEWER_HEADER = mysqlHeader('view', 'view2020', 'stock')
NLP_HEADER = mysqlHeader('stock', 'stock2020', 'natural_language')