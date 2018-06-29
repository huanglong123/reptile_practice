# -*- coding:utf-8 -*-
"""
http://docs.python-requests.org/zh_CN/latest/user/quickstart.html

"""

import requests

from .status_code import code_info
from .headers import make_headers

import urllib3
urllib3.disable_warnings()


class Req:
    
    def __init__(self):
        """ 爬虫基本操作
        使用方法 Req().get使用get方式，Req().post就使用post方式，Req().head参数就使用head方式

        :params url  需要抓取的网页地址
        :params fields 需要输出的参数，默认输出code和last_url、text内容，可以选择json、headers、cookies、cookies_dict、content、encode、raw
        :params facility 日志记录集合名字，一般不需要改
        :params ident  日志标识，要用网站名字或者版本库、服务名字，可以根据各个节点做不同的标不同识来区分，比如kdb.items.price
        :params debug 是否调试，默认是False：将日志写入到日志服务器，True：日志内容会在终端打印和写入日志服务器
        :params url: 需要抓取的网址，支持http://和https://
        :params params: (可选) 网址参数params={'a': 'test', 'b': 'ok'} 会在请求网址生成 /?a=test&b=ok，注意：params、data、json里面的数据都经过了url编码处理
        :params data: (可选) 发送post请求，dict类型数据。通过data参数来传递，data不光可以接受字典类型的数据，还可以接受json等格式
        :params json: (可选) 发送post请求，json类型数据。通过json参数来传递
        :params headers: (可选) 定制headers。所有的 header 值必须是 string
        :params cookies: (可选) 自定义请求的COOKIES ，可以是dict类型或者是CookieJar
        :params files: (可选) 发送文件的post类型，相当于向网站上传一张图片，文档等操作，这时要使用files参数
        :params auth: (可选) Aauth认证，支持HTTPProxyAuth、HTTPDigestAuth等认证方式.
        :params timeout: (可选) 设置超时时间，数值要求是int或者float，格式可以是tuple(连接超时时间,  读取超时时间) 或者一个超时时间数字，timeout=(3, 27) or timeout=30
        :params allow_redirects: (可选) 自动处理重定向的请求，默认是True允许重定向，允许301、302等跳转，设置False来设置不自动处理重定向，使用r.history来追踪是否有重定向
        :params proxies: (可选) 使用代理进行抓取，可以设置url、主机、方法.
        :params encoding (可选) 指定解析页面使用的编码，默认会从网页中获取编码，不需要自己指定.
        :params stream: (可选) 流下载方式，默认False，立即下载全部数据，使用requests的get下载大文件/数据时，建议使用使用stream模式，使用流文件模式
        :params verify: (可选) 是否使用SSL证书验证，requests默认是True，Req默认是False，因为有些网站使用的ssl不标准会造成出错
        :params cert: (可选) 使用自定义SSL证书，需要verify=True才生效，默认使用https连接时候获取到证书，cert是指定一个解密的证书文件来认证，加密的证书文件是无效的
        """
        self.requests = requests.session()
        self.req = None
        self.encoding = None

    def get(self, url, **kwargs):
        """ get方式取数据 """
        kw = self.build_parameter(url, **kwargs)
        self.req = self.requests.get(url, **kw)

        return self

    def post(self, url, **kwargs):
        """ post方式，需要有data、json、files三个参数的任意一个 """
        kw = self.build_parameter(url, **kwargs)
        if kw.get('data') and isinstance(kw.get('data'), str):
            # post_data默认使用quote处理，默认对+进行编码，将空格变成新+，造成个别网址会出错，遇到这种情况前端传post_data过来要转成str
            kw['headers']['Content-Type'] = 'application/x-www-form-urlencoded'

        self.req = self.requests.post(url, **kw)

        return self

    def head(self, url, **kwargs):
        """ 只取head操作 """
        kw = self.build_parameter(url, **kwargs)
        self.req = self.requests.head(url, **kw)
        return self

    def build_parameter(self, url, **kwargs):
        """ 对参数进行处理，默认添加请求头、ua、证书忽略等操作"""
        kw = dict(params=kwargs.get('params'),
                  data=kwargs.get('data'),
                  cookies=kwargs.get('cookies'),
                  files=kwargs.get('files'),
                  auth=kwargs.get('auth'),
                  allow_redirects=kwargs.get('allow_redirects', True),
                  hooks=kwargs.get('hooks'),
                  stream=kwargs.get('stream'),
                  cert=kwargs.get('cert'),
                  json=kwargs.get('json'))
        kw['headers'] = make_headers(url, **kwargs)
        kw['verify'] = kwargs.get('verify', False)
        kw['proxies'] = kwargs.get('proxies', None)
        kw['timeout'] = kwargs.get('timeout', (3, 27))
        self.encoding = kwargs.get('encoding', None)

        return kw

    @property
    def url(self):
        """ 最后的抓取网址，遇到301、302会返回实际抓取的网址 """
        return self.req.url

    @property
    def headers(self):
        """ 获取网页的头部信息，注意requests返回的headers是属CaseInsensitiveDict，要用dict转换 """
        return dict(self.req.headers)

    @property
    def cookies(self):
        """ 获取响应中的cookies，返回RequestsCookieJar """
        return self.req.cookies

    @property
    def cookies_dict(self):
        """ 获取响应中的cookies，已经转成dict """
        return requests.utils.dict_from_cookiejar(self.req.cookies)

    @property
    def status_code(self):
        """ 获取状态码  """
        return self.req.status_code

    @property
    def text(self):
        """ 获取内容 """
        if self.status_code == 200:
            if self.encoding:
                self.req.encoding = self.encoding
            elif not self.req.encoding or self.req.encoding == 'ISO-8859-1':
                """ 如果HTTP响应中Content-Type字段没有指定charset，则默认页面是'ISO-8859-1'编码，中文会乱码，需检查页面内容编码
                r.encoding 网页header字段Content-Type字段charset的响应内容编码方式
                r.apparent_encoding 从内容中分析出的响应内容编码方式（备选编码方式）
                """
                self.req.encoding = self.req.apparent_encoding
            if self.req.encoding == 'GB2312' or self.req.encoding == 'gb2312':
                self.req.encoding = 'GB18030'

        return self.req.text

    @property
    def content(self):
        """ 输出原始抓取数据 """
        return self.req.content

    @property
    def history(self):
        """ 输出连接跳转的信息 """
        return self.req.history

    @property
    def raw(self):
        """ 获取来自服务器的原始套接字响应，需要请求中设置了 stream=True """
        return self.req.raw

    @property
    def encode(self):
        """ 输出编码信息 """
        return self.req.encoding

    @property
    def json(self):
        """ 输出json格式的内容 """
        from xcore.util.json_util import json_load
        return json_load(self.text)


