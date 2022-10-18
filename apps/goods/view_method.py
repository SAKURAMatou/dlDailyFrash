from django_redis import get_redis_connection

'''
view所需要的方法单独存放在一个文件
'''
LIST_SORT = (('0', 'create_time'), ('1', 'price'), ('2', 'saleCount'))


def getSKUSortFile(key):
    '''默认按价格排序'''
    for t in LIST_SORT:
        if t[0] == key:
            return t[1]
    return "price"
