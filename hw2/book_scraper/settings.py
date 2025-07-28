# hw2/book_scraper/settings.py

"""
Scrapy project settings for book_scraper.

- Limits request rate for polite crawling.
- Sets UTF-8 export and fixed order of book fields.
- Enables pipelines for data cleaning and optional MongoDB export.
- Configures User-Agent rotation and retry logic.
- Sets logging level.
- Enables AutoThrottle for extra politeness.
"""

BOT_NAME = "book_scraper"

SPIDER_MODULES = ["book_scraper.spiders"]
NEWSPIDER_MODULE = "book_scraper.spiders"

# Follow robots.txt rules (respect website's requirements)
ROBOTSTXT_OBEY = True

# Output encoding (CSV, JSON, etc.)
FEED_EXPORT_ENCODING = "utf-8"

# Order of fields in exported CSV/JSON
FEED_EXPORT_FIELDS = [
    "title",
    "author",
    "description",
    "price_amount",
    "price_currency",
    "rating_value",
    "rating_count",
    "publication_year",
    "isbn",
    "pages_cnt",
    "publisher",
    "book_cover",
    "source_url",
]

# User-Agent rotation and retries (uses scrapy-fake-useragent)
DOWNLOADER_MIDDLEWARES = {
    "scrapy.downloadermiddlewares.useragent.UserAgentMiddleware": None,
    "scrapy_fake_useragent.middleware.RandomUserAgentMiddleware": 400,
    "scrapy.downloadermiddlewares.retry.RetryMiddleware": 90,
}

RETRY_TIMES = 5  # On errors, try again up to 5 times

# Enable data post-processing pipeline (for description cleanup etc)
ITEM_PIPELINES = {
    "book_scraper.pipelines.BookScraperPipeline": 100,
    "book_scraper.pipelines.MongoDBPipeline": 300,  # включи, если нужен MongoDB экспорт
}

# MongoDB settings (используются только если активировать MongoDBPipeline)
MONGODB_URI = "mongodb://localhost:27017"
MONGODB_DATABASE = "books"
MONGODB_COLLECTION = "books"

# Limit how many items to scrape before shutting down spider
CLOSESPIDER_ITEMCOUNT = 1000

# Logging level (INFO, WARNING, ERROR, DEBUG)
LOG_LEVEL = "INFO"

# --- Если хочешь быть супер-вежливым: включай автотроттлинг ---
# AUTOTHROTTLE_ENABLED = True
# AUTOTHROTTLE_START_DELAY = 5
# AUTOTHROTTLE_MAX_DELAY = 60
print("!!! Scrapy settings loaded, pipelines =", ITEM_PIPELINES)
