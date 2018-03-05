# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import MySQLdb.cursors
import time
from twisted.enterprise import adbapi


class BuildingPipeline(object):

    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        """
        1、@classmethod声明一个类方法，而对于平常我们见到的叫做实例方法。
        2、类方法的第一个参数cls（class的缩写，指这个类本身），而实例方法的第一个参数是self，表示该类的一个实例
        3、可以通过类来调用，就像C.f()，相当于java中的静态方法
        """
        # 读取settings中配置的数据库参数
        dbparams = dict(
            host=settings['MYSQL_HOST'],
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            passwd=settings['MYSQL_PASSWD'],
            port=settings['MYSQL_PORT'],
            charset='utf8',  # 编码要加上，否则可能出现中文乱码问题
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=False,
        )
        dbpool = adbapi.ConnectionPool('MySQLdb', **dbparams)  # **表示将字典扩展为关键字参数,相当于host=xxx,db=yyy....
        return cls(dbpool)  # 相当于dbpool付给了这个类，self中可以得到

    def process_item(self, item, spider):
        if spider.name == 'taobao':
            query = self.dbpool.runInteraction(self._conditional_insert, item)
            query.addErrback(self._handle_error, item, spider)
        if spider.name == 'detail':
            query = self.dbpool.runInteraction(self._conditional_update, item)
            query.addErrback(self._handle_error, item, spider)

    # 写入数据库中
    # SQL语句在这里
    @staticmethod
    def _conditional_insert(tx, item):
        result = tx.execute("select 1 from auctioning_item_detail where id = %(id)s", {"id": item['id']})
        timestamp = (int(round(time.time() * 1000)))
        if result:
            print("Item already stored in db: %s" % item['id'])
        else:
            sql = "insert into auctioning_item_detail(id, url, title, sell_start, sell_end, type, state, province, " \
                  "city, create_time, modify_time, detailed) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            params = (
                item['id'], item['url'], item['title'], item['start'], item['end'], '01', '00', '浙江', '杭州', timestamp,
                timestamp, '00')
            tx.execute(sql, params)

    @staticmethod
    def _conditional_update(tx, item):
        result = tx.execute("select 1 from auctioning_item_detail where id = %(id)s", {"id": item['id']})
        timestamp = (int(round(time.time() * 1000)))
        if result:
            sql = 'update auctioning_item_detail set start_price = %s, step_price = %s, security_deposit = %s, ' \
                  'valuation = %s, preferred_customer = %s, sell_org = %s, contact = %s, contact_phone = %s, ' \
                  'sell_org = %s, detailed = %s, modify_time = %s where id = %s'
            params = (item['start_price'], item['step_price'], item['security_deposit'], item['valuation'],
                      item['preferred_customer'], item['sell_org'], item['contact'], item['contact_phone'],
                      item['sell_org'], '01', timestamp, item['id'])
            tx.execute(sql, params)
        else:
            print("Item does not stored in db: %s" % item['id'])

    # 错误处理方法
    @staticmethod
    def _handle_error(failuer, item, spider):
        print(failuer)
