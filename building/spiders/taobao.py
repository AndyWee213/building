# -*- coding: utf-8 -*-
import json
import scrapy

from building.items import BuildingItem


class TaobaoSpider(scrapy.Spider):
    name = 'taobao'
    allowed_domains = ['taobao.com']
    start_urls = 'https://sf.taobao.com/item_list.htm?category=50025969&city=%BA%BC%D6%DD&sorder=1&auction_start_seg=-1'
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "upgrade-insecure-requests": 1,
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:58.0) Gecko/20100101 Firefox/58.0",
    }

    def start_requests(self):
        return [scrapy.Request(self.start_urls, headers=self.headers)]

    def parse(self, response):
        json_buildings = response.xpath('//script[@id="sf-item-list-data"]/text()').extract()
        for each_building in json_buildings:
            arr_buildings = json.loads(each_building, encoding="GBK")['data']
            for each_item in arr_buildings:
                item = BuildingItem()
                item['id'] = each_item['id']
                item['url'] = 'https:' + each_item['itemUrl']
                item['title'] = each_item['title']
                item['start'] = each_item['start']
                item['end'] = each_item['end']
                yield item
        next_page_url = response.xpath('//div[@class="pagination J_Pagination"]/a[@class="next"]/@href').extract()
        if next_page_url:
            yield scrapy.Request('https:'+next_page_url[0].strip(), headers=self.headers)
