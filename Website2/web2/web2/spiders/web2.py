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
    name = "lechocolat"
    # using sitemap to get the product links
    start_urls = ['https://www.lechocolat-alainducasse.com/uk/sitemap']

    def parse(self, response):
        parser = Selector(text=response.text)
        lis = parser.xpath(
            '//h2[contains(text(),"Categories")]//ancestor::section//li//li')
        # categories_sitemap = []
        for cat in lis:
            # data = {}
            # name = cat.xpath('.//a/@title').getall()
            category_url = cat.xpath('.//a/@href').getall()
            if len(category_url) > 1:
                continue
            # categories_sitemap.append(data)
            yield response.follow(
                clean(category_url),
                headers=self.get_headers(),
                callback=self.parse_category
            )
            # break

    def parse_category(self, response):
        parser = Selector(response.text)
        prod_list_section = parser.xpath(
            '//section[@class="productMiniature__data"]')
        # prod_data = []
        for prod in prod_list_section:
            # data = {}
            # name = prod.xpath(
            #     './/a/h2[@class="productMiniature__title product-title"]//text()').getall()
            prod_url = prod.xpath('.//a/@href').getall()
            # name = clean(name)
            prod_url = clean(prod_url)
            # prod_data.append(data)
            yield response.follow(
                prod_url,
                headers=self.get_headers(referer=response.url),
                callback=self.parse_product
            )
            # break

    def parse_product(self, response):
        parser = Selector(response.text)
        scripts_data = parser.xpath(
            '//script[@type="application/ld+json"]//text()').getall()
        data = None
        for script in scripts_data:
            script = json.loads(script)
            print(script.get("@type"))
            if script.get("@type") == "Product":
                data = script
        if not data:
            logger.warning(f"no product data found [url:{response.url}]")
        else:
            sku = clean(data.get("sku"))
            name = clean(data.get("name"))
            url = clean(data.get("url"))
            image = clean(data.get("image"))
            price = f'{data.get("offers").get("priceCurrency")} {data.get("offers").get("price")}'
            description = self.get_description(parser)
            response_url = response.url
            yield ProductData(**{
                "sku": sku,
                "name": name,
                "url": url,
                "image": image,
                "price": price,
                "description": description,
                "response_url": response_url
            })

    def get_description(self, parser):
        raw_text = parser.xpath(
            '//div[contains(@class, "productAccordion__content")]//text()').getall()
        text = " | ".join([clean(value) for value in raw_text if clean(value)])
        return text

    def get_variants(self, data):
        """pares data to get the variants"""
        variants_data = []
        offers = data.get("offers")
        for offer in offers:
            variant_data = {
                "name": clean(offer.get("itemOffered").get("name")),
                "variant_url": clean(offer.get("itemOffered").get("url")),
                "variant_price": f'{offer.get("priceCurrency")} {offer.get("price")}',
                "availability": clean(offer.get("availability").split("/")[-1]),
                "weight": offer.get("itemOffered").get("weight").get("value")
            }
            variants_data.append(variant_data)
        return variants_data

    def get_headers(self, referer=None):
        header = {
            'authority': 'www.lechocolat-alainducasse.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'sec-ch-ua': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        }
        if referer:
            header['referer'] = referer
        return header


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
