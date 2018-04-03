# -*- coding: utf-8 -*-
import json
import re
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
                yield scrapy.Request('https:' + each_item['itemUrl'],
                                     meta={'id': each_item['id'], 'url': 'https:' + each_item['itemUrl'],
                                           'title': each_item['title'], 'start': each_item['start'],
                                           'end': each_item['end']}, callback = self.parse_item)
        next_page_url = response.xpath('//div[@class="pagination J_Pagination"]/a[@class="next"]/@href').extract()
        if next_page_url:
            yield scrapy.Request('https:' + next_page_url[0].strip(), headers=self.headers)

    def parse_item(self, response):
        if response.meta['id']:
            item = BuildingItem()
            item['id'] = response.meta['id']
            item['url'] = response.meta['url']
            item['title'] = response.meta['title']
            item['start'] = response.meta['start']
            item['end'] = response.meta['end']
            pai_pay_table_cells = response.xpath('//table[@class="pai-pay-infor"]/tbody/tr/td')
            if pai_pay_table_cells:
                for cell in pai_pay_table_cells:
                    label = cell.xpath('./span[1]/text()')
                    if label and (self.trim_blank(label.extract()[0]) == '起拍价' or self.trim_blank(
                            label.extract()[0]) == '变卖价') and cell.xpath('./span[2]/span/text()'):
                        item['start_price'] = self.trim_blank(cell.xpath('./span[2]/span/text()').extract()[0])
                    if label and (self.trim_blank(label.extract()[0]) == '起拍价' or self.trim_blank(
                            label.extract()[0]) == '变卖价') and cell.xpath('./span[2]/span/text()'):
                        item['start_price'] = self.trim_blank(cell.xpath('./span[2]/span/text()').extract()[0])
                    if label and self.trim_blank(label.extract()[0]) == '加价幅度' and cell.xpath('./span[2]/span/text()'):
                        item['step_price'] = self.trim_blank(cell.xpath('./span[2]/span/text()').extract()[0])
                    if label and self.trim_blank(label.extract()[0]) == '变卖预缴款' and cell.xpath('./span[2]/span/text()'):
                        item['pre_pay'] = self.trim_blank(cell.xpath('./span[2]/span/text()').extract()[0])
                    if label and self.trim_blank(label.extract()[0]) == '保证金' and cell.xpath('./span[2]/span/text()'):
                        item['security_deposit'] = self.trim_blank(cell.xpath('./span[2]/span/text()').extract()[0])
                    if label and self.trim_blank(label.extract()[0]) == '优先购买权人':
                        if cell.xpath('./span[2]/span/text()'):
                            item['preferred_customer'] = \
                                self.trim_blank(cell.xpath('./span[2]/span/text()').extract()[0])
                        else:
                            item['preferred_customer'] = \
                                re.sub(':', '', self.trim_blank(cell.xpath('./span[2]/text()').extract()[0]))
                    if label and (self.trim_blank(label.extract()[0]) == '评估价' or self.trim_blank(
                            label.extract()[0]) == '市场价') and cell.xpath('./span[2]/span/text()'):
                        item['valuation'] = self.trim_blank(cell.xpath('./span[2]/span/text()').extract()[0])
                    if label and self.trim_blank(label.extract()[0]) == '类型' and cell.xpath('./span[2]/span/text()'):
                        item['sell_type'] = self.trim_blank(cell.xpath('./span[2]/span/text()').extract()[0])

            pai_info_paragraphs = response.xpath('//div[@class="pai-info"]/p')
            look_for_review_org = False
            if pai_info_paragraphs:
                for paragraph in pai_info_paragraphs:
                    label = re.sub('\s', '', paragraph.xpath('./text()').extract()[0]).split('：')
                    if label[0] == '处置单位':
                        if paragraph.xpath('./a'):
                            item['sell_org'] = self.trim_blank(paragraph.xpath('./a/text()').extract()[0])
                        else:
                            item['sell_org'] = self.trim_blank(paragraph.xpath('./text()').extract()[0]).split('：')[1]
                            look_for_review_org = True
                    if label[0] == '联系咨询方式' and paragraph.xpath('./em/text()'):
                        item['contact'] = paragraph.xpath('./em/text()').extract()[0].strip()
                        item['contact_phone'] = paragraph.xpath('./text()').extract()[1].strip()

            if look_for_review_org and response.xpath('//div[@class="pai-info"]/text()'):
                item['review_org'] = self.trim_blank(response.xpath('//div[@class="pai-info"]/a/text()').extract()[0])
            yield item

    @staticmethod
    def trim_blank(param):
        return re.sub('\s', '', param)
