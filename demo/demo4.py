# -*- coding: utf-8 -*-
"""
爬取雪球网股票行情

股票代码
股票名称
当前价
涨跌额
涨跌幅
当日股价幅度
52周股价幅度
市值
市盈率
成交量
成交额


"""
import re

from util.req import spider
import redis
import ujson
from time import time

redis_pool = redis.Redis()


def get_token(refresh=False):
    """

    :param refresh: 强制刷新，重新获取
    :return:
    """
    token = redis_pool.get('xueqiu_token')

    # 判断是否object对象
    if token:
        token = token.decode()
        try:
            token = ujson.loads(token)
        except ValueError:
            pass

    if refresh or not token:
        url = 'https://xueqiu.com/hq'
        result = spider(url)
        text = result.get('text')
        reg = re.escape('SNB.data.access_token =  $.cookie("xq_a_token") || "') + '(?P<m>[\w\d]+)";'
        token = re.search(reg, text).group('m')
        redis_pool.set('xueqiu_token', token)

    return token


def get_page_content(page):
    """
    股票代码 symbol
    股票名称 name
    当前价 current
    涨跌额 change
    涨跌幅 percent
    当日股价幅度 low - high
    52周股价幅度 low52w - high52w
    市值 marketcapital
    市盈率 pettm
    成交量 volume
    成交额 amount
    """
    url = 'https://xueqiu.com/stock/cata/stocklist.json'
    params = {
        'page': page,
        'size': '90',
        'order': 'desc',
        'orderby': 'percent',
        'type': '11,12',
        '_': int(time() * 1000)
    }
    cookies = {
        'xq_a_token': get_token()
    }
    result = spider(url, fields=['json', 'text'], params=params, cookies=cookies)
    json = result.get('json')
    items = json.get('stocks')
    print(result.get('text'))

    if items:
        # 股票详情URL
        [obj.setdefault('url', 'https://xueqiu.com/S/' + obj.get('symbol')) for obj in items]

    return items


def get_content():
    items = []
    page = 1
    while 1:
        r_items = get_page_content(page)
        if not r_items:
            break

        items.extend(r_items)
        print('第 {page} 页获取完成，股票数：{count}'.format(page=page, count=len(r_items)))
        page += 1

    # 返回最大页数
    return items, page - 1


if __name__ == '__main__':
    get_token(refresh=True)
    start_time = time()
    items, max_page = get_content()
    end_time = time()
    print(items)
    print('总页数：{pages}，总股票数：{count}，总耗时：{times}'.format(pages=max_page, count=len(items), times=end_time-start_time))
