# coding: utf-8
import peewee


db = peewee.MySQLDatabase('p2pfcc', user='root', password='', host='127.0.0.1', port=3306)
accesse_coins = 'in ("BTC", "ETH")'


class BaseModel(Model):
    class Meta:
        database = db