# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class JobparserItem(scrapy.Item):
    # define the fields for your item here like:
    _id = scrapy.Field()
    domain = scrapy.Field()
    vacancy_link = scrapy.Field()
    vacancy_text = scrapy.Field()
    salary = scrapy.Field()
    pass