# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import os
import re
from datetime import datetime
from pathlib import Path
from itemadapter import ItemAdapter


class MarkdownFilePipeline:
    def __init__(self):
        self.output_dir = Path("wiki_content")
        self.output_dir.mkdir(exist_ok=True)
        self.filename_counts = {}

    def extract_url_slug(self, url):
        """Extract the last part of the URL path as the slug."""
        from urllib.parse import urlparse

        path = urlparse(url).path
        # Get the last non-empty segment from the path
        segments = [s for s in path.split("/") if s]
        if segments:
            slug = segments[-1]
            # Clean up any query parameters or fragments
            slug = slug.split("?")[0].split("#")[0]
            return slug
        return None

    def sanitize_filename(self, name):
        """Convert name to safe filename."""
        # Remove special characters, replace spaces/hyphens with underscores
        safe = re.sub(r"[^\w\s-]", "", name)
        safe = re.sub(r"[-\s]+", "_", safe)
        # Limit length and strip underscores
        return safe[:100].strip("_")

    def get_unique_filename(self, base_filename):
        """Ensure filename is unique by appending counter if needed."""
        if base_filename not in self.filename_counts:
            self.filename_counts[base_filename] = 0
            return f"{base_filename}.md"
        else:
            self.filename_counts[base_filename] += 1
            count = self.filename_counts[base_filename]
            return f"{base_filename}_{count}.md"

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        # Extract URL slug as filename
        url_slug = self.extract_url_slug(adapter.get("url", ""))
        if url_slug:
            base_name = self.sanitize_filename(url_slug)
        else:
            # Fallback to title if URL slug extraction fails
            base_name = self.sanitize_filename(adapter.get("title", "untitled"))

        filename = self.get_unique_filename(base_name)
        filepath = self.output_dir / filename

        # Create markdown content with metadata header
        metadata = f"""---
URL: {adapter.get("url")}
Title: {adapter.get("title")}
Type: {adapter.get("page_type")}
Scraped: {adapter.get("scraped_at")}
---

"""

        full_content = metadata + adapter.get("markdown", "")

        # Write to file
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(full_content)

        spider.logger.info(f"Saved {filename}")

        return item
