import scrapy
import json

from spiders.reviews import Review

class Products(scrapy.Spider):
    """docs"""
    name = "products"
    start_urls = [
        'https://www.tesco.com/groceries/en-GB/shop/household/kitchen-roll-and-tissues/all?page=1',
        #'https://www.tesco.com/groceries/en-GB/shop/pets/cat-food-and-accessories/all?page=1'
    ]

    def __init__(self):
        self.reviews = []

    def parse(self, response):
        if response.status == 404:
            return

        products = response.xpath('//div[@class="product-details--content"]/h3/a/@href').getall()

        for url in products:
            yield scrapy.Request(url="https://www.tesco.com"+url, callback=self.split_data)

        url = response.request.url
        splited_url = url.split("=")
        splited_url[-1] = str(int(splited_url[-1])+1)
        new_url = "=".join(splited_url)

        yield scrapy.Request(url=new_url, callback=self.parse)

    def split_data(self, response):
        #dict with all xpath list to simplify editing
        #data 'in one row'
        single_data = {
            "image": '//img[@class="product-image"]/@src',
            "prod_title": '//h1[@class="product-details-tile__title"]/text()',
            "price": '//span[@data-auto="price-value"]/text()',
            "review_amount":'//h2[@class="reviews-list__header"]/text()',
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


        product = {}
        review = {}
        bought_next = {}

        product["URL"] = response.url
        product["ID"] = int(response.url.split("/")[-1])
        product["review"] = []

        for key in single_data.keys():
            product[key] = response.xpath(single_data[key]).get()
            if key == "review_amount":
                try:
                    product[key] = int(product[key].split(" ")[0])//10+1
                except Exception as e:
                    product[key] = 0

        for key in mul_data.keys():
            product[key] = ' '.join(response.xpath(mul_data[key]).getall())

        try:
            product["bought_next"] = self.split_bought(response)
        except Exception as e:
            print("[EXCEPTION]: ", e)

        yield self.save_data(product)

    def get_review_page(self, response):
        pages = 1
        try:
            amount = int(response.xpath('//h2[@class="reviews-list__header"]/text()').get().split(" ")[0])
            if amount>10:
                pages = amount//10
        except Exception as e:
            print("[EXCEPTION]: ", e)

        for page in range(1, pages):
            url = response.request.url+"?active-tab=product-reviews&page={0}#review-data".format(page)
            yield scrapy.Request(url=url, callback=self.split_review)

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
        self.reviews.extend(result)

    def split_bought(self, response):
        result = []
        bought_css = {
            "URL": 'a.jfbLom::attr(href)',
            "title": 'a.jfbLom::text',
            "image": 'img.product-image::attr(src)',
            "price": 'span.value::text',
        }
        
        bought_next = response.xpath('//div[@class="product-tile-wrapper"]')
        for product in bought_next:
            #print("\n", product.css('').getall(), "\n")
            tmp = {}
            for key in bought_css.keys():
                tmp[key] = product.css(bought_css[key]).get()
                if key == "URL":
                    tmp[key] = "https://www.tesco.com"+tmp[key]
            result.append(tmp)

        return result

    def save_data(self, item):
        with open('parsed/data.json', 'r') as file:
            data = json.load(file)
            data['items'].append(item)
        with open('parsed/data.json', 'w') as file:
            json.dump(data, file, indent=4)
