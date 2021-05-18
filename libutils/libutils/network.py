#! /usr/bin/python3
import json
import os
import requests
from dev_global.path import COOKIE_FILE, HEAD_FILE
from lxml import etree
from random import randint
from .utils import read_json


class cookie(object):
    def __init__(self):
        self.js = None
        with open(COOKIE_FILE, 'r') as f:
            result = f.read()
            self.js = json.loads(result)

    def get_cookie(self, name: str) -> str:
        return self.js[name]


class CookieBase(object):
    """
    API:
    1. CookieBase.from_file
    2. get_cookie after setting value.
    """
    def __init__(self) -> None:
        self._cookie = {}

    def _set_expire(self, expire_time: str) -> None:
        self._cookie["Expires"] = expire_time

    def _set_domain(self, domain: str) -> None:
        self._cookie["Domain"] = domain

    def _set_path(self, path: str) -> None:
        self._cookie["Path"] = path

    def _set_value(self, key_name: str, value: str):
        self._cookie[key_name] = value

    def from_file(self, cookie_file: str, idx: str) -> str:
        """
        Read cookie text from file where user write in.
        """
        if os.path.exists(cookie_file):
            _, cookie_text = read_json(idx, cookie_file)
        else:
            raise FileNotFoundError("Cookie config file is not found.")
        return cookie_text

    def __str__(self) -> str:
        if self._cookie:
            cookie_pair = []
            for k, v in self._cookie:
                cookie_pair.append(f"{k}={v}")
            result = "; ".join(cookie_pair)
        else:
            result = ""
        return result

    def get_cookie(self):
        return self.__str__


class RandomHeader(object):
    def __init__(self):
        self.js = None
        with open(HEAD_FILE, 'r') as f:
            result = f.read()
            self.js = json.loads(result)
        self.header = None

    def set_user_agent(self):
        index = randint(0, len(self.js)-1)
        self.header = {"User-Agent": self.js[str(index)]}

    def set_refer(self, reference):
        if not self.header:
            self.set_user_agent()
        self.header['Referer'] = reference

    def __call__(self):
        index = randint(0, len(self.js)-1)
        header = {"User-Agent": self.js[str(index)]}
        return header


class HttpHeaderBase(object):
    def __init__(self):
        self._http_header = {}

    def _set_ua(self, user_agent: str):
        self._http_header["User-Agent"] = user_agent

    def _set_refer(self, reference):
        self._http_header['Referer'] = reference

    def _set_cookie(self, cookie: str):
        self._http_header["Cookie"] = cookie

    def _set_host(self, site: str, port=80):
        if port == 80:
            host = site
        else:
            host = f"{site}:{str(port)}"
        self._http_header["Host"] = host

    def __call__(self):
        return self._http_header

    def __str__(self):
        content = ""
        for k, v in self._http_header:
            content += f'{k}: {v}\n'
        return content


class userAgent(object):
    """
    Example:
    object = usrAgent()
    result = object(), get a str type result which is User_Agent.
    result = object.random_agent, get a random User_Agent from liboratory.
    """
    def __init__(self):
        self.js = None
        with open(HEAD_FILE, 'r') as f:
            result = f.read()
            self.js = json.loads(result)
        self.header = None

    def random_agent(self) -> str:
        i = randint(0, len(self.js)-1)
        return self.js[str(i)]

    def __call__(self):
        return self.js["10"]


def delay(n):
    """
    Delay delta time not longer than n seconds.
    """
    import time
    time.sleep(randint(1, n))


def fetch_html_object(url, header):
    """
    result is a etree.HTML object
    """
    response = None
    while not response:
        response = requests.get(url, headers=header, timeout=3)
        delay(5)
    response.encoding = response.apparent_encoding
    result = etree.HTML(response.text)
    return result
