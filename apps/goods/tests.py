from django.test import TestCase

# from apps.goods.view_method import LIST_SORT

# Create your tests here.
LIST_SORT = (('0', 'create_time'), ('1', 'price'), ('2', 'saleCount'))
print(LIST_SORT.count(0))


def getSortType(key):
    '''默认按价格排序'''
    for t in LIST_SORT:
        if t[0] == key:
            return t[1]
    return "price"


# print(getSortType('0'))

import jieba

# jieba.enable_paddle()  # 启动paddle模式。 0.40版之后开始支持，早期版本不支持
strs = ["我来到北京清华大学", "乒乓球拍卖完了", "中国科学技术大学"]
for str in strs:
    seg_list = jieba.cut(str, use_paddle=True)  # 使用paddle模式
    print("Paddle Mode: " + '/'.join(list(seg_list)))

seg_list = jieba.cut("我来到北京清华大学", cut_all=True)
print("Full Mode: " + "/ ".join(seg_list))  # 全模式

seg_list = jieba.cut("我来到北京清华大学", cut_all=False)
print("Default Mode: " + "/ ".join(seg_list))  # 精确模式

seg_list = jieba.cut("他来到了网易杭研大厦")  # 默认是精确模式
print(", ".join(seg_list))

seg_list = jieba.cut_for_search("小明硕士毕业于中国科学院计算所，后在日本京都大学深造")  # 搜索引擎模式
print(", ".join(seg_list))

from whoosh.analysis import StemmingAnalyzer
import jieba
from whoosh.analysis import Tokenizer, Token


class ChineseTokenizer(Tokenizer):
    def __call__(self, value, positions=False, chars=False, keeporiginal=False, removestops=True, start_pos=0,
                 start_char=0, mode='', **kwargs):
        t = Token(positions, chars, removestops=removestops, mode=mode, **kwargs)
        seglist = jieba.cut(value, cut_all=True)
        for item in seglist:
            t.orginal = t.text = item
            t.boost = 1.0
            if positions:
                t.pos = start_pos + value.find(item)
            if chars:
                t.startchar = start_char + value.find(item)
                t.endchar = start_char + value.find(item) + len(item)
            yield t


def ChineseAnalyzer():
    return ChineseTokenizer()
