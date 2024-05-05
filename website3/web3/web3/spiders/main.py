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
    name = "traderjoes"
    start_urls = ['https://www.traderjoes.com']

    def start_requests(self):
        url = "https://www.traderjoes.com/api/graphql"
        jdata = self.get_json_data(page=1)
        yield scrapy.Request(
            url=url,
            method="POST",
            body=json.dumps(jdata),
            headers=self.get_headers(),
            callback=self.parse,
            meta={
                "page": 1
            })

    def parse(self, response):
        data = response.json()
        items = data.get("data", {}).get("products", {}).get("items", {})
        if not items:
            logger.error("No data Found. Graphql Request failed!!!")
        else:
            for item in items:
                sku = item.get('sku')
                headers = self.get_headers()
                headers['referer'] = f"https://www.traderjoes.com/home/products/pdp/{sku}"
                yield scrapy.Request(
                    'https://www.traderjoes.com/api/graphql',
                    body=json.dumps(self.get_product_jdata(sku)),
                    method="POST",
                    headers=headers,
                    callback=self.parse_pdp
                )
            # break
        total_pages = data.get("data").get("products").get(
            "pageInfo").get("totalPages")
        current_page = response.meta.get("page")+1
        if current_page <= total_pages:
            logger.info(
                f"Paginating listing [Page:{current_page}/{total_pages}]")
            url = "https://www.traderjoes.com/api/graphql"
            jdata = self.get_json_data(page=current_page)
            yield scrapy.Request(
                url=url,
                body=json.dumps(jdata),
                method="POST",
                headers=self.get_headers(),
                callback=self.parse,
                meta={
                    "page": current_page
                })

    def parse_pdp(self, response):
        data = response.json()
        pdp_data_full = data.get("data").get("products").get("items")
        yield ProductData(**{
            "data": pdp_data_full
        })

    def get_product_jdata(self, sku):
        json_data = {
            'operationName': 'SearchProduct',
            'variables': {
                'storeCode': 'TJ',
                'published': '1',
                'sku': sku,
            },
            'query': 'query SearchProduct($sku: String, $storeCode: String = "TJ", $published: String = "1") {\n  products(\n    filter: {sku: {eq: $sku}, store_code: {eq: $storeCode}, published: {eq: $published}}\n  ) {\n    items {\n      category_hierarchy {\n        id\n        url_key\n        description\n        name\n        position\n        level\n        created_at\n        updated_at\n        product_count\n        __typename\n      }\n      item_story_marketing\n      product_label\n      fun_tags\n      primary_image\n      primary_image_meta {\n        url\n        metadata\n        __typename\n      }\n      other_images\n      other_images_meta {\n        url\n        metadata\n        __typename\n      }\n      context_image\n      context_image_meta {\n        url\n        metadata\n        __typename\n      }\n      published\n      sku\n      url_key\n      name\n      item_description\n      item_title\n      item_characteristics\n      item_story_qil\n      use_and_demo\n      sales_size\n      sales_uom_code\n      sales_uom_description\n      country_of_origin\n      availability\n      new_product\n      promotion\n      price_range {\n        minimum_price {\n          final_price {\n            currency\n            value\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      retail_price\n      nutrition {\n        display_sequence\n        panel_id\n        panel_title\n        serving_size\n        calories_per_serving\n        servings_per_container\n        details {\n          display_seq\n          nutritional_item\n          amount\n          percent_dv\n          __typename\n        }\n        __typename\n      }\n      ingredients {\n        display_sequence\n        ingredient\n        __typename\n      }\n      allergens {\n        display_sequence\n        ingredient\n        __typename\n      }\n      created_at\n      first_published_date\n      last_published_date\n      updated_at\n      related_products {\n        sku\n        item_title\n        primary_image\n        primary_image_meta {\n          url\n          metadata\n          __typename\n        }\n        price_range {\n          minimum_price {\n            final_price {\n              currency\n              value\n              __typename\n            }\n            __typename\n          }\n          __typename\n        }\n        retail_price\n        sales_size\n        sales_uom_description\n        category_hierarchy {\n          id\n          name\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    total_count\n    page_info {\n      current_page\n      page_size\n      total_pages\n      __typename\n    }\n    __typename\n  }\n}\n',
        }
        return json_data

    def get_json_data(self, page):
        json_data = {
            'operationName': 'SearchProducts',
            'variables': {
                'storeCode': 'TJ',
                'availability': '1',
                'published': '1',
                'categoryId': 2,
                'currentPage': page,
                'pageSize': 1000,
            },
            'query': 'query SearchProducts($categoryId: String, $currentPage: Int, $pageSize: Int, $storeCode: String = "TJ", $availability: String = "1", $published: String = "1") {\n  products(\n    filter: {store_code: {eq: $storeCode}, published: {eq: $published}, availability: {match: $availability}, category_id: {eq: $categoryId}}\n    currentPage: $currentPage\n    pageSize: $pageSize\n  ) {\n    items {\n      sku\n      item_title\n      category_hierarchy {\n        id\n        name\n        __typename\n      }\n      primary_image\n      primary_image_meta {\n        url\n        metadata\n        __typename\n      }\n      sales_size\n      sales_uom_description\n      price_range {\n        minimum_price {\n          final_price {\n            currency\n            value\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      retail_price\n      fun_tags\n      item_characteristics\n      __typename\n    }\n    total_count\n    pageInfo: page_info {\n      currentPage: current_page\n      totalPages: total_pages\n      __typename\n    }\n    aggregations {\n      attribute_code\n      label\n      count\n      options {\n        label\n        value\n        count\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n',
        }
        return json_data

    def get_headers(self):
        headers = {
            'accept': '*/*',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'content-type': 'application/json',
            'origin': 'https://www.traderjoes.com',
            'priority': 'u=1, i',
            # 'referer': 'https://www.traderjoes.com/home/products/category/food-8',
            'sec-ch-ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Linux"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        }
        return headers
