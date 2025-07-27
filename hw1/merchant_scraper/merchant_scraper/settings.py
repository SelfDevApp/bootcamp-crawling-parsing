# hw1/merchant_scraper/merchant_scraper/settings.py

"""
Scrapy project settings for merchant_scraper.

- Configures User-Agent rotation and retry logic for stable scraping.
- Limits request rate for polite crawling.
- Sets UTF-8 export, CSV column order, and pipeline activation.
"""

BOT_NAME = "merchant_scraper"

SPIDER_MODULES = ["merchant_scraper.spiders"]
NEWSPIDER_MODULE = "merchant_scraper.spiders"

# Follow robots.txt rules (respect website rules)
ROBOTSTXT_OBEY = True

# Control request rate (no ban, no DDOS)
CONCURRENT_REQUESTS_PER_DOMAIN = 1
DOWNLOAD_DELAY = 1

# Output encoding (CSV, etc.)
FEED_EXPORT_ENCODING = "utf-8"

# Order of fields in exported CSV
FEED_EXPORT_FIELDS = [
    "merchant_name",
    "mcc",
    "address",
    "geo_coordinates",
    "org_name",
    "org_description",
    "website",
    "source_url",
]

# Enable middlewares for User-Agent rotation and retries
DOWNLOADER_MIDDLEWARES = {
    "scrapy.downloadermiddlewares.useragent.UserAgentMiddleware": None,
    "scrapy_fake_useragent.middleware.RandomUserAgentMiddleware": 400,
    "scrapy.downloadermiddlewares.retry.RetryMiddleware": 90,
}

# Retry settings (handle blocks/timeouts)
RETRY_TIMES = 5

# Enable the data cleaning pipeline
ITEM_PIPELINES = {
    "merchant_scraper.pipelines.MerchantScraperPipeline": 300,
}

# Limit how many items to scrape before stopping the spider (auto-shutdown when reached)
CLOSESPIDER_ITEMCOUNT = 1000
