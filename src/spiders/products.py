import scrapy
import json


class Products(scrapy.Spider):
	"""docs"""
	name = "products"
	start_urls = [
		'https://www.tesco.com/groceries/en-GB/shop/household/kitchen-roll-and-tissues/all'
	]

	def parse(self, response):
		products = response.css('a.sc-cSHVUG::attr(href)').getall()
		for url in products:
			yield scrapy.Request(url="https://www.tesco.com"+url, callback=self.split_data)

	def split_data(self, response):
		data = {
			"image_url": '//img[@class="product-image"]/@src',
			"prod_title": '//h1[@class="product-details-tile__title"]/text()',
			"price": '//span[@data-auto="price-value"]/text()',
		}

		product = {}
		product["prod_URL"] = response.url
		product["prod_ID"] = int(response.url.split("/")[-1])
		product["description"] = '. '\
			.join(response\
				.xpath('//li[@class="product-info-block__content-item"]/text()')\
				.getall())

		for key in data.keys():
			product[key] = response.xpath(data[key]).get()

		yield self.save_data(product)

	def save_data(self, item):
		with open('parsed/data.json', 'r') as file:
			data = json.load(file)
			data['items'].append(item)
		with open('parsed/data.json', 'w') as file:
			json.dump(data, file, indent=4)
		

	