from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from hw_7.leroymerlin import settings
from hw_7.leroymerlin.spiders.leroymerlinru import LeroymerlinruSpider

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    # inputed_word = input('Я ищу...')

    crawler_process = CrawlerProcess(settings=crawler_settings)
    # crawler_process.crawl(LeroymerlinruSpider, search=inputed_word)
    crawler_process.crawl(LeroymerlinruSpider)

    crawler_process.start()
