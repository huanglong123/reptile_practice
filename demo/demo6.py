# -*- coding: utf-8 -*-
"""
爬取豌豆荚游戏周排行榜

游戏名称、下载量、图标、下载地址

"""
from util.req import spider
from util.dcit_util import unpack_dict
from pyquery import PyQuery as query
from time import time


def get_cards():
    cards = []
    page = 1

    start_time = time()

    while 1:
        params = {
            'resourceType': 1,  # 0是软件排行，1是游戏排行
            'page': page
        }
        ret = spider('http://www.wandoujia.com/api/top/more', params=params, fields='json')
        json_data = ret.get('json')
        content = unpack_dict(json_data, 'data.content')

        # 到最大页则 content 为空
        if not content:
            end_time = time()
            print('爬取完成，总页数：{page}，游戏总数：{count}，耗时：{times}'.format(page=page - 1, count=len(cards), times=end_time-start_time))
            return cards

        document = query(content)
        cards_dom = document('.card')
        for card_dom in cards_dom:
            # 游戏名称、下载量、图标、下载地址
            # 下载地址需安装豌豆荚
            card_dom = query(card_dom)
            download_btn = card_dom('a.i-source.install-btn')

            name = download_btn.attr('data-name')
            downloads = download_btn.attr('data-install')
            icon = download_btn.attr('data-app-icon')
            url = download_btn.attr('href')

            cards.append({
                'name': name,
                'downloads': downloads,
                'icon': icon,
                'url': url
            })

        print('完成第 {page} 页爬取，当前总数：{count}'.format(page=page, count=len(cards)))
        page += 1


if __name__ == '__main__':
    cards = get_cards()
    print(cards)
    # Tools.set('demo10', cards)
