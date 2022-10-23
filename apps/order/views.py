import decimal
import math
import uuid
from random import random

from django.shortcuts import render, redirect
from django.urls import reverse
from django.db import transaction

from django.views import View

# Create your views here.
from django_redis import get_redis_connection
import time
from apps.goods.models import GoodsSKU
from apps.order.models import OrderInfo, OrderGoods
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
                if value:
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
    @transaction.atomic
    def post(self, request):
        '''订单的提交后台'''
        post = request.POST
        addressId = post.get('address')
        payWay = post.get('payWay')
        goods = post.get('goods')
        goods = json.loads(goods.replace("'", "\""))
        print(addressId, payWay, goods, type(goods))

        # 必填项验证
        if not all([addressId, payWay, goods]):
            return DlUtil.makeJsonResponse(msg='缺少必填项！')
        # 校验收货地址是否存在
        address = Address.objects.filter(id=addressId).first()
        if not address:
            return DlUtil.makeJsonResponse(msg='收货地址异常！')
        # 校验支付方式
        flag = False
        payWay = int(payWay)
        for t in OrderInfo.payWay_chioce:
            if payWay == t[0]:
                flag = True
                break
        if not flag:
            return DlUtil.makeJsonResponse(msg='支付方法错误！')

        # 创建订单
        # 获取购物车内的商品信息
        redisConn = get_redis_connection('default')
        carKey = f'car_user_{request.user.id}'
        goodList = []
        totalCount = 0
        totalPrice = decimal.Decimal()
        # 后期本次订单中的商品信息，包含商品的数量
        try:
            for goodId in goods:
                good = GoodsSKU.objects.filter(id=goodId).first()
                if good:
                    value = redisConn.hget(carKey, goodId)
                    if value:
                        good.count = int(value)
                        totalCount += good.count
                        totalPrice += good.count * good.price
                        goodList.append(good)
                    else:
                        raise Exception(f'{good.goodName}商品订单已经提交，请勿重复提交')

                else:
                    raise Exception(f"编号{goodId}的商品不存在！")
        except Exception as e:
            return DlUtil.makeJsonResponse(msg=str(e))

        orderSavePoint = transaction.savepoint()
        try:
            # TODO  创建订单信息dl_order_info表记录
            guid = uuid.uuid4()
            user = request.user
            tradeNo = time.strftime('%Y%m%d%H%M%S', time.localtime()) + str(math.trunc(random() * 10000))
            orderInfo = OrderInfo.objects.create(guid=guid, userId=user, payWay=payWay, goodsCount=totalCount,
                                                 payGoods=totalPrice,
                                                 payTraffic=10, addr=address, tradeNo=tradeNo)

            # TODO 订单商品表中插入记录，同时需要修改商品的剩余数量
            for good in goodList:
                # 创建OrderGoods
                OrderGoods.objects.create(guid=uuid.uuid4(), orderGuid=orderInfo, skuCount=good.count,
                                          skuPrice=good.price,
                                          skuGuid=good.id)
                # TODO 商品库存和本次购买数量的验证
                stock = good.stock - good.count
                # GoodsSKU.objects.update(id=good.id, stock=stock)

            # TODO 清除用户购物车中提交的订单记录
            # map(lambda a: a.encode(), goods)
            redisConn.hdel(carKey, *goods)
            transaction.savepoint_commit(orderSavePoint)
        except Exception as e:
            # 插入订单数据时出现异常回滚
            transaction.savepoint_rollback(transaction)
            return DlUtil.makeJsonResponse("服务器异常！")

        return DlUtil.makeJsonResponse(1, "提交成功！")
