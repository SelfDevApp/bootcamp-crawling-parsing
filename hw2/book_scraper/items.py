# hw2/book_scraper/items.py

"""
Defines data structure for scraped book items.
Each field represents a piece of information extracted from chitai-gorod.ru.
"""

import scrapy


class BookScraperItem(scrapy.Item):
    # Title of the book (required)
    title = scrapy.Field()
    # Author of the book (optional)
    author = scrapy.Field()
    # Book description (optional)
    description = scrapy.Field()
    # Price amount (optional)
    price_amount = scrapy.Field()
    # Price currency (optional)
    price_currency = scrapy.Field()
    # Average rating (optional)
    rating_value = scrapy.Field()
    # Number of ratings (optional)
    rating_count = scrapy.Field()
    # Year of publication (required)
    publication_year = scrapy.Field()
    # ISBN number (required)
    isbn = scrapy.Field()
    # Number of pages (required)
    pages_cnt = scrapy.Field()
    # Publisher (optional)
    publisher = scrapy.Field()
    # Book cover image URL (optional)
    book_cover = scrapy.Field()
    # Source page URL (required, link to the book page)
    source_url = scrapy.Field()
