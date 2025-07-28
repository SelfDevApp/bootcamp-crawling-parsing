# hw1/merchant_scraper/spiders/merchants_spider.py

"""
Main spider for merchant_scraper project.

- Collects links to all brand pages from https://merchantpoint.ru/brands (follows all pages via "Далее" button).
- For each brand, extracts:
    - org_name: Brand name from <h1>
    - org_description: Description text from .description_brand
    - mcc, merchant_name, address: Parsed from the table with MCC codes (3 columns, merged via comma if multiple)
    - website: Parsed from "Сайт" block or first link in description
    - source_url: URL of the brand page
- Yields MerchantScraperItem for every brand found.
"""

import scrapy
from merchant_scraper.items import MerchantScraperItem
import re


class MerchantsSpider(scrapy.Spider):
    name = "merchants"
    allowed_domains = ["merchantpoint.ru"]
    start_urls = ["https://merchantpoint.ru/brands"]

    custom_headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0 Safari/537.36"
        ),
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://merchantpoint.ru/",
    }

    def start_requests(self):
        yield scrapy.Request(
            url=self.start_urls[0],
            headers=self.custom_headers,
            callback=self.parse,
            dont_filter=True,
        )

    def parse(self, response):
        self.logger.info(f"Parsing page: {response.url}")

        # 1. Собираем ссылки на бренды на странице
        for link in response.xpath("//a[contains(@href, '/brand/')]/@href").getall():
            yield response.follow(
                link,
                headers=self.custom_headers,
                callback=self.parse_org,
                dont_filter=True,
            )

        # 2. Переходим на следующую страницу, если есть кнопка "Далее"
        next_page = response.xpath("//a[contains(text(), 'Далее')]/@href").get()
        if next_page:
            yield response.follow(
                next_page,
                headers=self.custom_headers,
                callback=self.parse,
                dont_filter=True,
            )

    def parse_org(self, response):
        item = MerchantScraperItem()
        item["org_name"] = response.xpath("//h1/text()").get(default="").strip()

        # Описание только из блока description_brand
        description_text = " ".join(
            response.css("div.description_brand *::text").getall()
        ).strip()
        item["org_description"] = description_text

        # --- MCC, merchant_name и address из таблицы ---
        mcc_set = set()
        merchant_set = set()
        address_set = set()
        for row in response.css("table.finance-table tbody tr"):
            mcc = row.css("td:nth-child(1)::text").get()
            name = row.css("td:nth-child(2) a::text, td:nth-child(2)::text").get()
            address = row.css("td:nth-child(3)::text").get()
            if mcc:
                mcc_set.add(mcc.strip())
            if name:
                merchant_set.add(name.strip())
            if address:
                address_set.add(address.strip())
        item["mcc"] = ",".join(sorted(mcc_set)) if mcc_set else None
        item["merchant_name"] = ",".join(sorted(merchant_set)) if merchant_set else None
        item["address"] = ",".join(sorted(address_set)) if address_set else None

        # --- Website из блока "Сайт — ..." ---
        website_block = response.xpath(
            "//section[@id='description']//p[contains(text(), 'Сайт')]"
        )
        website = None
        if website_block:
            website_text = website_block.xpath("text()").get("")
            match = re.search(r'https?://[^\s,"]+', website_text)
            if match:
                website = match.group(0)
        # Fallback: первая явная ссылка
        if not website:
            website = response.xpath(
                "//section[@id='description']//a[contains(@href,'http')]/@href"
            ).get(default="")
        item["website"] = website.strip() if website else None

        item["source_url"] = response.url

        # Остальные поля
        item["geo_coordinates"] = None

        yield item
