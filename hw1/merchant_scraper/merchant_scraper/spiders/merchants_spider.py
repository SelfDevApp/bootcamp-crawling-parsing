# hw1/merchant_scraper/merchant_scraper/spiders/merchants_spider.py

import scrapy
from merchant_scraper.items import MerchantScraperItem


class MerchantsSpider(scrapy.Spider):
    name = "merchants"
    allowed_domains = ["merchantpoint.ru"]
    start_urls = ["https://merchantpoint.ru/brands"]

    def parse(self, response):
        for link in response.xpath("//a[contains(@href, '/brand/')]/@href").getall():
            yield response.follow(link, callback=self.parse_org)

    def parse_org(self, response):
        item = MerchantScraperItem()
        item["org_name"] = response.xpath("//h1/text()").get()
        item["org_description"] = response.xpath(
            "//div[contains(@class,'description-block')]/p/text()"
        ).get()
        item["source_url"] = response.url

        # Поскольку торговые точки недоступны — устанавливаем эти поля в None
        item["merchant_name"] = None
        item["mcc"] = None
        item["address"] = None
        item["geo_coordinates"] = None

        yield item
