# -*- coding: utf-8 -*-
import re

import pymysql
import scrapy

from building.items import BuildingItem


class DetailSpider(scrapy.Spider):
    name = 'detail'
    allowed_domains = ['taobao.com']
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "upgrade-insecure-requests": 1,
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:58.0) Gecko/20100101 Firefox/58.0",
    }

    @staticmethod
    def get_urls():
        # 读取settings中配置的数据库参数
        records = {}
        connection = pymysql.connect(host='172.28.128.3',
                                     user='root',
                                     password='123456',
                                     port=3306,
                                     db='shancha_taobao',
                                     charset='utf8',
                                     cursorclass=pymysql.cursors.DictCursor)
        try:
            with connection.cursor() as cursor:
                sql = 'select id, url from auctioning_item_detail where detailed = "00"'
                cursor.execute(sql)
                results = cursor.fetchall()
                for row in results:
                    records[row['id']] = row['url']
            return records
        except Exception as e:
            print(e)
        finally:
            connection.close()

    def start_requests(self):
        records = self.get_urls()
        pages = []
        for key in records.keys():
            page = scrapy.Request(records[key], headers=self.headers, meta={'id': key})
            pages.append(page)
        return pages

    def parse(self, response):
        if response.meta['id']:
            item = BuildingItem()
            item['id'] = response.meta['id']

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
