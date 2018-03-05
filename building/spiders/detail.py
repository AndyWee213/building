# -*- coding: utf-8 -*-
import re
import scrapy
import pymysql

from building import settings
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
                    if label and re.sub('\s', '', label.extract()[0]) == '起拍价' and cell.xpath('./span[2]/span/text()'):
                        item['start_price'] = re.sub('\s', '', cell.xpath('./span[2]/span/text()').extract()[0])
                    if label and re.sub('\s', '', label.extract()[0]) == '加价幅度' and cell.xpath('./span[2]/span/text()'):
                        item['step_price'] = re.sub('\s', '', cell.xpath('./span[2]/span/text()').extract()[0])
                    if label and re.sub('\s', '', label.extract()[0]) == '保证金' and cell.xpath('./span[2]/span/text()'):
                        item['security_deposit'] = re.sub('\s', '', cell.xpath('./span[2]/span/text()').extract()[0])
                    if label and re.sub('\s', '', label.extract()[0]) == '优先购买权人':
                        if cell.xpath('./span[2]/span/text()'):
                            item['preferred_customer'] = re.sub('\s', '', cell.xpath('./span[2]/span/text()').extract()[0])
                        else:
                            item['preferred_customer'] = re.sub('\s', '', cell.xpath('./span[2]/text()').extract()[0])
                    if label and re.sub('\s', '', label.extract()[0]) == '评估价' and cell.xpath('./span[2]/span/text()'):
                        item['valuation'] = re.sub('\s', '', cell.xpath('./span[2]/span/text()').extract()[0])

            pai_info_paragraphs = response.xpath('//div[@class="pai-info"]/p')
            if pai_info_paragraphs:
                for paragraph in pai_info_paragraphs:
                    label = re.sub('\s', '', paragraph.xpath('./text()').extract()[0]).split('：')
                    if label[0] == '处置单位' and paragraph.xpath('./a/text()'):
                        item['sell_org'] = paragraph.xpath('./a/text()').extract()[0]
                    if label[0] == '联系咨询方式' and paragraph.xpath('./em/text()'):
                        item['contact'] = paragraph.xpath('./em/text()').extract()[0]
                        item['contact_phone'] = label[1]
            yield item
