# hw2/book_scraper/spiders/chitai_gorod_sitemap.py

"""
Spider for extracting book data from chitai-gorod.ru using their sitemap.

- Uses Scrapy's SitemapSpider for efficient crawling.
- Parses book detail pages and extracts all relevant fields.
- Applies custom headers to mimic real browser requests.
"""

import scrapy
from scrapy.spiders import SitemapSpider
from book_scraper.items import BookScraperItem
import re


class ChitaiGorodSitemapSpider(SitemapSpider):
    # Spider name (run with: scrapy crawl chitai_gorod_sitemap)
    name = "chitai_gorod_sitemap"
    allowed_domains = ["chitai-gorod.ru"]
    sitemap_urls = ["https://www.chitai-gorod.ru/sitemap.xml"]
    sitemap_rules = [("/product/", "parse")]

    # Custom browser-like headers for requests
    custom_headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0 Safari/537.36"
        ),
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://www.chitai-gorod.ru/",
    }

    def start_requests(self):
        """
        Initial request for the sitemap, uses custom headers.
        """
        for url in self.sitemap_urls:
            yield scrapy.Request(
                url=url,
                headers=self.custom_headers,
                callback=self._parse_sitemap,
                dont_filter=True,
            )

    def _requests_to_follow(self, response):
        """
        For every URL found in the sitemap, attach custom headers.
        """
        for req in super()._requests_to_follow(response):
            req = req.replace(headers=self.custom_headers)
            yield req

    def extract_cover_url(self, response):
        """
        Extracts the book cover image URL:
        1. Tries to find <img> tag inside the main image container.
        2. If not found, tries to extract from inline style on a preview button.
        """
        img_url = response.xpath(
            '//div[contains(@class,"product-detail-page_media")]//img/@src'
        ).get()
        if img_url:
            return img_url

        style = response.xpath(
            "//button[contains(@class, 'product-preview__button')]/@style"
        ).get()
        if style:
            m = re.search(r"url\(['\"]?(https?://[^\)'\"]+)", style)
            if m:
                return m.group(1)
        return None

    def parse(self, response):
        """
        Main parsing function: extracts all book fields from the product page.
        """
        self.logger.info(f"Parsing book page: {response.url}")
        item = BookScraperItem()

        # --- Title ---
        item["title"] = response.xpath("//h1[@itemprop='name']/text()").get(
            default=None
        )

        # --- Authors (comma-separated from meta tags) ---
        authors = response.xpath(
            '//ul[@class="product-authors"]//meta[@itemprop="name"]/@content'
        ).getall()
        item["author"] = ", ".join(authors) if authors else None

        # --- Description (as list of text blocks for the pipeline) ---
        desc = response.xpath(
            "//article[contains(@class,'product-detail-page__detail-text')]//text()"
        ).getall()
        item["description"] = desc if desc else None

        # --- Price (digits only, currency if available) ---
        price_text = response.xpath(
            "//span[contains(@class,'product-offer-price__actual')]/text()"
        ).get()
        price = None
        if price_text:
            price = "".join(filter(str.isdigit, price_text))
        item["price_amount"] = price if price else None
        item["price_currency"] = "₽" if price else None

        # --- Rating (average and count, if available) ---
        item["rating_value"] = response.xpath(
            "//span[@itemprop='ratingValue']/text()"
        ).get(default=None)
        item["rating_count"] = response.xpath(
            "//span[@itemprop='ratingCount']/text()"
        ).get(default=None)

        # --- Helper function for product properties by name ---
        def get_prop(prop):
            return response.xpath(
                f'//ul[@class="product-properties"]/li[span[@class="product-properties-item__title" and contains(text(),"{prop}")]]/span[@class="product-properties-item__content"]//span/text()'
            ).get()

        # --- Publication year, ISBN, page count, publisher ---
        item["publication_year"] = get_prop("Год издания") or None
        item["isbn"] = response.xpath('//span[@itemprop="isbn"]/span/text()').get(
            default=None
        )
        item["pages_cnt"] = response.xpath(
            '//span[@itemprop="numberOfPages"]/span/text()'
        ).get(default=None)
        item["publisher"] = response.xpath(
            '//span[@itemprop="publisher"]/a/text() | //span[@itemprop="publisher"]/text()'
        ).get(default=None)

        # --- Book cover URL ---
        item["book_cover"] = self.extract_cover_url(response)

        # --- Source page URL ---
        item["source_url"] = response.url

        yield item
