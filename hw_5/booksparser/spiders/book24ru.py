import scrapy
from scrapy.http import HtmlResponse

from hw_5.booksparser.items import BooksparserItem


class Book24ruSpider(scrapy.Spider):
    name = 'book24ru'
    allowed_domains = ['book24.ru']
    start_urls = ['https://book24.ru/catalog/']
    page_counter = 1

    def parse(self, response: HtmlResponse):
        if response.status == 200:
            links = response.xpath('//a[contains(@class, "product-card__image-link")]/@href').extract()
            self.page_counter += 1
            next_page = f'https://book24.ru/catalog/page-{self.page_counter}/'

            yield response.follow(next_page, callback=self.parse)

            for link in links:
                yield response.follow(link, callback=self.parse_item_page)

    def parse_item_page(self, response: HtmlResponse):
        book_url = response.url
        book_name = response.xpath('//li[contains(@class, "_last-item")]/span[@itemprop="name"]/text()').extract_first()
        book_author_with_link = response.xpath('//span[text()[contains(.,"Автор:")]]/../following::div[1]/a/@title').extract_first()
        book_author_without_link = response.xpath('//span[text()[contains(.,"Автор:")]]/../following::div[1]/a/text()').extract_first()
        book_main_price = response.xpath('//span[@class="app-price product-sidebar-price__price-old"]/text()').extract_first()
        book_sale_price = response.xpath('//meta[@itemprop="price"]/@content').extract_first()
        book_rating = response.xpath('//span[@class="rating-widget__main-text"]/text()').extract_first()

        yield BooksparserItem(url=book_url,
                              name=book_name,
                              author=book_author_with_link if book_author_with_link else book_author_without_link,
                              main_price=book_main_price,
                              sale_price=book_sale_price,
                              rating=book_rating)

