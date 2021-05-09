#!/usr/bin/python3
from mars.network import userAgent, cookie
import requests
import re


class PriceMonitor(object):
    def __init__(self) -> None:
        self.http_header = {
            "Referer": "https://finance.sina.com.cn/futuremarket/",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36"
            }

    def monitor(self):
        # url = "https://hq.sinajs.cn/rn=1615481409084&list=DINIW,hf_CL,hf_GC,hf_SI,hf_S,hf_C,hf_OIL,hf_CAD,hf_CHA50CFD"
        url = "https://hq.sinajs.cn/rn=1615481409084&list=hf_CL,hf_OIL"
        result = requests.get(url)
        # print(result.text)
        wti = re.search(r'hq_str_hf_CL=\"(.*)\"', result.text)
        # print(wti.group(1))
        seq = wti.group(1).split(',')
        # print(f"Date: {seq[12]}, Time: {seq[6]}")
        # print(f"Open price: {seq[8]}")
        # print(f"Latest price: {seq[0]}")
        # print(f"High price: {seq[4]}")
        # print(f"Low price: {seq[5]}")
        rate = '%.2f%%' % ((float(seq[0]) / float(seq[7]) - 1) * 100)
        # print(f"Amplitude: {rate}")
        with open('/home/friederich/Dev/neutrino2/data/wti_price', 'a') as f:
            # f.write(f"{seq[12]},{seq[6]},{seq[0]},{seq[8]},{seq[1]},{seq[4]},{seq[5]},{seq[7]},{rate}\n")
            f.write(f"{wti.group(1)}\n")
        brent = re.search(r'hq_str_hf_OIL=\"(.*)\"', result.text)
        # print(wti.group(1))
        seq = brent.group(1).split(',')
        # print(f"Date: {seq[12]}, Time: {seq[6]}")
        # print(f"Open price: {seq[8]}")
        # print(f"Latest price: {seq[0]}")
        # print(f"High price: {seq[4]}")
        # print(f"Low price: {seq[5]}")
        rate = '%.2f%%' % ((float(seq[0]) / float(seq[7]) - 1) * 100)
        # print(f"Amplitude: {rate}")
        with open('/home/friederich/Dev/neutrino2/data/brent_price', 'a') as f:
            # f.write(f"{seq[12]},{seq[6]},{seq[0]},{seq[8]},{seq[1]},{seq[4]},{seq[5]},{seq[7]},{rate}\n")
            f.write(f"{brent.group(1)}\n")

    def foriegn_future(self):
        url = "https://hq.sinajs.cn/rn=1615481409084&list=hf_CL,hf_OIL,hf_CHA50CFD"
        result = requests.get(url)
        wti = re.search(r'hq_str_hf_CL=\"(.*)\"', result.text)
        brent = re.search(r'hq_str_hf_OIL=\"(.*)\"', result.text)
        a50 = re.search(r'hq_str_hf_CHA50CFD=\"(.*)\"', result.text)
        file_name = '/home/friederich/Dev/neutrino2/data/'
        # file_name = '/var/data_volume/app/future_data'
        with open(file_name + 'wti_price', 'a') as f1:
            f1.write(f"{wti.group(1)}\n")
        with open(file_name + 'brent_price', 'a') as f2:
            f2.write(f"{brent.group(1)}\n")
        with open(file_name + 'a50_price', 'a') as f3:
            f3.write(f"{a50.group(1)}\n")

    def inland_future(self):
        url = "https://hq.sinajs.cn/rn=1615562194587&list=hf_GC,hf_SI,gds_AUTD,gds_AGTD,nf_AU0,nf_AG0"
        result = requests.get(url)
        ny_gold = re.search(r'hq_str_hf_GC=\"(.*)\"', result.text)
        ny_silver = re.search(r'hq_str_hf_SI=\"(.*)\"', result.text)
        sh_gold = re.search(r'hq_str_nf_AU0=\"(.*)\"', result.text)
        sh_silver = re.search(r'hq_str_nf_AG0=\"(.*)\"', result.text)
        file_name = '/home/friederich/Dev/neutrino2/data/'
        with open(file_name + 'nygold_price', 'a') as f1:
            f1.write(f"{ny_gold.group(1)}\n")
        with open(file_name + 'nysilver_price', 'a') as f2:
            f2.write(f"{ny_silver.group(1)}\n")
        with open(file_name + 'SHgold_price', 'a') as f3:
            f3.write(f"{sh_gold.group(1)}\n")
        with open(file_name + 'SHsilver_price', 'a') as f4:
            f4.write(f"{sh_silver.group(1)}\n")


if __name__ == '__main__':
    import time
    import random
    # from libbasemodel.data_monitor import PriceMonitor
    event = PriceMonitor()
    while True:
        i = random.randint(-5, 10)
        try:
            event.foriegn_future()
            event.inland_future()
        except Exception:
            pass
        time.sleep(30 + i)
