BOT_NAME = "noticias"

SPIDER_MODULES = ["noticias.spiders"]
NEWSPIDER_MODULE = "noticias.spiders"


ROBOTSTXT_OBEY = False


USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/151.0.0.0 Safari/537.36"
)


DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}


TWISTED_REACTOR = (
    "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
)


PLAYWRIGHT_LAUNCH_OPTIONS = {
    "headless": True,
    "timeout": 60000,
}


PLAYWRIGHT_CONTEXT_OPTIONS = {
    "ignore_https_errors": True,
}


CONCURRENT_REQUESTS = 1
CONCURRENT_REQUESTS_PER_DOMAIN = 1

DOWNLOAD_DELAY = 2


LOG_LEVEL = "INFO"