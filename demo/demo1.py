# -*- coding: utf-8 -*-
"""
抓取尚妆网，获取所有商品信息，价格和销量

http://list.showjoy.com/search/

"""
import re

import time
from pyquery import PyQuery as query
from util.req import spider as Sp


class ShangZhuang:

    def __init__(self):
        self.start_time = time.time()
        self.end_time = 0
        self.goods = []  # 储存商品信息
        self.page = 1
        self.max_count = 0
        self.max_page = 0

    def run(self):
        while 1:
            print('开始爬取...')

            page_goods = []
            url = 'http://list.showjoy.com/search/?page={page}'.format(page=self.page)
            html = query(Sp(url).get('text'))
            containers = html('.brick-cover')

            # 获取最大页
            if self.max_count + self.max_page == 0:
                self.max_count = int(html('.highlight').text())
                self.max_page = int(self.max_count / 20) + 1
                print('获取最大页：' + str(self.max_page))

            for g in containers:
                g = query(g)
                url = g('.brick-pic').eq(0).attr('href')
                img = g('.brick-pic').eq(0)('img').eq(0).attr('src')
                brand = {
                    'name': g('.brand').eq(0)('img').eq(0).attr('alt'),
                    'img': g('.brand').eq(0)('img').eq(0).attr('src')
                }
                title = g('.brick-title').text().strip()

                # 价格转换为数字格式
                price = g('.price').text().strip()
                price = float(re.findall('¥(\d+\.\d+)', price)[0])

                # 销量转换为数字格式
                sales = g('.sales').text().strip()
                sales = int(re.findall('最近成交(\d+)笔', sales)[0])

                page_goods.append({
                    'url': url,
                    'img': img,
                    'brand': brand,
                    'title': title,
                    'price': price,
                    'sales': sales
                })

                print('{title}，价格：{price}，销量：{sales}'.format(title=title, price=price, sales=sales))

            print('第 {page} 页：商品总数：{count}'.format(page=self.page, count=len(page_goods)))
            self.goods += page_goods
            self.page += 1
            if self.page > self.max_page:
                self.end_time = time.time()
                break

        print(
            '完成所有商品获取，总页数：{max_page}，商品总数:{count}，耗费时间：{times}'.format(max_page=self.max_page,
                                                                       count=len(self.goods),
                                                                       times=self.end_time-self.start_time,
                                                                                           ))


if __name__ == '__main__':
    s = ShangZhuang()
    s.run()
