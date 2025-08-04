import scrapy
from scrapy_playwright.page import PageMethod
from news_scraper.items import NewsScraperItem


class NewsSpider(scrapy.Spider):
    """
    Spider for extracting news from kp.ru/online using Playwright.
    - Clicks 'Показать еще' multiple times to load more news items.
    """

    name = "news_spider"
    allowed_domains = ["kp.ru"]
    start_urls = ["https://www.kp.ru/online/"]

    def start_requests(self):
        max_clicks = int(getattr(self, "load_more_clicks", 20))
        self.logger.info(
            f"Using Playwright with up to {max_clicks} clicks for 'Показать еще' button."
        )

        script = f"""
        async () => {{
            let actualClicks = 0;
            for (let i = 0; i < {max_clicks}; i++) {{
                const btn = [...document.querySelectorAll('button')].find(el => el.textContent.includes('Показать еще'));
                if (!btn) break;
                btn.click();
                actualClicks++;
                console.log('Clicked button ' + actualClicks);
                window.scrollTo(0, document.body.scrollHeight);
                await new Promise(r => setTimeout(r, 2500));
            }}
            window.__scrapy_clicks = actualClicks;
            return actualClicks;
        }}
        """

        yield scrapy.Request(
            self.start_urls[0],
            meta={
                "playwright": True,
                "playwright_include_page": True,
                "playwright_page_methods": [
                    PageMethod(
                        "wait_for_selector",
                        "button:has-text('Показать еще')",
                        timeout=60000,
                    ),
                    PageMethod("evaluate", script),
                ],
            },
            callback=self.parse_main,
        )

    async def parse_main(self, response):
        # ✅ Берём результат последнего PageMethod
        clicks_done = response.meta["playwright_page_methods"][-1].result
        self.logger.info(f"✅ Actual 'Показать еще' clicks performed: {clicks_done}")

        page = response.meta["playwright_page"]
        await page.close()

        # Собираем ссылки на новости
        news_links = response.css("a[href^='/online/news/']::attr(href)").getall()
        self.logger.info(f"Found {len(news_links)} news links on the page")

        for link in news_links:
            url = response.urljoin(link)
            yield scrapy.Request(
                url,
                callback=self.parse_article,
                meta={
                    "playwright": True,
                    "playwright_page_methods": [PageMethod("wait_for_selector", "h1")],
                },
            )

    def parse_article(self, response):
        item = NewsScraperItem()
        item["title"] = response.css("h1 *::text, h1::text").getall()
        item["description"] = (
            response.css('div[class*="lead"]::text').get()
            or response.css('meta[name="description"]::attr(content)').get()
        )
        item["publication_datetime"] = response.xpath(
            '//a[@data-is-first="true"]/following-sibling::span/text()'
        ).get()
        item["header_photo_url"] = (
            response.xpath('//div[@data-content-type="photo"]//img/@src').get()
            or response.xpath("//picture/img/@src").get()
        )
        item["header_photo_base64"] = None
        item["keywords"] = response.css('meta[name="keywords"]::attr(content)').get()
        item["authors"] = response.xpath(
            '//a[contains(@href, "/daily/author/")]/span/text()'
        ).getall()
        item["article_text"] = response.xpath(
            '//div[@data-gtm-el="content-body"]//p['
            'not(ancestor::div[@data-content-type="photo"])'
            ' and not(ancestor::div[@data-wide="true"])]//text()'
        ).getall()
        item["source_url"] = response.url
        yield item
