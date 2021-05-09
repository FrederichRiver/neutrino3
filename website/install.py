import os
ALIYUN_ROOT = '/home/friederich/Documents/dev/neutrino/applications/orion'
ALIYUN_SITE = '/var/www/neutrino'
DIST_DIR = '/home/friederich/Documents/dev/neutrino/applications/dist/orion'
os.system(f"sudo cp -r {ALIYUN_ROOT}/neutrino/* {ALIYUN_SITE}/neutrino/")
os.system(f"sudo cp -r {ALIYUN_ROOT}/dev/* {ALIYUN_SITE}/dev/")
os.system(f"sudo cp -r {ALIYUN_ROOT}/index/* {ALIYUN_SITE}/index/")
os.system(f"sudo cp -r {ALIYUN_ROOT}/templates/* {ALIYUN_SITE}/templates/")
os.system(f"sudo cp -r {ALIYUN_ROOT}/static/* {ALIYUN_SITE}/static/")
os.system(f"cp -r {ALIYUN_ROOT}/* {DIST_DIR}")
