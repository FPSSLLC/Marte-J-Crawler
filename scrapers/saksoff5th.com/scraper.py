from bs4 import BeautifulSoup
from urllib import parse
from itertools import permutations
import importlib.util,os,requests,json
from urllib.parse import urlparse
from typing import TypedDict,List
from utils.http import HTTP

from utils.my_types import ProductListingInput,ProductListingOutput,ProductScraperInput,Variant,PostProcess,PreProcess,PerVariant

http=HTTP()



	

def product_listing(data:ProductListingInput)->ProductListingOutput:

	pages=[]
	headers={
		"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/115.0",
		"Accept": "*/*",
		"Accept-Language": "en-US,en;q=0.5",
		"X-Requested-With": "XMLHttpRequest",
		"Sec-Fetch-Dest": "empty",
		"Sec-Fetch-Mode": "cors",
		"Sec-Fetch-Site": "same-origin"
	}
	def list_pages(url):
		print("Listing products",url)
		#This can be replaced with proxy support and retries
		s=http.get({"url":url,"headers":headers})
		soup = BeautifulSoup(s.content,features="xml")
		urls = soup.find_all("loc")
		for u in urls:
			pages.append(u.text)
	list_pages('https://www.saksoff5th.com/sitemap_0-product.xml')
	list_pages('https://www.saksoff5th.com/sitemap_1-product.xml')

	return {
		"site":data["site"],
		"urls":pages,
		"data":{}
	}



def product_scraping(data:ProductScraperInput)->List[Variant]:

	headers={
		"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/115.0",
		"Accept": "*/*",
		"Accept-Language": "en-US,en;q=0.5",
		"X-Requested-With": "XMLHttpRequest",
		"Sec-Fetch-Dest": "empty",
		"Sec-Fetch-Mode": "cors",
		"Sec-Fetch-Site": "same-origin"
	}
	print("Scraping page",data["product_url"])
	x=http.get({"url":data["product_url"],"headers":headers})

	soup = BeautifulSoup(x.content.decode(),features="lxml")

	variant_pages=[]
	urls = soup.select('button[data-url]')
	for u in urls:
		y=u.get("data-url")
		if y!=None:
			if y.startswith("https://www.saksoff5th.com/on/demandware.store/Sites-SaksOff5th-Site/en_US/Product-Variation"):
				variant_pages.append(y)

	urls = soup.select('.attributes a')
	for u in urls:
		y=u.get("href")
		if y!=None:
			if y.startswith("https://www.saksoff5th.com/on/demandware.store/Sites-SaksOff5th-Site/en_US/Product-Variation"):
				variant_pages.append(y)


	urls = soup.select('option[data-url]')
	for u in urls:
		y=u.get("data-url")
		if y!=None:
			if y.startswith("https://www.saksoff5th.com/on/demandware.store/Sites-SaksOff5th-Site/en_US/Product-Variation") or y.startswith("/"):
				variant_pages.append(y)


	def fix_url(x):
		if x.startswith("/"):
			return "https://www.saksoff5th.com"+x
		else:
			return x
	variant_pages=list(map(fix_url, variant_pages))

	product_variation=json.loads(http.get({"url":variant_pages[0],"headers":headers}).content.decode())

	pv=product_variation["product"]["variationAttributes"]
	data=[]
	for i in pv:
		attr_in=[]
		attr_val=i["values"]
		for av in attr_val:
			attr_in.append("dwvar_"+product_variation["product"]["masterProductID"]+"_"+i["id"]+"="+av["id"])
		data.append(attr_in)

	other_params=["quantity=1","pid="+product_variation["product"]["masterProductID"]]


	unique_combinations = []
	if len(data)>1:
		for i in range(len(data[0])):
			for j in range(len(data[1])):
				unique_combinations.append((data[0][i], data[1][j]))
	else:
		for i in data[0]:
			unique_combinations.append([i])

	jsonmktdata=soup.select('#productMktData')[0].get_text()

	offers=json.loads(jsonmktdata)["offers"]

	# field_names=list(data[0].keys())



	

	variants=[]
	for uc in unique_combinations:
		result='&'.join([*list(uc),*other_params])
		api="https://www.saksoff5th.com/on/demandware.store/Sites-SaksOff5th-Site/en_US/Product-Variation?"+result
		x=http.get({"url":api,"headers":headers})
		print("API URL",api)
		# print(x.content.decode())
		j=json.loads(x.content.decode())

		upc=""
		for o in offers:
			if str(o["SKU"])==str(j["product"]["id"]):
				upc=str(o["gtin13"])

		pnum=j["product"]["masterProductID"]

		brand=j["product"]["brand"]["name"]
		name=j["product"]["productName"]
		sku=j["product"]["manufacturerSKU"]
		sales_price=j["product"]["price"]["sales"]["value"]
		list_price=j["product"]["price"]["list"]["value"]
		if sales_price:
			price=float(sales_price)
		else:
			price=float(list_price)
		
		variation_attributes=j["product"]["variationAttributes"]
		options={}
		for i in variation_attributes:
			for x in i["values"]:
				if x["selected"]==True:
					options[i["displayName"]]=x["displayValue"]




		availability=json.loads(http.get({"url":"https://www.saksoff5th.com/on/demandware.store/Sites-SaksOff5th-Site/en_US/Product-AvailabilityAjax?pid="+j["product"]["id"]+"&quantity=1&readyToOrder=false","headers":headers}).content.decode())["product"]["available"]

		url=j["product"]["pdpURL"]
		images=list(map(lambda x: x["url"], j["product"]["images"]["hi-res"]))
		
		data={
			"store":"saksoff5th",
			"brand":brand,
			"product_title":name,
			"product_url":url,
			"image_url":images[0],
			"upc":upc,	
			"sku":sku,
			"product_model":"",
			"mpn":pnum,
			"price":price,
			"availability":availability,
			"options":options,
			"bundle":[]
		}

		variants.append(data)
	return variants




