import decimal
from functools import reduce

from django.shortcuts import render
from django.views import View

from commonUtil import DlUtil
from apps.goods.models import GoodsSKU
from django_redis import get_redis_connection


# Create your views here.


class CarView(View):
    '''添加购物车的视图方法'''

    def post(self, request):
        post = request.POST
        goodId = post.get('goodId')
        goodCount = int(post.get('goodCount'))
        # 数据校验
        if not all([goodId, goodCount]):
            return DlUtil.makeJsonResponse('0', '缺少必填')
        # 获取商品
        good = GoodsSKU.objects.filter(id=goodId).first()
        # 商品不存在时返回错误
        if good is None:
            return DlUtil.makeJsonResponse('0', '商品唯一标识错误！')
        # 判断商品库存是否够
        if goodCount > good.stock:
            return DlUtil.makeJsonResponse('0', '商品库存不足！')
        # 添加购物车；现获取redis连接
        redisConn = get_redis_connection('default')
        carKey = f'car_user_{request.user.id}'
        # 先判断当前商品是否在购物车中有，有的话数量相加，没有的话添加记录
        checkGoodInCarCount = redisConn.hget(carKey, goodId)
        if checkGoodInCarCount is not None:
            goodCount += int(checkGoodInCarCount)
        redisConn.hset(carKey, goodId, goodCount)
        countInCar = DlUtil.getUserCountInCar(request.user.id)
        return DlUtil.makeJsonResponse('1', '添加成功！', {"nowCount": countInCar})


class myCar(View):
    def get(self, request):
        '''
        我的购物车请求
        '''
        user = request.user
        carList = DlUtil.getUserCarList(user.id)
        res = []
        totalCount = 0
        totalPrice = decimal.Decimal()
        for key, value in carList.items():
            # key 商品id,value，购物车内商品数量
            good = GoodsSKU.objects.filter(id=key).first()
            if good is not None:
                # 保存商品数量，计算小计=商品单价*数量
                good.count = int(value)
                # django-redis获取到的数字都是btye类型，需要通过decode方法转成字符串；
                # 商品价格是decimal类型，需要通过decimal.Decimal进行护转化，否则无法和float int进行直接运算
                # good.amount = decimal.Decimal(value.decode()) * good.price
                good.amount = good.count * good.price
                res.append(good)
                # 计算总商品数，总价
                totalCount += good.count
                totalPrice += good.amount

        car_count = DlUtil.getUserCountInCar(request.user.id)
        return render(request, 'car.html',
                      {'carList': res, 'totalCount': totalCount,
                       'totalPrice': str(totalPrice.quantize(decimal.Decimal("0.00"))), 'car_count': car_count})


class goodInCarCountChange(View):
    def post(self, request):
        '''购物车中商品数量变更'''
        post = request.POST
        goodId = post.get('goodid')
        newCount = post.get("newcount")
        totalPrice = post.get("totalPrice")
        if not all([goodId, newCount, totalPrice]):
            return DlUtil.makeJsonResponse(msg='缺少必填项！')
        # 字符串转数字
        newCount = int(newCount)
        totalPrice = decimal.Decimal(totalPrice)
        # 校验商品是否存在
        good = GoodsSKU.objects.filter(id=goodId).first()
        if good is None:
            return DlUtil.makeJsonResponse(msg='商品错误！')
        # 判断商品库存是否够
        if newCount > good.stock:
            return DlUtil.makeJsonResponse(msg='商品库存不足！')

        # 商品数量足够时修改购物车中对应商品数量
        redisConn = get_redis_connection('default')
        carKey = f'car_user_{request.user.id}'
        # 先判断当前商品是否在购物车中是否存在，不存在时返回，不直接添加购物车
        checkGoodInCarCount = redisConn.hget(carKey, goodId)
        if checkGoodInCarCount is None:
            return DlUtil.makeJsonResponse(msg='错误，购物车中没有该商品，请手动添加')

        checkGoodInCarCount = int(checkGoodInCarCount)
        if checkGoodInCarCount > newCount:
            # 新的商品数小于之前数据表示减少
            totalPrice -= good.price
        else:
            totalPrice += good.price

        redisConn.hset(carKey, goodId, newCount)

        # TODO 购物车内商品总价，共计如何修改？总价的计算需要查库，获取商品对象，故页面展示的总价等通过js实现
        # 返回总数，以及商品价格
        totalCount = getTotalCount(redisConn, carKey)

        return DlUtil.makeJsonResponse(1, '修改成功！',
                                       {"totalPrice": str(totalPrice.quantize(decimal.Decimal("0.00"))),
                                        "totalCount": totalCount, "price": good.price})


class deleteGood(View):
    def post(self, request):
        '''购物车中商品删除'''
        post = request.POST
        goodId = post.get('goodid')
        totalPrice = post.get("totalPrice")

        if not all([goodId, totalPrice]):
            return DlUtil.makeJsonResponse(msg='缺少必填项！')

        totalPrice = decimal.Decimal(totalPrice)
        good = GoodsSKU.objects.filter(id=goodId).first()
        if good is None:
            return DlUtil.makeJsonResponse(msg='商品错误！')

        redisConn = get_redis_connection('default')
        carKey = f'car_user_{request.user.id}'
        # 查找现在购物车中的商品的数量
        nowCount = redisConn.hget(carKey, goodId)
        if nowCount is None:
            return DlUtil.makeJsonResponse(msg='购物车中不存在该商品，无需删除！')
        nowCount = int(nowCount)
        # 计算商品删除之后的总价
        totalPrice -= good.price * nowCount
        redisConn.hdel(carKey, goodId)
        # 计算删除之后的总商品数
        totalCount = getTotalCount(redisConn, carKey)

        return DlUtil.makeJsonResponse(1, '商品删除成功！',
                                       {"totalPrice": str(totalPrice), "totalCount": totalCount})


def getTotalCount(redisConn, carKey):
    '''计算商品总数，入参redisConn,key'''
    # carList = redisConn.hgetall(carKey)
    val = redisConn.hvals(carKey)
    return reduce(lambda a, b: int(a) + int(b), val)
    # total = 0
    # for key, value in carList.items():
    #     total += int(value)
    # return total
