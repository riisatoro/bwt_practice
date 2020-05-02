import scrapy 
import json



class Review(scrapy.Spider):
    name = 'reviews'

    def start_requests(self):
        with open('parsed/data.json', 'r') as file:
            products = json.load(file)["items"]

        for product in products:
            for page in range(1, product["review_amount"]):
                url = product["URL"]+"?active-tab=product-reviews&page={}#review-data".format(page)
                yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
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