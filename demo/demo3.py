# -*- coding: utf-8 -*-
"""
抓取京东商品评价

http://search.jd.com/

"""
import time

from pyquery import PyQuery as query
from tqdm import tqdm
from util.req import spider
from xcore.util.time_util import Timer
from util.dcit_util import unpack_dict


class JingDongComment:

    def __init__(self):
        self.stime = time.time()
        self.etime = 0
        self.max_page = 0
        self.keyword = ''

    def process_goods(self, html):
        """
        清理获取到的商品数据，返回商品列表

        :param ret:
        :return:
        """
        goods = []
        d_goods = html('.gl-item')

        #  解析商品数据
        for d_good in d_goods:
            d_good = query(d_good)
            good = {
                'id': d_good.attr('data-sku'),
                'title': d_good('.p-name > a').text(),
                'price': d_good('.p-price > strong > i').text(),
                'url': 'https:' + d_good('div.p-img > a').attr('href')
            }

            # 商品封面
            icon = d_good('.p-img > a > img').attr('source-data-lazy-img')

            if not icon or icon == 'done':
                icon = d_good('.p-img > a > img').attr('src')
            good.setdefault('icon', 'https:' + icon)

            goods.append(good)

        return goods

    def get_max_page(self):
        """
        获取商品搜索最大页

        :return:
        """
        url = 'http://search.jd.com/Search?keyword=' + self.keyword
        max_page = query(spider(url).get('text')).html('#J_topPage > span > i').text()
        print('获取最大页：' + max_page)
        return max_page

    def get_page_goods(self, page):
        page = page * 2 - 1  # 京东商品搜索页每页请求两次
        url = 'http://search.jd.com/s_new.php'

        """ 获取上半部分商品 """
        params = {
            "keyword": self.keyword,
            "page": page,
            "click": "0",
            "enc": "utf-8",
            "qrst": "1",
            "rt": "1",
            "s": "110",
            "stop": "1",
            "vt": "2"
        }
        html = query(spider(url, params=params).get('text'))
        goods = self.process_goods(html)

        """ 获取下半部分商品 """
        params = {
            "keyword": self.keyword,
            "show_items": ','.join([g.get('id') for g in goods]),
            "enc": "utf-8",
            "page": "2",
            "log_id": "1510505434.63851",
            "qrst": "1",
            "rt": "1",
            "s": "28",
            "scrolling": "y",
            "stop": "1",
            "tpl": "2_M",
            "vt": "2"
        }
        html = query(spider(url, params=params).get('text'))
        goods.extend(self.process_goods(html))

        print('第 {page} 页商品数量：{count}'.format(page=page, count=len(goods)))
        return goods

    def get_comments(self, good_id):
        """
        获取商品评价

        :param good_id:
        :return:
        """
        url = 'https://sclub.jd.com/comment/productPageComments.action'
        params = {
            "productId": good_id,
            "page": "0",
            "pageSize": "10",
            "sortType": "3",
            "isShadowSku": "0",
            "score": "0",
            "callback": "fetchJSON_comment98vv14677",
        }
        rp = spider(url, params=params, fields='json')
        if rp.get('code') == 200:
            comments = [c.get('content') for c in unpack_dict(rp.get('json'),'comments')]
            print('商品ID {good_id} 评价获取完成'.format(good_id=good_id))
            return comments
        else:
            print('获取商品评价出错：' + str(rp.err))

    def run(self, keyword, page=1):
        self.keyword = keyword
        # self.max_page = self.get_max_page()

        goods = self.get_page_goods(page=page)
        for g in tqdm(goods, total=len(goods)):
            comments = self.get_comments(good_id=g.get('id'))
            g.setdefault('comments', comments)

        self.etime = time.time()
        print(goods[0])
        print('总耗时：{t}，总商品数：{g}'.format(t=Timer.format_easytime(self.etime - self.stime), g=len(goods)))

    def get_recommend_goods(self, page, keyword):
        """
        获取（左侧）商品精选

        :param page:
        :param keyword:
        :return:
        """
        goods = []

        url = 'http://x.jd.com/Search'
        params = {
            "page": page,
            "keyword": keyword,
            "_": time.time() * 1000,
            "adType": "7",
            "ad_ids": "291:20",
            "area": "1",
            "callback": "jQuery5618052",
            "enc": "utf-8",
            "xtest": "new_search"
        }

        ret = spider(url, fields='json', params=params, debug=True)
        if ret.get('code') == 200:
            # 解析商品数据，格式化保存
            json_data = ret.get('json')
            json_goods = json_data.get('291', [])
            for json_good in json_goods:
                good = {
                    'id': json_good.get('sku_id'),  # 通过 ID 取商品评价
                    'title': query(json_good.get('ad_title')).text(),
                    'icon': 'http://img1.360buyimg.com/n1/' + json_good.get('image_url'),
                    'price': json_good.get('pc_price'),
                    'url': json_good.get('click_url')
                }
                # 获取商品评价
                good.setdefault('comments', self.get_comments(good.get('id')))
                goods.append(good)
                print('已获取商品：' + good.get('title'))
            else:
                print('第 {page} 页商品获取完成'.format(page=page))
        else:
            print('获取商品出错：' + str(ret.get('err')))

        return goods


if __name__ == '__main__':
    s = JingDongComment()
    s.run(keyword='iphone')