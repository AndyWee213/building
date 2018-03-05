# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class BuildingItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    id = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    start = scrapy.Field()
    end = scrapy.Field()
    province = scrapy.Field()
    city = scrapy.Field()
    start_price = scrapy.Field()
    step_price = scrapy.Field()
    security_deposit = scrapy.Field()
    valuation = scrapy.Field()
    preferred_customer = scrapy.Field()
    sell_org = scrapy.Field()
    contact = scrapy.Field()
    contact_phone = scrapy.Field()
