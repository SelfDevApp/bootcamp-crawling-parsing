# project/news_scraper/items.py

"""
Defines data structure for scraped news articles.
Each field represents a piece of information extracted from kp.ru/online.
"""

import scrapy


class NewsScraperItem(scrapy.Item):
    # Title of the article (required)
    title = scrapy.Field()
    # Short description or subtitle (required)
    description = scrapy.Field()
    # Full article text (required)
    article_text = scrapy.Field()
    # Publication date and time (required, ISO format preferred)
    publication_datetime = scrapy.Field()
    # URL of the article's header photo (optional)
    header_photo_url = scrapy.Field()
    # Base64-encoded header photo (optional)
    header_photo_base64 = scrapy.Field()
    # Article keywords/tags (required)
    keywords = scrapy.Field()
    # Author(s) of the article (required)
    authors = scrapy.Field()
    # Source page URL (required, link to the article)
    source_url = scrapy.Field()
