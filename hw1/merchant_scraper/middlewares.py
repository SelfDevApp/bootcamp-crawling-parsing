# hw1/merchant_scraper/merchant_scraper/middlewares.py

"""
Custom middlewares for merchant_scraper project.

Currently, these middlewares don't add any custom logic — all methods are default stubs.
You can use these classes as a template to add request/response modification or logging in the future.
"""

from scrapy import signals


class MerchantScraperSpiderMiddleware:
    """Default spider middleware (no custom logic, just logs spider open)."""

    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        return None

    def process_spider_output(self, response, result, spider):
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        pass

    def spider_opened(self, spider):
        spider.logger.info(f"Spider opened: {spider.name}")


class MerchantScraperDownloaderMiddleware:
    """Default downloader middleware (no custom logic, just logs spider open)."""

    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        return None

    def process_response(self, request, response, spider):
        return response

    def process_exception(self, request, exception, spider):
        pass

    def spider_opened(self, spider):
        spider.logger.info(f"Spider opened: {spider.name}")
