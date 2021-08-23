import scrapy
from scrapy.http import HtmlResponse
from hw_7.leroymerlin.items import LeroymerlinItem
from scrapy.loader import ItemLoader

class LeroymerlinruSpider(scrapy.Spider):
    name = 'leroymerlinru'
    allowed_domains = ['leroymerlin.ru']


    def __init__(self, search):
        super().__init__()
        if len(search):
            self.start_urls = [f'https://kaliningrad.leroymerlin.ru/search/?q={search}']
        else:
            self.start_urls = ['https://kaliningrad.leroymerlin.ru/catalogue/dekor/']


    def parse(self, response: HtmlResponse):

        # ссылка <a> на следующую страницу
        next_page_link = response.xpath('//a[@data-qa-pagination-item="right"]/@href').extract_first()
        if next_page_link:
            yield response.follow(next_page_link, callback=self.parse)

        # ссылка <a> на товар
        product_links = response.xpath('//a[@data-qa="product-name"]')
        for link in product_links:
            yield response.follow(link, callback=self.parse_product)

    def parse_product(self, response: HtmlResponse):

        item_loader = ItemLoader(item=LeroymerlinItem(), response=response)
        item_loader.add_value('url', response.url)
        item_loader.add_xpath('name', '//h1/text()')
        item_loader.add_xpath('price', '//uc-pdp-price-view[@slot="primary-price"]/span[@slot="price"]/text()')
        item_loader.add_xpath('photos', '//source[@media=" only screen and (min-width: 1024px)"]/@srcset') # "only screen and (min-width: 768px)"|" only screen and (-webkit-min-device-pixel-ratio: 2)"|"(max-width: 767px)"|
        item_loader.add_xpath('props', '//div[@class="def-list__group"]')

        yield item_loader.load_item()
        #
        # product_photos = response.xpath('//source[@media=" only screen and (min-width: 1024px)"]/@srcset').getall()
        # product_props = response.xpath('//div[@class="def-list__group"]/*/text()').getall()
        # yield LeroymerlinItem(link=product_link,
        #                       name=product_name,
        #                       price=product_price,
        #                       photos=product_photos,
        #                       props=product_props)
