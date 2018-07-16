# -*- coding: utf-8 -*-
"""
爬取《糗事百科》热门文章

内容
配图
评论
原文链接

抓取太频繁会导致失败，每页抓取后休息 1 秒

"""
import time
from pyquery import PyQuery as query

from util.req import spider


def get_page_content(page):
    items = []

    domain = 'https://www.qiushibaike.com'

    # 获取原始链接，内容详情页
    url = 'https://www.qiushibaike.com/8hr/page/{0}/'.format(page)
    ret = spider(url)
    text = ret.get('text')
    index_document = query(text)

    articles = index_document('.article')
    for article in articles:
        href = query(article)('a.contentHerf').attr('href')
        items.append({
            'url': domain + href
        })
    print('第 {page} 页获取链接数：{count}'.format(page=page, count=len(items)))
    if len(items) == 0:
        print(ret)

    for index, item in enumerate(items):
        for i in range(0, 2):
            # 访问详情页，获取内容 + 评论
            text = spider(item['url']).get('text')
            document = query(text)
            # 内容
            content = document('#single-next-link > div').text()
            if not content:
                print('获取失败，重试获取，进度：{index}/{maxlength}'.format(index=index + 1, maxlength=len(items)))
                continue

            # 内容配图
            img_href = document('#single-next-link > div.thumb > img').attr('src') or ''
            if img_href:
                img_href = 'https:' + img_href

            # 评论
            comments = []
            comments_dom = document('.comment-block > div.replay > span.body')
            for span in comments_dom:
                comments.append(query(span).text())

            item.update({
                'content': content,
                'img_href': img_href,
                'comments': comments
            })
            print('获取第 {page} 页，进度：{index}/{maxlength}'.format(page=page, index=index + 1, maxlength=len(items)))
            break

    print('第 {page} 页获取完成'.format(page=page))

    if page == 1:
        max_page = int(index_document('#content-left > ul > li:nth-child(7) > a > span').text())
        print('最大页：' + str(max_page))
        return max_page, items

    return items


def get_hot_content():
    """
    获取热门文章

    :return:
    """
    start = time.time()
    print('抓取开始')

    max_page, contents = get_page_content(1)
    for page in range(2, max_page + 1):
        items = get_page_content(page)
        contents.extend(items)
        time.sleep(1)

    end_time = time.time()
    print('抓取完成，总页数：{max_page}，总文章数：{count}，耗时：{times}'.format(
        max_page=max_page,
        count=len(contents),
        times=end_time - start
    ))
    return contents


if __name__ == '__main__':
    contents = get_hot_content()
    # Tools.set('demo9', contents)