class Spider:

    def __init__(self):
        """
        网页抓取方法，跟直接使用Req()不同的是已经使用了try，遇到抓取出错时候不会引起500，出错时候会返回{'code': 500}
        使用方法 Spider().get使用get方式，Spider().post就使用post方式，Spider().head参数就使用head方式

        :params url  需要抓取的网页地址
        :params fields 需要输出的参数，默认输出code和last_url、text内容，可以选择json、headers、cookies、cookies_dict、content、encode、raw
        :params facility 日志记录集合名字，一般不需要改
        :params ident  日志标识，要用网站名字或者版本库、服务名字，可以根据各个节点做不同的标不同识来区分，比如kdb.items.price
        :params debug 是否调试，默认是False：将日志写入到日志服务器，True：日志内容会在终端打印和写入日志服务器
        :params url: 需要抓取的网址，支持http://和https://
        :params params: (可选) 网址参数params={'a': 'test', 'b': 'ok'} 会在请求网址生成 /?a=test&b=ok，注意：params、data、json里面的数据都经过了url编码处理
        :params data: (可选) 发送post请求，dict类型数据。通过data参数来传递，data不光可以接受字典类型的数据，还可以接受json等格式
        :params json: (可选) 发送post请求，json类型数据。通过json参数来传递
        :params headers: (可选) 定制headers。所有的 header 值必须是 string
        :params cookies: (可选) 自定义请求的COOKIES ，可以是dict类型或者是CookieJar
        :params files: (可选) 发送文件的post类型，相当于向网站上传一张图片，文档等操作，这时要使用files参数
        :params auth: (可选) Aauth认证，支持HTTPProxyAuth、HTTPDigestAuth等认证方式.
        :params timeout: (可选) 设置超时时间，数值要求是int或者float，格式可以是tuple(连接超时时间,  读取超时时间) 或者一个超时时间数字，timeout=(3, 27) or timeout=30
        :params allow_redirects: (可选) 自动处理重定向的请求，默认是True允许重定向，允许301、302等跳转，设置False来设置不自动处理重定向，使用r.history来追踪是否有重定向
        :params proxies: (可选) 使用代理进行抓取，可以设置url、主机、方法.
        :params encoding (可选) 指定解析页面使用的编码，默认会从网页中获取编码，不需要自己指定.
        :params stream: (可选) 流下载方式，默认False，立即下载全部数据，使用requests的get下载大文件/数据时，建议使用使用stream模式，使用流文件模式
        :params verify: (可选) 是否使用SSL证书验证，requests默认是True，Req默认是False，因为有些网站使用的ssl不标准会造成出错
        :params cert: (可选) 使用自定义SSL证书，需要verify=True才生效，默认使用https连接时候获取到证书，cert是指定一个解密的证书文件来认证，加密的证书文件是无效的

        :return: 根据 fields 整形输出的数据
        """

        self.req = Req()

    def get(self, url, **kwargs):
        """ get方式取数据 """
        kwargs['method'] = 'get'
        return self.get_result(url, **kwargs)

    def post(self, url, **kwargs):
        """ post方式，需要有data、json、files三个参数的任意一个 """
        kwargs['method'] = 'post'
        return self.get_result(url, **kwargs)

    def head(self, url, **kwargs):
        """ 只取head操作 """
        kwargs['method'] = 'head'
        return self.get_result(url, **kwargs)

    def get_result(self, url, **kwargs):
        """ 获取结果"""

        fields = kwargs.get('fields', ['text'])
        if isinstance(fields, str):
            fields = fields.split(',')
        method = kwargs.get('method', 'get')

        log_params = self.log_params(**kwargs)
        err = None
        result = {}
        try:
            ret = getattr(self.req, method.strip())(url, **kwargs)

            code = ret.status_code
            result['code'] = code
            if code != 200:
                result['msg'] = code_info.req(code)
            result['last_url'] = ret.url

            for field in fields:
                result[field.strip()] = getattr(ret, field.strip())

        except requests.exceptions.RequestException as e:
            print(url, e, **log_params)
            err = e
            code = 602
        except Exception as e:
            print(url, e, **log_params)
            err = e
            code = 600

        if err:
            if self.debug is not True:
                err = 'debug关闭不显示错误信息'
            result = {'code': code, 'fields': fields, 'err': err}

        return result

    def log_params(self, **kwargs):
        """ 组合日志参数 """
        kw = {}
        if kwargs.get('facility'):
            kw['facility'] = kwargs.get('facility')
        if kwargs.get('ident'):
            kw['ident'] = kwargs.get('ident')
        if kwargs.get('debug', False) is True:
            kw['debug'] = True
            self.debug = True

        return kw


