# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import MySQLdb.cursors
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
        query = self.dbpool.runInteraction(self._conditional_insert, item)
        query.addErrback(self._handle_error, item, spider)

    # 写入数据库中
    # SQL语句在这里
    def _conditional_insert(self, tx, item):
        result = tx.execute("select 1 from auctioning_item where id = %(id)s", {"id": item['id']})
        if result:
            print("Item already stored in db: %s" % item)
        else:
            sql = "insert into auctioning_item(id, url, title, sell_start, sell_end, type, state, province, city) values(%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            params = (item['id'], item['url'], item['title'], item['start'], item['end'], '01', '00', '浙江', '杭州')
            tx.execute(sql, params)

    # 错误处理方法
    def _handle_error(self, failuer, item, spider):
        print(failuer)
