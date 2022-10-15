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


print(getSortType('0'))
