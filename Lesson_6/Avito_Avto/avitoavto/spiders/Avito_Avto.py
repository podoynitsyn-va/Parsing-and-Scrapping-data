# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from avitoavto.items import AvitoAvtoItem
from scrapy.loader import ItemLoader



class AvitoAvtoSpider(scrapy.Spider):
    name = 'Avito_Avto'
    allowed_domains = ['avito.ru']
    #start_urls = ['https://www.avito.ru/rossiya/transport']
    start_urls = ['https://www.avito.ru/rossiya/avtomobili']

    def parse(self, response: HtmlResponse):
        #links = response.xpath('//a[@class="styles-link-2BT6y"]/@href').extract()
        links = response.xpath('//a[@class="item-description-title-link"]/@href').extract()
        for link in links:
            yield response.follow(link, self.parse_ads)

    def parse_ads(self, response: HtmlResponse):
        # photos = response.xpath('//div[contains(@class, "gallery-img-wrapper")]//div[contains(@class, "gallery-img-frame")]/@data-url').extract()
        # temp = AvitoItem(photos=photos)
        # yield temp
        loader = ItemLoader(item=AvitoAvtoItem(), response=response)
        loader.add_xpath('photos',
                         '//div[contains(@class, "gallery-img-wrapper")]//div[contains(@class, "gallery-img-frame")]/@data-url')
        loader.add_css('title', 'h1.title-info-title span.title-info-title-text::text')
        loader.add_value('avto_link', response.url)
        yield loader.load_item()
