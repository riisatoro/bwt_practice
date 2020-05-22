import scrapy
import json
import logging

import schema
from scrapy.utils.log import configure_logging

logging.basicConfig(
    filename='logs/product_log.txt',
    format='%(levelname)s: %(message)s',
    level=logging.INFO
)


class Products(scrapy.Spider):
    """docs"""
    name = "products"
    start_urls = [
        'https://www.tesco.com/groceries/en-GB/shop/household/kitchen-roll-and-tissues/all?page=1',
        'https://www.tesco.com/groceries/en-GB/shop/pets/cat-food-and-accessories/all?page=1'
    ]

    def parse(self, response):
        if response.status == 404:
            return

        products = response.xpath(schema.PRODUCTS_URL).getall()

        for url in products:
            yield scrapy.Request(url=schema.GLOBAL_URL+url, callback=self.split_data)

        url = response.request.url
        splited_url = url.split("=")
        splited_url[-1] = str(int(splited_url[-1])+1)
        new_url = "=".join(splited_url)

        yield scrapy.Request(url=new_url, callback=self.parse)

    def split_data(self, response):
        product = {}
        product["URL"] = response.url
        product["ID"] = int(response.url.split("/")[-1])
        product["review"] = []

        for key in schema.SINGLE_DATA.keys():
            product[key] = response.xpath(schema.SINGLE_DATA[key]).get()
            if key == "review_amount":
                try:
                    product[key] = int(product[key].split(" ")[0])//10+1
                except Exception as e:
                    product[key] = 0

        for key in schema.MULTIPLE_DATA.keys():
            product[key] = ' . '.join(response.xpath(schema.MULTIPLE_DATA[key]).getall())

        try:
            product["bought_next"] = self.split_bought(response)
        except Exception as e:
            print("[Exception]:", e)
            pass

        yield self.save_data(product)

    def split_bought(self, response):
        result = []
        
        bought_next = response.xpath(schema.BOUGHT_NEXT_LIST)
        for product in bought_next:
            tmp = {}
            for key in schema.BOUGHT_CSS.keys():
                tmp[key] = product.css(schema.BOUGHT_CSS[key]).get()
                if key == "URL":
                    tmp[key] = schema.GLOBAL_URL+tmp[key]
            result.append(tmp)

        return result

    def save_data(self, item):
        with open('parsed/data.json', 'r') as file:
            data = json.load(file)
            data['items'].append(item)
        with open('parsed/data.json', 'w') as file:
            json.dump(data, file, indent=4)
