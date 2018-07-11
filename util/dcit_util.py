# -*- coding: utf-8 -*-
"""
Dict相关工具库

"""
import re


def unpack_dict(dict_obj, params, default=None):
    """
    取嵌套字典的值
    :param dict_obj: 输入数据，dict类型
    :param params: 取值参数，支持str和list类型， 如：unpack_dict(data, 'mods.itemlist.data')或 unpack_dict(data, ['mods', 'itemlist', 'data'])
    :param default: 取值错误时或者没有数据时候，返回默认值，如果没有指定默认值就输出：{}
    :return: 取值数据

    演示：
    obj = {
        'app': {
            'msg': 'ok',
            'list': [{
                'msg': 'list'
            }]
        },
        'error': 'no'
    }

    unpack_dict(obj, 'app.msg')
    # ===> ok

    unpack_dict(obj, 'app.list[0].msg')
    # ===> list

    unpack_dict(obj, 'error.msg')
    # ===> {}

    unpack_dict(obj, 'app.msg2', None)
    # ===> None
    """
    if default is None:
        default = {}

    # 判断参数类型
    if not isinstance(dict_obj, dict) or not isinstance(params, (str, list)):
        return default

    # 解析结构
    if isinstance(params, str):
        params = params.split('.')

    parent = dict_obj
    for p in params:
        # 判断是否取 List 对象
        ret = re.search('(?P<name>[^\.\\[]+)(?P<indexs>(\[-?\d+\])+)', p)

        if ret:
            name = ret.group('name')
            indexs = ret.group('indexs')

            list_obj = parent.get(name)

            if list_obj:
                list_indexs = re.findall('-?\d+', indexs)

                for index in list_indexs:
                    index = int(index)
                    list_obj = list_obj[index]

                parent = list_obj
                continue
            else:
                return default
        elif isinstance(parent, dict):
            parent = parent.get(p)
        else:
            return default

    if parent is None:
        return default

    return parent


if __name__ == '__main__':
    obj = {
        'app': {
            'msg': 'ok',
            'list': [{
                'msg': 'list'
            }]
        },
        'error': 'no'
    }

    print(unpack_dict(obj, 'app.msg'))
    # ===> ok

    print(unpack_dict(obj, 'app.list[0].msg'))
    # ===> list

    print(unpack_dict(obj, 'error.msg'))
    # ===> {}

    print(unpack_dict(obj, 'app.msg2', None))
    # ===> None

    print(unpack_dict({
        'ips': [
            [
                {
                    'a': [
                        1, 2, 3
                    ]
                }
            ]
        ]
    }, 'ips[0][0].a[-1]'))
    # ===> 3
