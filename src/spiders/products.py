import scrapy
import json

from scrapy.selector import Selector


class Products(scrapy.Spider):
    """docs"""
    name = "products"
    start_urls = [
        'https://www.tesco.com/groceries/en-GB/shop/household/kitchen-roll-and-tissues/all'
    ]

    def parse(self, response):
        #!empty
        products = response.xpath('//div[@class="product-details--content"]/h3/a/@href').getall()
        #print("[PRODUCTS]: ", products)
        for url in products:
            yield scrapy.Request(url="https://www.tesco.com"+url, callback=self.split_data)

    def split_data(self, response):
        #dict with all xpath list to simplify editing
        #data 'in one row'
        single_data = {
            "image": '//img[@class="product-image"]/@src',
            "prod_title": '//h1[@class="product-details-tile__title"]/text()',
            "price": '//span[@data-auto="price-value"]/text()',
        }

        #make list of xpath to combine description blocks
        #xpath for lists and multiple divs
        mul_data = {
            "description": '//div[@id="product-description"]/ul/li/text()',
            "address": '//div[@id="manufacturer-address"]/ul[@class="product-info-block__content"]/li/text()',
            "return": '//div[@id="return-address"]/ul/li/text()',
            "net_contents": '//div[@id="net-contents"]/p/text()',
        }

        rev_data = '//p[@class="reviews-list__show-more"]/a/@href'

        bought_next_data = {
            "URL": '',
            "title": '',
            "image": '',
            "price": '',
        }

        product = {}
        review = {}
        bought_next = {}

        product["URL"] = response.url
        product["ID"] = int(response.url.split("/")[-1])

        for key in single_data.keys():
            product[key] = response.xpath(single_data[key]).get()

        for key in mul_data.keys():
            product[key] = ' '.join(response.xpath(mul_data[key]).getall())

        try:
            product["review"] = self.split_review(response)
        except Exception as e:
            print("[EXCEPTION]: ", e)

        yield self.save_data(product)

    def split_review(self, response):
        review_data = '//article[@class="review"]'
        
        review_css = {
            "title": 'h3.review__summary::text',
            "stars": 'span.czgxkL::text',
            "author": 'span.review-author__nickname::text',
            "date": 'span.review-author__submission-time::text',
            "text": 'p.review__text::text'
        }
        
        #get all reviews on the page
        result = []
        reviews = response.xpath(review_data)
        for rev in reviews:
            tmp = {}
            for key in review_css.keys():
                tmp[key] = rev.css(review_css[key]).get()
                if key == "stars":
                    tmp[key] = int(tmp[key][0])
            result.append(tmp)

        return result

    def save_data(self, item):
        with open('parsed/data.json', 'r') as file:
            data = json.load(file)
            data['items'].append(item)
        with open('parsed/data.json', 'w') as file:
            json.dump(data, file, indent=4)
