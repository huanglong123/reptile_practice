"""
抓取淘宝网，搜索商品页，关键词：keyword
获取宝贝的名称，缩略图，价格，销量

https://s.taobao.com/search

"""

# -*- coding: utf-8 -*-
import re

import time
from util.req import spider as Sp
from util.dcit_util import unpack_dict


class TaoBaoGood:

    def __init__(self, max_page=5):
        self.max_page = max_page
        self.goods = []
        self.url = 'https://s.taobao.com/search'
        self.stime = time.time()
        self.etime = 0

    def run(self, keyword):
        for page in range(1, self.max_page + 1):
            print('开始抓取第 {page} 页...'.format(page=page))
            page_goods = []

            params = {
                "q": keyword,
                "data-value": page * 44,  # 当前页
                "s": page * 44 - 44,  # 上一页

                "ajax": "true",
                "data-key": "s",
                "callback": "jsonp1111",
                "commend": "all",
                "ie": "utf8",
                "initiative_id": "tbindexz_20170306",
                "bcoffset": "4",
                "ntoffset": "4",
                "p4ppushleft": "1%2C48",
                "search_type": "item",
                "sourceId": "tb.index",
                "spm": "a21bo.2017.201856-taobao-item.1",
                "ssid": "s5-e"
            }
            auctions = unpack_dict(Sp(self.url, params=params, fields='json').get('json'), 'mods.itemlist.data.auctions')

            for g in auctions:
                nid = g.get('nid')
                if nid not in [i.get('nid') for i in self.goods]:
                    try:
                        data = {
                            'id': nid,
                            'title': g.get('raw_title'),
                            'img': 'https:' + g.get('pic_url'),
                            'url': 'https:' + g.get('detail_url'),
                            'price': float(g.get('view_price')),
                            'city': g.get('item_loc'),
                            'sales': g.get('view_sales') and int(re.findall('(\d+)人付款', g.get('view_sales'))[0]) or 0,
                            # 销量
                            'credit': unpack_dict(g, 'shopcard.sellerCredit')  # 信用
                        }
                    except Exception as e:
                        print(g)
                        raise e
                    page_goods.append(data)
                    print('{title}，价格：{price}，销量：{sales}'.format(title=data.get('title'), price=data.get('price'),
                                                                     sales=data.get('sales')))

            self.goods += page_goods
            print('完成第 {page} 页抓取，总商品数：{count}'.format(page=page, count=len(page_goods)))
            time.sleep(1)

        self.etime = time.time()
        print('抓取完成，总页数：{page}，商品总数：{count}，平均个数：{avg_count}，耗时：{times}'.format(page=self.max_page,
                                                                                    count=len(self.goods),
                                                                                    avg_count=int(
                                                                                        len(
                                                                                            self.goods) / self.max_page),
                                                                                    times=self.etime - self.stime))


if __name__ == '__main__':
    s = TaoBaoGood()
    s.run('连衣裙')
    print(s.goods[0])
