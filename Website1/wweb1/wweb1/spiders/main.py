import scrapy
# import requests
from parsel import Selector
import json
from ..items import ProductData
import logging

logging.basicConfig(
    filename='web1.log', 
    level=logging.INFO,
    format="%(asctime)s [%(name)s]%(levelname)s:%(message)s"
    )
logger = logging.getLogger(__name__)


class Spider(scrapy.Spider):
    name = "foreignfortune_com"
    # start_url = "https://foreignfortune.com"
    # using sitemap to get all the product links
    start_urls = ["https://foreignfortune.com/sitemap.xml"]

    def parse(self, response):
        parser = Selector(text=response.text)
        locs = parser.xpath("//loc/text()").getall()
        for loc in locs:
            if "sitemap_products" in loc:
                sitemap_url = loc
        yield response.follow(
            sitemap_url,
            headers=self.get_headers(type="sitemap"),
            callback=self.parse_sitemap_products
        )

    def parse_sitemap_products(self, response):
        parser = Selector(response.text)
        products = parser.xpath("//url/loc/text()").getall()
        for product in products:
            if product == "https://foreignfortune.com/":
                continue
            yield response.follow(
                product,
                headers=self.get_headers(type="product_header"),
                callback=self.parse_products
                )

    def parse_products(self, response):
        parser = Selector(response.text)
        scripts_data = parser.xpath('//script[@type="application/ld+json"]//text()').getall()
        data = None
        for script in scripts_data:
            script = json.loads(script)
            print(script.get("@type"))
            if script.get("@type") == "Product":
                data = script
        if not data:
            logger.warning(f"no product data found [url:{response.url}]")
        else:
            yield ProductData(**{
                "name": clean(data.get("name")),
                "brand": clean(data.get("brand", {}).get("name")),
                "description": clean(data.get("description")),
                "image": clean(data.get("image")),
                "images": self.get_all_images(parser),
                "models": self.get_models(data),
                "price": clean(parser.xpath('//span[@id="ProductPrice-product-template"]//text()').getall()),
                "product_id": clean(data.get("url").split("/")[-1]),
                "sale_prices": [],
                "title": clean(data.get("name")),
                "url": response.url,
                "raw_data": data
            })
    
    def get_all_images(self, parser):
        imgs = parser.xpath('//img[contains(@id, "FeaturedImage-product-template")]//@src').getall()
        data = []
        for img in imgs:
            if clean(img):
                img = clean(img).replace("//", "https://www.")
                data.append(img)
        return data

    def get_models(self, data):
        """pares data to get the models"""
        models_data = []
        offers = data.get("offers")
        for offer in offers:
            model_data = {
                "name": clean(offer.get("itemOffered").get("name")),
                "model_url":clean(offer.get("itemOffered").get("url")),
                "model_price":f'{offer.get("priceCurrency")} {offer.get("price")}',
                "availability": clean(offer.get("availability").split("/")[-1]),
                "weight": offer.get("itemOffered").get("weight").get("value")
            }
            models_data.append(model_data)
        return models_data

    def get_headers(self, type):
        header_dict = {
            "sitemap": {
                'authority': 'foreignfortune.com',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
                'cache-control': 'max-age=0',
                'if-none-match': '"cacheable:a07d6f6181aeb133c965c0f3bc98cf1d"',
                'sec-ch-ua': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'cross-site',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
            },
            "product_header": {
                'authority': 'foreignfortune.com',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
                'cache-control': 'no-cache',
                'pragma': 'no-cache',
                # 'referer': 'https://colab.research.google.com/',
                'sec-ch-ua': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'cross-site',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
            }
        }
        headers = header_dict[type]
        return headers


def clean(dirty):
    """
    Cleans extra spaces from string, list and dict values.
    """
    if isinstance(dirty, list):
        return " ".join(" ".join(dirty).split())
    elif isinstance(dirty, str):
        cleaned_string = "".join(" ".join(dirty.split()))
        return cleaned_string if cleaned_string else None
    elif isinstance(dirty, (float, int, bool)):
        return dirty
    elif isinstance(dirty, dict):
        clean_dict = {key: clean(value) for key, value in dirty.items()}
        return clean_dict
    else:
        return None
