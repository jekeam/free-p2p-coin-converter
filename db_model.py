# coding: utf-8
from peewee import *


db = MySQLDatabase('p2pfcc', user='root', password='', host='127.0.0.1', port=3306)


class BaseModel(Model):
    class Meta:
        database = db
        
class Request(BaseModel):
    id = PrimaryKeyField(unique=True)
    stat =  CharField(null=False, default='0') # 0 Draft, 1 Post, -1 Cancel, 3 Open Deal,
    user_id = IntegerField(null=False)
    summ = FloatField(null=False)
    coin_sell = CharField(null=True, constraints=[Check('coin_sell in (`BTC`)')])
    addr_sell = CharField(null=False, unique=False)
    coin_buy = CharField(null=True, constraints=[Check('coin_buy in (`BTC`)')])
    addr_buy =  CharField(null=False, unique=False)
    counter_request = IntegerField(null=True)
    
def create_request(user_id, summ, coin_sell, addr_sell, coin_buy, addr_buy):
    Request.create(user_id=user_id, summ=summ, coin_sell=coin_sell, addr_sell=addr_sell, coin_buy=coin_buy, addr_buy=addr_buy)
    
def get_requests(user_id):
    return Request.select().where(user_id==user_id).execute()