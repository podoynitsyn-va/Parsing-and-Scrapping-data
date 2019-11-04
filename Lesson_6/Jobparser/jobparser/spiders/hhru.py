# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem
from scrapy.loader import ItemLoader


class HhruSpider(scrapy.Spider):
    name = 'hhru'
    allowed_domains = ['hh.ru']
    start_urls = ['https://khabarovsk.hh.ru/search/vacancy?clusters=true&enable_snippets=true&text=Python&showClusters=true']

    def parse(self, response: HtmlResponse):
        next_page = response.css('a.HH-Pager-Controls-Next::attr(href)').extract_first()
        yield response.follow(next_page, callback=self.parse)
        vacancy = response.css(
            'div.vacancy-serp div.vacancy-serp-item div.vacancy-serp-item__row_header a.bloko-link::attr(href)').extract()
        for link in vacancy:
            yield response.follow(link, self.vacancy_parse)

    def vacancy_parse(self, response: HtmlResponse):
        # vacancy_link = response.url
        # vacancy_text = response.css('div.vacancy-title h1.header::text').extract_first()
        # salary_full = response.css('div.vacancy-title p.vacancy-salary::text').extract_first()
        #
        # salary_from = response.css(
        #     'div.vacancy-title span[itemprop="baseSalary"] meta[itemprop="minValue"]::attr(content)').extract_first()
        # salary_to = response.css(
        #     'div.vacancy-title span[itemprop="baseSalary"] meta[itemprop="maxValue"]::attr(content)').extract_first()
        # currency = response.css(
        #     'div.vacancy-title span[itemprop="baseSalary"] meta[itemprop="currency"]::attr(content)').extract_first()
        # salary = {'salary_from': salary_from, 'salary_to': salary_to, 'currency':currency}
        # yield JobparserItem(
        #     domain=self.allowed_domains[0],
        #     vacancy_link=vacancy_link,
        #     vacancy_text=vacancy_text,
        #     salary=salary
        #
        # )

        #новая версия
        loader = ItemLoader(item=JobparserItem(), response=response)
        salary_from = response.css(
             'div.vacancy-title span[itemprop="baseSalary"] meta[itemprop="minValue"]::attr(content)').extract_first()
        salary_to = response.css(
             'div.vacancy-title span[itemprop="baseSalary"] meta[itemprop="maxValue"]::attr(content)').extract_first()
        currency = response.css(
             'div.vacancy-title span[itemprop="baseSalary"] meta[itemprop="currency"]::attr(content)').extract_first()
        salary = {'salary_from': salary_from, 'salary_to': salary_to, 'currency': currency}

        loader.add_value('domain', self.allowed_domains[0])
        loader.add_value('vacancy_link', response.url)
        loader.add_css('vacancy_text', 'div.vacancy-title h1.header::text')
        loader.add_value('salary', salary)

        yield loader.load_item()