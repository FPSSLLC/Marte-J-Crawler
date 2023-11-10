import requests
import os
import random
from dotenv import load_dotenv, find_dotenv
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
load_dotenv(find_dotenv())

http_proxy = os.environ.get("PROXY_HTTP")
https_proxy = os.environ.get("PROXY_HTTPS")


class HTTP:
    def __init__(self):
        self.retries = 15
        self.user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
        self.headers = {
            "User-Agent": self.user_agent,
        }

        self.session = requests.Session()
        self.session.headers.update(self.headers)

        self.session.verify = False

        self.session.trust_env = False

        self.proxies = dict(http=""+http_proxy, https=""+https_proxy)

        self.counters = {
            "get": 0,
            "head": 0,
            "post": 0
        }
        pass

    def post(self, data):
        if "headers" in data:
            self.session.headers.update(data["headers"])
        if self.counters["post"] >= self.retries:
            raise Exception("Retries exceeded with url "+data["url"])
        self.counters["post"] += 1
        try:
            with self.session.post(data["url"], proxies=self.proxies, stream=True, json=data["body"], verify=False) as d:
                d.content
                if d.status_code == 404:
                    return d
                elif d.status_code == 200:
                    if d != None and d.content != None:
                        self.counters["post"] = 0
                        return d
                    else:
                        self.new_proxy()
                        return self.post(data)

                elif d.status_code >= 300 and d.status_code <= 399:
                    self.counters["post"] = 0
                    return d
                else:
                    print(d.status_code)
                    self.new_proxy()
                    return self.post(data)

        except Exception as e:
            print(e)
            self.new_proxy()
            return self.post(data)

    def get(self, data):
        if "headers" in data:
            self.session.headers.update(data["headers"])
        if self.counters["get"] >= self.retries:
            raise Exception("Retries exceeded with url "+data["url"])
        self.counters["get"] += 1
        try:
            with self.session.get(data["url"], proxies=self.proxies, stream=True, verify=False) as d:
                d.content
                if d.status_code == 404:
                    return d
                elif d.status_code == 200:
                    if d != None and d.content != None:
                        self.counters["get"] = 0
                        return d
                    else:
                        self.new_proxy()
                        return self.get(data)

                elif d.status_code >= 300 and d.status_code <= 399:
                    self.counters["get"] = 0
                    return d
                else:
                    print(d.status_code)
                    self.new_proxy()
                    return self.get(data)

        except Exception as e:
            print(e)
            self.new_proxy()
            return self.get(data)

    def head(self, data):
        if self.counters["head"] >= self.retries:
            raise Exception("Retries exceeded with url "+data["url"])
        self.counters["head"] += 1
        try:
            with self.session.head(data["url"], proxies=self.proxies, stream=True, verify=False) as d:
                d.content
                if d.status_code == 404:
                    return d
                elif d.status_code == 200:
                    if d != None and d.content != None:
                        self.counters["head"] = 0
                        return d
                    else:
                        self.new_proxy()
                        return self.get(data)

                elif d.status_code >= 300 and d.status_code <= 399:
                    self.counters["head"] = 0
                    return d
                else:
                    print(d.status_code)
                    self.new_proxy()
                    return self.get(data)

        except Exception as e:
            print(e)
            self.new_proxy()
            return self.get(data)

    def new_proxy(self):
        print("Setting new proxy")
        self.session.close()
        self.session = requests.Session()
