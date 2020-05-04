import scrapy 
import json

from . import schema

class Review(scrapy.Spider):
    name = 'reviews'

    def start_requests(self):
        with open('parsed/data.json', 'r') as file:
            products = json.load(file)["items"]

        for product in products:
            for page in range(1, product["review_amount"]):
                url = product["URL"]+schema.REVIEW_URL.format(page)
                yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        #get all reviews on the page
        result = []
        reviews = response.xpath(schema.REVIEW_DATA)
        for rev in reviews:
            tmp = {}
            for key in schema.REVIEW_CSS.keys():
                tmp[key] = rev.css(schema.REVIEW_CSS[key]).get()
                if key == "stars":
                    tmp[key] = int(tmp[key][0])
            result.append(tmp)
        self.save_data(result, response.request.url)


    def save_data(self, result, url):
        ID = int(url.split("?")[0].split("/")[-1])
        data = None
        with open('parsed/data.json', 'r') as file:
            data = json.load(file)

        for index in range(len(data["items"])):
            if data["items"][index]["ID"] == ID:
                data["items"][index]["review"].extend(result)

        with open('parsed/data.json', 'w') as file:
            json.dump(data, file, indent=4)