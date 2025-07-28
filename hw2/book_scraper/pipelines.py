# hw2/book_scraper/pipelines.py

"""
Pipeline for post-processing items and saving to MongoDB (if needed).
"""

from itemadapter import ItemAdapter
import pymongo
import re


class BookScraperPipeline:
    """Cleans up item fields, types, and strings."""

    INT_FIELDS = ["price_amount", "rating_count", "publication_year", "pages_cnt"]
    FLOAT_FIELDS = ["rating_value"]

    STR_FIELDS = [
        "title",
        "author",
        "description",
        "price_currency",
        "isbn",
        "publisher",
        "book_cover",
        "source_url",
    ]

    def process_item(self, item, spider):
        # Clean up description
        desc = item.get("description")
        if isinstance(desc, list):
            desc_clean = [x.strip() for x in desc if x.strip()]
            item["description"] = " ".join(desc_clean) if desc_clean else ""
        elif desc is None:
            item["description"] = ""
        else:
            item["description"] = str(desc)

        # Parse rating_count
        rc_val = item.get("rating_count", 0)
        if isinstance(rc_val, str):
            match = re.search(r"\d+", rc_val)
            if match:
                item["rating_count"] = int(match.group())
            else:
                item["rating_count"] = 0
        else:
            try:
                item["rating_count"] = int(rc_val)
            except (TypeError, ValueError):
                item["rating_count"] = 0

        # Int fields (except rating_count)
        for field in self.INT_FIELDS:
            if field == "rating_count":
                continue
            val = item.get(field, None)
            try:
                item[field] = int(val)
            except (TypeError, ValueError):
                item[field] = 0

        # Float fields
        for field in self.FLOAT_FIELDS:
            val = item.get(field, None)
            try:
                item[field] = float(str(val).replace(",", "."))
            except (TypeError, ValueError):
                item[field] = 0.0

        # String fields
        for field in self.STR_FIELDS:
            val = item.get(field, "")
            if val is None:
                item[field] = ""
            else:
                item[field] = str(val)

        # Debug print for pipeline pass-through
        print(
            f"[BookScraperPipeline] Processed item: {item.get('title')}, ISBN: {item.get('isbn')}"
        )
        return item


class MongoDBPipeline:
    """Pipeline to save items into MongoDB."""

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
            mongodb_db=crawler.settings.get("MONGODB_DATABASE", "books"),
            mongodb_collection=crawler.settings.get("MONGODB_COLLECTION", "books"),
        )

    def open_spider(self, spider):
        print("[MongoDBPipeline] Connecting to MongoDB...")
        self.client = pymongo.MongoClient(self.mongodb_uri)
        self.db = self.client[self.mongodb_db]
        self.collection = self.db[self.mongodb_collection]

    def close_spider(self, spider):
        print("[MongoDBPipeline] Closing MongoDB connection.")
        self.client.close()

    def process_item(self, item, spider):
        data = ItemAdapter(item).asdict()
        print(
            f"[MongoDBPipeline] Saving item: {data.get('title')} (ISBN: {data.get('isbn')})"
        )
        self.collection.update_one(
            {"isbn": data.get("isbn")}, {"$set": data}, upsert=True
        )
        return item
