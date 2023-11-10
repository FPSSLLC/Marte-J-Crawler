import os
import sys
import yaml
import importlib.util
from os.path import exists
from urllib.parse import urlparse
from typing import TypedDict

# Crawler

# Test

sys.dont_write_bytecode = True

class Config(TypedDict):
    urls: list
    data: dict
    type: str
    output: str


class Crawler:
    def load_module(self, module):
        sp = importlib.util.spec_from_file_location("m", module)
        m = importlib.util.module_from_spec(sp)
        sp.loader.exec_module(m)
        return m

    def __init__(self,config : Config):
        dirname = os.path.dirname(os.path.realpath(__file__))
        copy_config=config.copy()
        output_type=copy_config["output"]

        if ("urls" in config and len(config["urls"])==0) or not "urls" in config:
            with open(f'{dirname}/run/config.yml', 'r') as config_file:
                self.config = yaml.safe_load(config_file)
                if not "output" in self.config:
                    self.config["output"]=output_type
                if not "data" in self.config:
                    self.config["data"]={}
        else:
            self.config=config

        self.domain = urlparse(self.config["urls"][0]).netloc.replace("www.", "")

        output_config = self.config.copy()
        output_config["domain"] = self.domain
        output_config["dirname"] = dirname
        self.output_module = self.load_module(f"{dirname}/utils/{self.config['output']}.py").Output(output_config)

        self.module_path = f"{dirname}/scrapers/{self.domain}/scraper.py"
        self.variants = []
        self.run_scraper()

    def run_scraper(self):
        if exists(self.module_path):
            module = self.load_module(self.module_path)

            if self.config["type"]!="product":
                if hasattr(module, 'product_listing'):
                    self.config["urls"] = module.product_listing({
                        "site": self.config["urls"][0],
                        "data": self.config["data"]
                    })["urls"]
                    if self.config["type"]=="listing":
                        self.output_module.write_listing(self.config["urls"])
                else:
                    raise Exception(
                        "Missing product_listing function in scraper at", self.module_path)

            if self.config["type"]!="listing":
                for urlid, url in enumerate(self.config["urls"]):
                    print("Scraping", url)
                    if hasattr(module, 'product_scraping'):
                        variants = module.product_scraping({
                            "product_url": url,
                            "functions": {},
                            "data": self.config["data"]
                        })
                        for variant in variants:
                            if len(variant)!=0:
                                variant["scraper_id"]=self.domain
                                self.variants.append(variant)
                                self.output_module.write_products(variant)
                    else:
                        raise Exception(
                            "Missing product_scraping function in scraper at", self.module_path)

        else:
            raise Exception("Scraper not found :(", self.module_path)