def spider(url, **kwargs):
    """ 网页抓取方法，跟直接使用Req()不同的是已经使用了try，遇到抓取出错时候不会引起500，出错时候会返回{'code': 500}
    默认使用get方式，如果使用了data、json、files三个参数的任意一个或者参数有post就使用post方式，有head参数就使用head方式
    url  需要抓取的网页地址
    method  默认使用get方式，参数method='post'就使用post方式，有method='head'参数就使用head方式

    :param url  需要抓取的网页地址
    :param fields 需要输出的参数，默认输出code和last_url、text内容，可以选择json、headers、cookies、cookies_dict、content、encode、raw
    :param facility 日志记录集合名字，一般不需要改
    :param ident  日志标识，要用网站名字或者版本库、服务名字，可以根据各个节点做不同的标不同识来区分，比如kdb.items.price
    :param debug 是否调试，默认是False：将日志写入到日志服务器，True：日志内容会在终端打印和写入日志服务器
    :param url: 需要抓取的网址，支持http://和https://
    :param params: (可选) 网址参数params={'a': 'test', 'b': 'ok'} 会在请求网址生成 /?a=test&b=ok，注意：params、data、json里面的数据都经过了url编码处理
    :param data: (可选) 发送post请求，dict类型数据。通过data参数来传递，data不光可以接受字典类型的数据，还可以接受json等格式
    :param json: (可选) 发送post请求，json类型数据。通过json参数来传递
    :param headers: (可选) 定制headers。所有的 header 值必须是 string
    :param cookies: (可选) 自定义请求的COOKIES ，可以是dict类型或者是CookieJar
    :param files: (可选) 发送文件的post类型，相当于向网站上传一张图片，文档等操作，这时要使用files参数
    :param auth: (可选) Aauth认证，支持HTTPProxyAuth、HTTPDigestAuth等认证方式.
    :param timeout: (可选) 设置超时时间，数值要求是int或者float，格式可以是tuple(连接超时时间,  读取超时时间) 或者一个超时时间数字，timeout=(3, 27) or timeout=30
    :param allow_redirects: (可选) 自动处理重定向的请求，默认是True允许重定向，允许301、302等跳转，设置False来设置不自动处理重定向，使用r.history来追踪是否有重定向
    :param proxies: (可选) 使用代理进行抓取，可以设置url、主机、方法.
    :param encoding (可选) 指定解析页面使用的编码，默认会从网页中获取编码，不需要自己指定.
    :param stream: (可选) 流下载方式，默认False，立即下载全部数据，使用requests的get下载大文件/数据时，建议使用使用stream模式，使用流文件模式
    :param verify: (可选) 是否使用SSL证书验证，requests默认是True，Req默认是False，因为有些网站使用的ssl不标准会造成出错
    :param cert: (可选) 使用自定义SSL证书，需要verify=True才生效，默认使用https连接时候获取到证书，cert是指定一个解密的证书文件来认证，加密的证书文件是无效的

        :return: 根据 fields 整形输出的数据
    """
    r = Spider()

    return r.get_result(url, **kwargs)


