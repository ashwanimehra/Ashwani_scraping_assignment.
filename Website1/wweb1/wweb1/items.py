# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ProductData(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    brand = scrapy.Field()
    description = scrapy.Field()
    image = scrapy.Field()
    images = scrapy.Field()
    models = scrapy.Field()
    price = scrapy.Field()
    prices = scrapy.Field()
    product_id = scrapy.Field()
    sale_prices = scrapy.Field()
    title = scrapy.Field()
    url = scrapy.Field()
    raw_data = scrapy.Field()


class NoData(scrapy.Item):
    url = scrapy.Field()
