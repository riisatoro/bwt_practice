import scrapy


class Quotes(scrapy.Spider):
	"""docstring for Quotes"""
	
	name = "test"
	start_urls = [
			'http://quotes.toscrape.com/page/1/',
            'http://quotes.toscrape.com/page/2/',
		]

	'''
	#can be used to generate a special links from the common
	def start_requests(self):
		urls = [
			'http://quotes.toscrape.com/page/1/',
            'http://quotes.toscrape.com/page/2/',
		]

		for url in urls:
			#called a self.parse foo a few times with urls
			yield scrapy.Request(url=url, callback=self.parse)
	'''

	def parse(self, responce):
		#recieve page number from url ...com/page/1/
		page = responce.url.split("/")[-2]

		#creating a filename
		filename = 'quotes-%s.html' % page

		#responce is the main source of the page
		#save BODY of the file from request
		with open(filename, 'wb') as file:
			file.write(responce.body)

		#log to console
		self.log("Saved file %s" % filename)
