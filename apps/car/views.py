import decimal

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

        return render(request, 'car_car.html',
                      {'carList': res, 'totalCount': totalCount,
                       'totalPrice': str(totalPrice.quantize(decimal.Decimal("0.00")))})


class goodInCarCountChange(View):
    def post(self, request):
        '''购物车中商品数量变更'''
        post = request.POST
        goodId = post.get('goodid')
        newCount = post.get("newcount")
        if all([goodId, newCount]):
            return DlUtil.makeJsonResponse(msg='缺少必填项！')
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

        checkGoodInCarCount = newCount
        redisConn.hset(carKey, goodId, checkGoodInCarCount)
        countInCar = DlUtil.getUserCountInCar(request.user.id)
        # TODO 购物车内商品总价，共计如何修改
        return DlUtil.makeJsonResponse(1, '修改成功！', {"countInCar": countInCar})
