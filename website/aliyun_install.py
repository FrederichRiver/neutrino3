import os
ALIYUN_ROOT = '/root/ftp/orion'
ALIYUN_SITE = '/var/www/neutrino'
os.system(f"sudo cp -r {ALIYUN_ROOT}/main/* {ALIYUN_SITE}/main/")
os.system(f"sudo cp -r {ALIYUN_ROOT}/index/* {ALIYUN_SITE}/index/")
os.system(f"sudo cp -r {ALIYUN_ROOT}/templates/* {ALIYUN_SITE}/templates/")
os.system(f"sudo cp -r {ALIYUN_ROOT}/static/* {ALIYUN_SITE}/static/")