if __name__ == '__main__':

    url_test1 = 'http://192.168.8.99/'
    url_test = 'https://ext.henzanapp.com/api.html?path1=qihoo-mall-goodsinfo&path2=goodspricecmp&prevpop=&url=https%3A%2F%2Fdetail.tmall.com%2Fitem.htm' \
              '%3Fid%3D{0}%26ali_refid%3Da3_420432_1006%3A1102228814%3AN%3A%25E5%2587%2589%25E9%259E%258B%25E5%25A5%25B3%3Ac9fac06e8ab629323b3dcfb3bcabda90' \
              '%26ali_trackid%3D1_c9fac06e8ab629323b3dcfb3bcabda90%26spm%3Da230r.1.14.1.JmulPx%26sku_properties%3D-1%3A-1&v=v5&bfrom=normal&pop=1&cv=4.2.1.3' \
              '&hisOpn=0&toolbar_state=open&isGulike=false&mid=&tPrice=&tSale=&fromTp=0&ref=https%3A%2F%2Fdetail.tmall.com%2Fitem.htm%3Fid%3D{0}%26ali_refid' \
              '%3Da3_420432_1006%3A1102228814%3AN%3A%25E5%2587%2589%25E9%259E%258B%25E5%25A5%25B3%3Ac9fac06e8ab629323b3dcfb3bcabda90%26ali_trackid%3D1' \
              '_c9fac06e8ab629323b3dcfb3bcabda90%26spm%3Da230r.1.14.1.JmulPx%26sku_properties%3D-1%3A-1'.format(123456)

    s = Spider()
    text = s.get(url_test1)
    print(text)

    # r = Req()
    # j = r.get(url_test, debug=True)
    # print_json(j.json)
