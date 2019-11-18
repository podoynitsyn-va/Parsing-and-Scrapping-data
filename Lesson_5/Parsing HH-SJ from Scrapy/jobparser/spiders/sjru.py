# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem

class SJSpider(scrapy.Spider):
    name = 'SJru'
    allowed_domains = ['superjob.ru']

    keyword = 'Python'

    start_urls = [f'https://www.superjob.ru/vacancy/search/?keywords={keyword}&geo%5Bc%5D%5B0%5D=1']

    def parse(self, response: HtmlResponse):

        next_page = response.css('a.f-test-link-dalshe::attr(href)').extract_first()

        yield response.follow(next_page, callback=self.parse)

        vacancy_items = response.css(
            'div.f-test-vacancy-item a[class*=f-test-link][href^="/vakansii"]::attr(href)').extract()

        for link in vacancy_items:
            print('3' + link)
            yield response.follow(link, self.vacancy_parse)

    def vacancy_parse(self, response: HtmlResponse):
        vacancy_link = response.url
        vacancy_text = response.css('h1 ::text').extract()[0]

        salary = response.css(
            'div._3MVeX span[class="_3mfro _2Wp8I ZON4b PlM3e _2JVkc"] ::text').extract()

        salary = ''.join(salary)

        yield JobparserItem(
            domain=self.allowed_domains[0],
            vacancy_link=vacancy_link,
            vacancy_text=vacancy_text,
            salary=salary
        )
