from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from hw_8.instascraper import settings
from hw_8.instascraper.spiders.instagramcom import InstagramcomSpider

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    crawler_process = CrawlerProcess(settings=crawler_settings)
    crawler_process.crawl(InstagramcomSpider)

    crawler_process.start()
