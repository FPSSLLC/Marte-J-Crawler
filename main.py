import argparse
import json
import sys
from urllib.parse import urlparse
from core import Config,Crawler

sys.dont_write_bytecode = True

parser = argparse.ArgumentParser()
parser.add_argument("-l", "--listing", help="List products")
parser.add_argument("-p", "--product", help="Scrape product")
parser.add_argument("-r", "--run", help="Run full scraper")
parser.add_argument("-o", "--output", help="Define output")
parser.add_argument("-j", "--json", help="JSON payload")
args = parser.parse_args()

config : Config = {}

if args.json:
    config = json.loads(args.json)

if args.run:
    parsed_uri = urlparse(args.run)
    config = {"urls":['{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)], "data": {},"type":"run"}
if args.product:
    parsed_uri = urlparse(args.product)
    config = {"urls": [args.product], "data": {},"type":"product"}
if args.listing:
    parsed_uri = urlparse(args.listing)
    config = {"urls": ['{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)], "data": {},"type":"listing"}
if args.output:
    config["output"] = args.output
else:
    config["output"] = "csv"


crawl = Crawler(config)
