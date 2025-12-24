# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class WikiPageItem(scrapy.Item):
    url = scrapy.Field()  # Source URL
    title = scrapy.Field()  # Page title
    content = scrapy.Field()  # Main content HTML
    markdown = scrapy.Field()  # Converted markdown
    scraped_at = scrapy.Field()  # Timestamp
    page_type = scrapy.Field()  # 'wiki' or 'forum'
