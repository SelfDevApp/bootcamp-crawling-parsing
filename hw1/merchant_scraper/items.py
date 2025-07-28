# hw1/merchant_scraper/items.py

"""
Defines data structure for scraped items.
Each field represents a piece of information extracted from merchantpoint.ru.
"""

import scrapy


class MerchantScraperItem(scrapy.Item):
    # Merchant names (from external table, may be multiple, comma-separated)
    merchant_name = scrapy.Field()
    # MCC codes (from external table, may be multiple, comma-separated)
    mcc = scrapy.Field()
    # Address of the merchant's physical location (optional, from external table)
    address = scrapy.Field()
    # Geographical coordinates (currently unavailable)
    geo_coordinates = scrapy.Field()
    # Organization name (brand name from site)
    org_name = scrapy.Field()
    # Organization description (short text about the brand from site)
    org_description = scrapy.Field()
    # Official website (from brand page)
    website = scrapy.Field()
    # Source page URL (brand page)
    source_url = scrapy.Field()
