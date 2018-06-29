# -*- coding:utf-8 -*-
"""
headers处理
"""


def make_headers(url, **kwargs):
    """ 设置
    :param  url: （指定抓取使用的网址
    :param  ua: （可选）指定抓取使用的User-Agent
    :param  referrer: (可选）指定Referer
    :param  headers （可选） 指定headers，如果使用headers会覆盖原有的参数，如果在headers指定了ua和referrer也会被覆盖

    :return: 输出组合好的headers
    """
    headers = {'Connection': 'keep-alive',
               'Accept-Encoding': 'gzip, deflate',
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
               'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3'}

    headers.update({'Referer': kwargs.get('referrer', make_referrer(url))})
    headers.update({'User-Agent': kwargs.get('ua', make_ua(url))})
    headers.update(kwargs.get('headers', {}))

    return headers


def make_referrer(url, referrer=None):
    """ 设置来源 """
    if referrer:
        referrer = referrer
    elif not url or '.baidu' in url or '.360.com' in url or '.so.com' in url or '.sogou.com' in url:
        referrer = 'https://www.qq.com/'
    elif '.m.tmall' in url or '.m.taobao' in url or '/m.tmall' in url or '/m.taobao' in url:
        referrer = 'https://m.taobao.com/'
    elif '.tmall' in url or '.taobao' in url or '/tmall' in url or '/taobao' in url:
        referrer = 'https://www.taobao.com/?spm=a1z09.1.0.0.gZhpdT&scm=1012.1.1.0'
    else:
        referrer = url

    return referrer


def make_ua(url, ua=None, ua_type=None):
    """ 设置UA """
    if ua:
        ua = ua
    elif ua_type:
        ua = ua_type
    elif '.m.tmall' in url or '.m.taobao' in url or '/m.tmall' in url or '/m.taobao' in url:
        ua = "Mozilla/5.0 (iPhone; CPU iPhone OS 7_1_2 like Mac OS X) AppleWebKit/537.51.2 (KHTML, like Gecko) Version/7.0 Mobile/11D257 Safari/9537.53"
    else:
        ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36'

    return ua
