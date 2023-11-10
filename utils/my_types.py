from typing import TypedDict,List

class ProductListingOutput(TypedDict):
	site: str
	urls: list
	
class ProductListingInput(TypedDict):
	site:str
	
class ProductScraperInput(TypedDict):
	product_url:str

class Variant(TypedDict):
	store:str
	brand:str
	product_title:str
	product_url:str
	image_url:str
	upc:str
	sku:str
	product_model:str
	mpn:str
	price:float
	availability:bool
	options:dict
	bundle:list
	

class PostProcess(TypedDict):
	result: list
	pre_process_data: dict
	extra: dict


class PreProcess(TypedDict):
	shopify_product: dict
	product_url: str
	data:dict
	extra: dict
	

class PerVariant(TypedDict):
	variant: Variant
	shopify_variant: dict
	shopify_product:dict
	pre_process_data: dict
	extra:dict