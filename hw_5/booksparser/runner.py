from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from hw_5.booksparser import settings
from hw_5.booksparser.spiders.book24ru import Book24ruSpider

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    crawler_process = CrawlerProcess(settings=crawler_settings)
    crawler_process.crawl(Book24ruSpider)

    crawler_process.start()
