# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class Eu5ScraperSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    async def process_start(self, start):
        # Called with an async iterator over the spider start() method or the
        # maching method of an earlier spider middleware.
        async for item_or_request in start:
            yield item_or_request

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class Eu5ScraperDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


import scrapy


class ForumPlaywrightMiddleware:
    """Spider middleware to mark forum requests for Playwright rendering."""

    def process_spider_output(self, response, result, spider):
        """
        Intercept spider output and mark forum requests for Playwright.

        This runs after CrawlSpider generates requests from Rules, allowing us
        to add Playwright metadata to forum.paradoxplaza.com requests.
        """
        for item_or_request in result:
            # Pass through non-Request items
            if not isinstance(item_or_request, scrapy.Request):
                yield item_or_request
                continue

            # Convert forum URLs to use Playwright
            if "forum.paradoxplaza.com" in item_or_request.url:
                spider.logger.info(
                    f"Marking forum request for Playwright: {item_or_request.url}"
                )

                # Preserve all metadata from the original request
                meta = item_or_request.meta.copy()

                # Add Playwright-specific metadata
                meta["playwright"] = True
                meta["playwright_include_page"] = True
                meta["playwright_page_methods"] = [
                    # Wait for page to fully load
                    {"method": "wait_for_load_state", "args": ["domcontentloaded"]},
                    # Give page time to execute JavaScript and bypass any checks
                    {"method": "wait_for_timeout", "args": [5000]},
                ]

                # Create new request with Playwright metadata
                yield item_or_request.replace(meta=meta)
            else:
                # Pass through wiki requests unchanged
                yield item_or_request
