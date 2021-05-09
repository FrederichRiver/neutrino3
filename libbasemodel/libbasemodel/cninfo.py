#!/usr/bin/python3
from mars.network import userAgent, cookie


class cninfoSpider(object):
    """
    http_user_agent(): get a Mozilla User_Agent.
    http_user_agent.random_agent(): get a random User_Agent.
    http_cookie.get_cookie(cookie_name): return a cookie by name 'cookie_name'.
    """
    def __init__(self):
        # self.mysql = mysqlBase(mysql_header)
        self.http_user_agent = userAgent()
        self.http_cookie = cookie()
        # self.request = requests
        self.http_header = {
            "Accept": 'application/json, text/javascript, */*; q=0.01',
            "Accept-Encoding": 'gzip, deflate',
            "Accept-Language": 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
            "Connection": 'keep-alive',
            "Content-Length": '155',
            "Content-Type": 'application/x-www-form-urlencoded; charset=UTF-8',
            # "Cookie": 'JSESSIONID=196ABC7DC9783A9A5F1183F0FC14F909; _sp_ses.2141=*; cninfo_user_browse=603019,9900023134,%E4%B8%AD%E7%A7%91%E6%9B%99%E5%85%89; UC-JSESSIONID=C5797E04FA706DCDB026811F21AFF7CA; _sp_id.2141=12284594-c734-478d-82ca-0a1ccbb7de3f.1585407313.1.1585407329.1585407313.107d6c9a-afa9-4539-a924-b01124669401',
            "Cookie": 'JSESSIONID=8B6638DD0C83CD4AB10F76F86112CF43; cninfo_user_browse=603019,9900023134,%E4%B8%AD%E7%A7%91%E6%9B%99%E5%85%89; _sp_ses.2141=*; UC-JSESSIONID=D3B1EA13B965985C23366FCB9DB4B0FC; _sp_id.2141=12284594-c734-478d-82ca-0a1ccbb7de3f.1585407313.2.1585441676.1585408733.e3950f09-4644-4027-bec6-0dbd4bace06a',
            "Host": 'www.cninfo.com.cn',
            "Origin": 'http://www.cninfo.com.cn',
            "Referer": 'http://www.cninfo.com.cn/new/disclosure/stock?stockCode=603019&orgId=9900023134',
            "User-Agent": 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
            "X-Requested-With": 'XMLHttpRequest',
            }


class eastmoneySpider(object):
    def __init__(self) -> None:
        self.http_header = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Cookie": "intellpositionL=583.188px; qgqp_b_id=c296d37f90f4c939cacc16224744f41a; em_hq_fls=js; intellpositionT=1091px; waptgshowtime=202139; HAList=a-sz-300059-%u4E1C%u65B9%u8D22%u5BCC%2Ca-sh-603776-%u6C38%u5B89%u884C%2Ca-sz-300227-%u5149%u97F5%u8FBE%2Ca-sh-603929-%u4E9A%u7FD4%u96C6%u6210%2Ca-sz-300604-%u957F%u5DDD%u79D1%u6280%2Ca-sz-002245-%u6FB3%u6D0B%u987A%u660C; st_si=80758845330570; st_asi=delete; st_pvi=99506938076002; st_sp=2020-07-19%2022%3A28%3A41; st_inirUrl=https%3A%2F%2Fwww.eastmoney.com%2F; st_sn=15; st_psi=20210309233831816-111000300841-6472437881",
            "Host": "quote.eastmoney.com",
            "If-Modified-Since": "Wed, 04 Sep 2019 13:42:17 GMT",
            "If-None-Match": 'W/"e87c88912663d51:0"',
            "Referer": "https://www.baidu.com/s?wd=%E7%BE%8E%E8%82%A1%E5%88%97%E8%A1%A8",
            "Upgrade-Insecure-Requests": 1,
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36"
            }


if __name__ == "__main__":
    pass
