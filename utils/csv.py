import os
import csv
import datetime
import barcodenumber
import re
from os.path import exists


class Output:
    def __init__(self, config):

        file_path = f'{config["dirname"]}/output/{config["domain"]}.csv'

        file_exists = exists(file_path)
        if "site" in config and file_exists:
            os.remove(file_path)
        # CSV headers
        field_names = [
            "Scrape Date",
            "Scrape Time",
            "Store Name",
            "Product Brand",
            "Product Name",
            "Product URL",
            "Product Image URL",
            "Product UPC (verified)",
            "Product UPC (unverified)",
            "SKU",
            "Product Model",
            "Manufacturer #",
            "Product Price",
            "In Stock",
            "Color",
            "Size",
            "Option #1",
            "Option #2",
            "Option #3",
            "Option #4",
            "Bundle Products"
        ]
        # dirname=os.path.dirname(os.path.abspath(__file__))
        file_exists = exists(file_path)
        self.csvfile = open(file_path, 'a', encoding='utf-8', newline='')
        self.writer = csv.DictWriter(self.csvfile, fieldnames=field_names)
        if not file_exists:
            self.writer.writeheader()

    def write_listing(self, urls):
        return None

    def write_products(self, data):
        if "url" in data:
            print(data["url"])

        if "url" not in data:
            if data["upc"] != "":
                data["upc"] = "UPC-"+str(data["upc"])
            availability = "No"
            if data["availability"] == True:
                availability = "Yes"

            opts = {
                "color": "",
                "size": ""
            }
            counter = 1
            options = ["", "", "", "", ""]
            for k, v in data["options"].items():
                if "color" in k.lower():
                    opts["color"] = v
                if "size" in k.lower():
                    opts["size"] = v
                options[counter] = k+": "+v
                counter += 1

            def validate_upc(barcode):
                upc = ""
                unverified_upc = ""
                if barcode != None:
                    barcode = re.sub('\D', '', barcode.encode(
                        "ascii", "ignore").decode())
                    if barcode.isdigit():
                        barcode = str(int(barcode))
                    if len(barcode) < 12:
                        barcode = "000000000000000"+barcode
                        barcode = barcode[-12:]

                    if barcode != "" and barcode != "000000000000":
                        if barcodenumber.check_code('upc', barcode) or barcodenumber.check_code('ean13', barcode) or barcodenumber.check_code('gtin14', barcode):
                            upc = "UPC-"+str(barcode)
                        else:
                            if len(barcode) > 8:
                                unverified_upc = "UPC-"+barcode
                return {
                    "verified": upc,
                    "unverified": unverified_upc
                }

            upc_data = validate_upc(data["upc"])

            bundle = ""
            if len(data["bundle"]) > 0:
                bundle = ', '.join(data["bundle"])

            row = {
                "Scrape Date": datetime.datetime.now().strftime('%m/%d/%Y'),
                "Scrape Time": datetime.datetime.now().strftime('%H:%M:%S'),
                "Store Name": data["store"],
                "Product Brand": data["brand"],
                "Product Name": data["product_title"],
                "Product URL": data["product_url"],
                "Product Image URL": data["image_url"],
                "Product UPC (verified)": upc_data["verified"],
                "Product UPC (unverified)": upc_data["unverified"],
                "Product Model": data["product_model"],
                "SKU": data["sku"],
                "Manufacturer #": data["mpn"],
                "Product Price": "$"+str(data["price"]),
                "In Stock": availability,
                "Color": opts["color"],
                "Size": opts["size"],
                "Option #1": options[1],
                "Option #2": options[2],
                "Option #3": options[3],
                "Option #4": options[4],
                "Bundle Products": bundle

            }
            self.writer.writerows([row])
            self.csvfile.flush()

    def close(self):
        self.csvfile.close()
