# hw1/merchant_scraper/pipelines.py

"""
Pipeline for cleaning and normalizing scraped data.

- Removes HTML tags and extra spaces from the organization description.
- Ensures website links are properly formatted.
"""

import re
from itemadapter import ItemAdapter
from w3lib.html import remove_tags, replace_escape_chars


class MerchantScraperPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        desc = adapter.get("org_description") or ""

        # Clean HTML and special symbols, but don't touch outer quotes
        desc = remove_tags(desc)
        desc = replace_escape_chars(desc, replace_by=" ")
        desc = desc.replace("\xa0", " ").replace("\u200b", "")
        desc = " ".join(desc.split())  # Normalize spaces
        desc = desc.strip()  # Remove leading/trailing spaces/newlines

        adapter["org_description"] = desc if desc else None

        # Website: normalize URL
        website = adapter.get("website")
        if website:
            website = website.strip()
            if not website.startswith(("http://", "https://")):
                website = f"https://{website}"
            adapter["website"] = website
        else:
            adapter["website"] = None

        return item
