from typing import TypedDict,List
from utils.http import HTTP

from utils.my_types import ProductListingInput,ProductListingOutput,ProductScraperInput,Variant

# Product listing function
def product_listing(data:ProductListingInput)->ProductListingOutput:
	print(data)
	return {
		"site":data["site"],
		"urls":["https://test.com/"],
		"data":{}
	}

# Product scraping function
def product_scraping(data:ProductScraperInput)->List[Variant]:
	print(data)
	return []


