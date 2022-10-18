from django_redis import get_redis_connection
from django.http import JsonResponse


def makeJsonResponse(code: int = 0, msg: str = '操作失败', data: dict = None):
    res = {"code": code, 'msg': msg}
    if data is not None:
        res['data'] = data
    return JsonResponse(res)


def getUserCountInCar(userId):
    '''获取用户购物车中上商品数量'''
    redisConn = get_redis_connection('default')
    count = redisConn.hlen(f'car_user_{userId}')
    return int(count) if count is not None else 0


def setUserLookHistory(user, goodId):
    '''设置用户的浏览记录'''
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
