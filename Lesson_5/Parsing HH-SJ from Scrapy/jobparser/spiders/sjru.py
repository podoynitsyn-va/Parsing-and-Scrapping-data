# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem

import requests
from lxml import html


class SJSpider(scrapy.Spider):
    name = 'SJru'
    allowed_domains = ['superjob.ru']

    start_urls = ['https://www.superjob.ru/vacancy/search/?keywords=Python']

    def parse(self, response: HtmlResponse):

        # 1 способ - через requests
        headers = {'Accept': '*/*',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36\
                    (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'}
        link = 'https://www.superjob.ru/vacancy/search/?keywords=Python'
        request = requests.get(link, headers=headers)
        root = html.fromstring(request.text)

        requests_next_link = root.xpath("//a[@class='icMQ_ _1_Cht _3ze9n f-test-button-dalshe f-test-link-dalshe']/@href")

        # 2 способ - через response.xpath
        #next_page = response.xpath(
        #    '//div[@class="L1p51"]/a[@rel="next"]/@href').get()
        response_xpath_link = response.xpath(
            "//a[@class='icMQ_ _1_Cht _3ze9n f-test-button-dalshe f-test-link-dalshe']/@href").get()

        #
        # 3 способ - через response.css

        response_css_link = response.css('a.f-test-link-dalshe::attr(href)').extract_first()

        # Далее уже неважно, пока тестим

        next_page = response_css_link

        yield response.follow(next_page, callback=self.parse)

        vacancy_items = response.css(
            'div.f-test-vacancy-item a[class*=f-test-link][href^="/vakansii"]::attr(href)').extract()

        for link in vacancy_items:
            print('3' + link)
            yield response.follow(link, self.vacancy_parse)

    def vacancy_parse(self, response: HtmlResponse):
        vacancy_link = response.url
        vacancy_text = response.css('h1 ::text').extract()

        salary = response.css(
            'div._3MVeX span[class="_3mfro _2Wp8I ZON4b PlM3e _2JVkc"] ::text').extract()

        yield JobparserItem(
            domain=self.allowed_domains[0],
            vacancy_link=vacancy_link,
            vacancy_text=vacancy_text,
            salary=salary
        )
