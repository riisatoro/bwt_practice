#this is the semantic of the pages that required to parse

#for products.py

GLOBAL_URL = "https://www.tesco.com"

PRODUCTS_URL = '//div[@class="product-details--content"]/h3/a/@href'

SINGLE_DATA = {
    "image": '//img[@class="product-image"]/@src',
    "prod_title": '//h1[@class="product-details-tile__title"]/text()',
    "price": '//span[@data-auto="price-value"]/text()',
    "review_amount":'//h2[@class="reviews-list__header"]/text()',
}

MULTIPLE_DATA = {
    "description": '//div[@id="product-description"]/ul/li/text()',
    "address": '//div[@id="manufacturer-address"]/ul[@class="product-info-block__content"]/li/text()',
    "return": '//div[@id="return-address"]/ul/li/text()',
    "net_contents": '//div[@id="net-contents"]/p/text()',
    "category": '//div[@class="breadcrumbs__content"]/nav/ol/li/div/span/a/span/span/text()',
}

BOUGHT_NEXT_LIST = '//div[@class="product-tile-wrapper"]'

BOUGHT_CSS = {
    "URL": 'a.jfbLom::attr(href)',
    "title": 'a.jfbLom::text',
    "image": 'img.product-image::attr(src)',
    "price": 'span.value::text',
}

#for reviews.py

REVIEW_URL = "?active-tab=product-reviews&page={}#review-data"

REVIEW_DATA = '//article[@class="review"]'

REVIEW_CSS = {
    "title": 'h3.review__summary::text',
    "stars": 'span.czgxkL::text',
    "author": 'span.review-author__nickname::text',
    "date": 'span.review-author__submission-time::text',
    "text": 'p.review__text::text'
}
        