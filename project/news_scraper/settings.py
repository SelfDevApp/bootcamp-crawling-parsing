"""
Scrapy project settings for news_scraper.

- Uses Playwright for rendering dynamic content on kp.ru/online.
- Cleans and normalizes scraped data via pipelines.
- Saves results to MongoDB (primary storage).
- Optionally allows JSONL export by uncommenting FEEDS section.
"""

BOT_NAME = "news_scraper"

SPIDER_MODULES = ["news_scraper.spiders"]
NEWSPIDER_MODULE = "news_scraper.spiders"

# kp.ru robots.txt blocks /online/, so we ignore it
ROBOTSTXT_OBEY = False

# Crawl politeness
DOWNLOAD_DELAY = 1
CONCURRENT_REQUESTS_PER_DOMAIN = 1
DOWNLOAD_TIMEOUT = 30
RETRY_TIMES = 2

# Logging level (INFO for clean output)
LOG_LEVEL = "INFO"

# Output encoding
FEED_EXPORT_ENCODING = "utf-8"

# Uncomment to enable JSONL export (secondary output)
# FEEDS = {
#     "results.jsonl": {
#         "format": "jsonlines",
#         "encoding": "utf8",
#         "store_empty": False,
#     }
# }

# Fixed field order for optional JSONL/CSV export
FEED_EXPORT_FIELDS = [
    "title",
    "description",
    "article_text",
    "publication_datetime",
    "header_photo_url",
    "header_photo_base64",
    "keywords",
    "authors",
    "source_url",
]

# Pipelines for:
# - Normalization & image Base64 encoding
# - MongoDB storage
ITEM_PIPELINES = {
    "news_scraper.pipelines.NewsScraperPipeline": 300,
    "news_scraper.pipelines.MongoDBPipeline": 400,
}

# MongoDB settings
MONGODB_URI = "mongodb://localhost:27017"
MONGODB_DATABASE = "news"
MONGODB_COLLECTION = "articles"

# Playwright integration
DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"

# Browser configuration
PLAYWRIGHT_BROWSER_TYPE = "chromium"
PLAYWRIGHT_MAX_PAGES_PER_CONTEXT = 4
PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT = 60 * 1000  # 60s
PLAYWRIGHT_LAUNCH_OPTIONS = {
    "headless": True,
}

# Default headers to mimic real browser
DEFAULT_REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/119.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ru,en;q=0.9",
}
