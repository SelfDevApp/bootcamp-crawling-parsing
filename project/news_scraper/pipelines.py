"""
Pipelines for news_scraper.

Tasks:
- Normalize fields: title, article_text, authors
- Convert publication_datetime to ISO 8601 format
- Download header image and encode as Base64
- Save items into MongoDB (if enabled)
"""

import base64
import requests
from datetime import datetime
from itemadapter import ItemAdapter
import pymongo


class NewsScraperPipeline:
    """Pipeline for cleaning and normalizing scraped data."""

    # Mapping of Russian month names to numeric values
    MONTHS = {
        "января": "01",
        "февраля": "02",
        "марта": "03",
        "апреля": "04",
        "мая": "05",
        "июня": "06",
        "июля": "07",
        "августа": "08",
        "сентября": "09",
        "октября": "10",
        "ноября": "11",
        "декабря": "12",
    }

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        # --- Normalize title ---
        title = adapter.get("title")
        if isinstance(title, list):
            adapter["title"] = " ".join([t.strip() for t in title if t.strip()])
        elif isinstance(title, str):
            adapter["title"] = " ".join(title.split())

        # --- Normalize article_text ---
        text = adapter.get("article_text")
        if isinstance(text, list):
            adapter["article_text"] = " ".join([t.strip() for t in text if t.strip()])
        elif isinstance(text, str):
            adapter["article_text"] = " ".join(text.split())

        # --- Normalize authors ---
        authors = adapter.get("authors")
        if isinstance(authors, list):
            adapter["authors"] = ", ".join([a.strip() for a in authors if a.strip()])

        # --- Convert publication_datetime to ISO 8601 ---
        pub_dt = adapter.get("publication_datetime")
        if pub_dt:
            try:
                parts = pub_dt.split()
                if len(parts) >= 4:
                    day = parts[0].zfill(2)
                    month = self.MONTHS.get(parts[1].lower(), "01")
                    year = parts[2]
                    time = parts[3]
                    iso_date = f"{year}-{month}-{day}T{time}:00"
                    adapter["publication_datetime"] = iso_date
                else:
                    spider.logger.warning(f"Unexpected date format: {pub_dt}")
            except Exception as e:
                spider.logger.warning(f"Failed to parse date '{pub_dt}': {e}")

        # --- Download and encode header image as Base64 ---
        img_url = adapter.get("header_photo_url")
        if img_url:
            try:
                response = requests.get(img_url, timeout=10)
                response.raise_for_status()
                adapter["header_photo_base64"] = base64.b64encode(
                    response.content
                ).decode("utf-8")
            except requests.RequestException as e:
                spider.logger.warning(f"Failed to download image {img_url}: {e}")
                adapter["header_photo_base64"] = None

        return item


class MongoDBPipeline:
    """Pipeline to save news items into MongoDB."""

    def __init__(self, mongodb_uri, mongodb_db, mongodb_collection):
        self.mongodb_uri = mongodb_uri
        self.mongodb_db = mongodb_db
        self.mongodb_collection = mongodb_collection

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongodb_uri=crawler.settings.get(
                "MONGODB_URI", "mongodb://localhost:27017"
            ),
            mongodb_db=crawler.settings.get("MONGODB_DATABASE", "news"),
            mongodb_collection=crawler.settings.get("MONGODB_COLLECTION", "articles"),
        )

    def open_spider(self, spider):
        spider.logger.info("[MongoDBPipeline] Connecting to MongoDB...")
        self.client = pymongo.MongoClient(self.mongodb_uri)
        self.db = self.client[self.mongodb_db]
        self.collection = self.db[self.mongodb_collection]

    def close_spider(self, spider):
        spider.logger.info("[MongoDBPipeline] Closing MongoDB connection.")
        self.client.close()

    def process_item(self, item, spider):
        data = ItemAdapter(item).asdict()
        spider.logger.info(f"[MongoDBPipeline] Saving article: {data.get('title')}")
        self.collection.update_one(
            {"source_url": data.get("source_url")}, {"$set": data}, upsert=True
        )
        return item
