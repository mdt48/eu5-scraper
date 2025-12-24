import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from datetime import datetime
from markdownify import markdownify as md
from eu5_scraper.items import WikiPageItem
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


class EU5Spider(CrawlSpider):
    name = "eu5_spider"
    allowed_domains = ["eu5.paradoxwikis.com", "forum.paradoxplaza.com"]
    start_urls = [
        "https://eu5.paradoxwikis.com/Europa_Universalis_5_Wiki",
        "https://eu5.paradoxwikis.com/Developer_diaries",
    ]

    rules = (
        # Follow wiki internal links (pages like /Economy, /Government, etc.)
        Rule(
            LinkExtractor(
                allow=(r"/[A-Z][\w_]+$",),  # Match wiki pages
                deny=(
                    r"/Special:",  # Exclude special pages
                    r"/Template:",  # Exclude templates
                    r"/Category:",  # Exclude categories
                    r"/File:",  # Exclude file pages
                    r"/Help:",  # Exclude help pages
                    r"/User:",  # Exclude user pages
                    r"/Talk:",  # Exclude talk pages
                ),
                restrict_xpaths='//div[@id="mw-content-text"]',  # Only from content area
            ),
            callback="parse_wiki_page",
            follow=True,
        ),
        # Follow forum dev diary links
        Rule(
            LinkExtractor(
                allow=(r"forum\.paradoxplaza\.com/forum/.*threads/\d+",),
                restrict_xpaths='//div[@id="mw-content-text"]',  # Only from wiki content
            ),
            callback="parse_forum_page",
            follow=False,  # Don't follow links from forum pages
        ),
    )

    def parse_wiki_page(self, response):
        """Parse MediaWiki pages."""
        self.logger.info(f"Parsing wiki page: {response.url}")

        # Extract title
        title = response.xpath('//h1[@id="firstHeading"]/text()').get()
        if not title:
            title = response.xpath("//title/text()").get()
            if title:
                title = title.split(" - ")[0].strip()

        # Extract main content
        content = response.xpath(
            '//div[@id="mw-content-text"]/div[@class="mw-parser-output"]'
        ).get()

        if not content:
            self.logger.warning(f"No content found for {response.url}")
            return

        # Parse and clean HTML
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(content, "html.parser")

        # Remove unwanted elements
        for element in soup.select("div.noprint, div.navbox, script, style"):
            element.decompose()

        # Convert to markdown
        markdown_content = md(
            str(soup), heading_style="ATX", bullets="-", strip=["script", "style"]
        )

        # Create item
        item = WikiPageItem()
        item["url"] = response.url
        item["title"] = title or "Untitled"
        item["content"] = content
        item["markdown"] = markdown_content
        item["scraped_at"] = datetime.now().isoformat()
        item["page_type"] = "wiki"

        yield item

    def parse_forum_page(self, response):
        """Parse Paradox Forum dev diary pages using Selenium-rendered content."""
        self.logger.info(f"Parsing forum page: {response.url}")

        # Extract thread title
        title = response.css("h1.p-title-value::text").get()
        if not title:
            title = response.xpath('//meta[@property="og:title"]/@content').get()
        if not title:
            title = response.xpath("//title/text()").get()
            if title:
                title = title.split("|")[0].strip()

        if not title:
            self.logger.warning(f"No title found for {response.url}")
            title = "Untitled Forum Post"

        # Extract ONLY the first post (main post) - not replies
        # Use :first-of-type to target only the first article element
        main_post_selector = "article.message--post:first-of-type"

        # Get content from within the first post's message body
        content = response.css(f"{main_post_selector} .message-body .bbWrapper").get()

        if not content:
            # Fallback: try message-content
            content = response.css(f"{main_post_selector} .message-content").get()

        if not content:
            # Last resort: entire article
            content = response.css(main_post_selector).get()

        if not content:
            self.logger.warning(f"No content found for {response.url}")
            self.logger.debug(f"Page HTML preview: {response.text[:500]}")
            return

        # Parse and clean HTML
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(content, "html.parser")

        # Remove unwanted elements
        for element in soup.select(
            "script, style, .message-signature, .reactionsBar, "
            ".message-actionBar, .message-attribution-opposite"
        ):
            element.decompose()

        # Convert to markdown
        markdown_content = md(
            str(soup), heading_style="ATX", bullets="-", strip=["script", "style"]
        )

        # Create item
        item = WikiPageItem()
        item["url"] = response.url
        item["title"] = title
        item["content"] = content
        item["markdown"] = markdown_content
        item["scraped_at"] = datetime.now().isoformat()
        item["page_type"] = "forum"

        self.logger.info(f"Successfully parsed forum post: {title}")
        yield item

    def parse_start_url(self, response):
        """Handle start URLs - they should also be parsed."""
        if "forum.paradoxplaza.com" in response.url:
            return self.parse_forum_page(response)
        else:
            return self.parse_wiki_page(response)
