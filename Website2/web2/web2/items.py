# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ProductData(scrapy.Item):
    # define the fields for your item here like:
    sku = scrapy.Field()
    name = scrapy.Field()
    url = scrapy.Field()
    image = scrapy.Field()
    price = scrapy.Field()
    description = scrapy.Field()
    response_url = scrapy.Field()
