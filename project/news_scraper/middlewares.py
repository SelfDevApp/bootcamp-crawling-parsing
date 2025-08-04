# project/news_scraper/middlewares.py

"""
Custom middlewares for the news_scraper project.

Currently, no custom logic is implemented.
These stubs can be extended for:
- Adding custom headers
- Proxy rotation
- Error handling
- Request/response transformations
"""

from scrapy import signals


class NewsScraperSpiderMiddleware:
    """Spider middleware (currently not in use)."""

    @classmethod
    def from_crawler(cls, crawler):
        return cls()

    def process_spider_output(self, response, result, spider):
        # Simply pass through results
        for item in result:
            yield item


class NewsScraperDownloaderMiddleware:
    """Downloader middleware (currently not in use)."""

    @classmethod
    def from_crawler(cls, crawler):
        return cls()

    def process_response(self, request, response, spider):
        # Simply return response as is
        return response
