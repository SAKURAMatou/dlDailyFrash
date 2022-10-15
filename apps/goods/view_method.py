from django_redis import get_redis_connection

'''
view所需要的方法单独存放在一个文件
'''


def setUserLookHistory(user, goodId):
    if user.is_authenticated:
        #     设置本次浏览历史
        redisConn = get_redis_connection('default')
        historyKey = f'history_{user.id}'
        # 先把当前商品删除，防止多次出现
        redisConn.lrem(historyKey, 0, goodId)
        # 再添加进列表
        redisConn.lpush(historyKey, goodId)
        # 防止数据过多需要限制列表的长度
        redisConn.ltrim(historyKey, 0, 4)


LIST_SORT = (('0', 'create_time'), ('1', 'price'), ('2', 'saleCount'))


def getSortType(key):
    '''默认按价格排序'''
    for t in LIST_SORT:
        if t[0] == key:
            return t[1]
    return "price"
