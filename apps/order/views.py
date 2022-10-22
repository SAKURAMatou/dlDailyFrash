import decimal

from django.shortcuts import render, redirect
from django.urls import reverse
from django.db import transaction

from django.views import View

# Create your views here.
from django_redis import get_redis_connection

from apps.goods.models import GoodsSKU
from commonUtil import DlUtil
from apps.user.models import Address

import json


@transaction.atomic
def terst():
    savePoint = transaction.savepoint()
    try:
        '''逻辑代码'''
    except Exception as e:
        '''异常时回滚到指定点'''
        transaction.savepoint_rollback(savePoint)
    finally:
        transaction.savepoint_commit(savePoint)
    return ''


class commitOrder(View):
    def get(self, request):
        return render(request, 'place_order_order.html')

    def post(self, request):
        post = request.POST
        ids = post.getlist('checkId')
        # 缺少入参时返回购物车列表
        if not ids:
            return redirect(reverse("car:myCar"))

        # 查找购物车找到对应的商品以及数量，
        user = request.user
        totalCount = 0
        totalPrice = decimal.Decimal()
        res = []

        redisConn = get_redis_connection('default')
        carKey = f'car_user_{request.user.id}'
        for goodId in ids:
            # key 商品id,value，购物车内商品数量
            good = GoodsSKU.objects.filter(id=goodId).first()
            if good is not None:
                value = redisConn.hget(carKey, goodId)
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
        # 获取用户的默认收货地
        # defaultAddress = Address.objects.get_defult_address(user.id)
        addressList = Address.objects.all()
        if addressList is None:
            # 返回哟洪湖地址编辑页面
            return redirect(reverse("user:address"))

        trafficPay = 10
        totalPay = trafficPay + totalPrice

        contex = {
            "trafficPay": trafficPay,
            "totalPay": totalPay,
            'list': res,
            'addresses': addressList,
            "totalCount": totalCount,
            "totalPrice": totalPrice,
            'ids': ids
        }

        return render(request, 'place_order_order.html', contex)


class commit(View):
    def post(self, request):
        post = request.POST
        address = post.get('address')
        payWay = post.get('payWay')
        goods = post.get('goods')
        goods = json.loads(goods.replace("'", "\""))
        print(address, payWay, goods, type(goods))

        return DlUtil.makeJsonResponse(1, "提交成功！")
