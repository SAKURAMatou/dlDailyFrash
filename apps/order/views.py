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
from apps.order.PayUtil import PayUtil
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
        orderSavePoint = transaction.savepoint()
        # 后期本次订单中的商品信息，包含商品的数量
        try:
            for goodId in goods:
                # good = GoodsSKU.objects.filter(id=goodId).first()
                # 通过select for update进行加锁；事务提交之后锁释放
                good = GoodsSKU.objects.select_for_update().get(id=goodId)
                # 并发场景模拟获取锁之后暂停10s以供操作另一个账号提交订单
                # import time
                # time.sleep(10)
                if good:
                    value = redisConn.hget(carKey, goodId)
                    if value:
                        good.count = int(value)
                        # TODO 商品库存和本次购买数量的验证
                        if good.count > good.stock:
                            print(f'{request.user.username}购买商品{good.goodName}库存不足')
                            raise Exception("库存不足")
                        print(f'{request.user.username}购买商品{good.goodName}成功')
                        stock = good.stock - good.count
                        totalCount += good.count
                        totalPrice += good.count * good.price

                        goodList.append(good)
                        # 修改商品表中的库存记录
                        saleCount = good.saleCount + good.count
                        GoodsSKU.objects.filter(id=goodId).update(stock=stock, saleCount=saleCount)
                    else:
                        raise Exception(f'{good.goodName}商品订单已经提交，请勿重复提交')

                else:
                    raise Exception(f"编号{goodId}的商品不存在！")
        except Exception as e:
            transaction.savepoint_rollback(orderSavePoint)
            return DlUtil.makeJsonResponse(msg=str(e))

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


class payForOrder(View):
    def post(self, request):
        '''订单支付方法，需要根据支付方式调用不同的支付平台api，暂时不具体对接支付平台，只做演示'''
        post = request.POST
        user = request.user
        # 获取定点标识用于构成订单相关信息
        orderId = post.get("orderId")
        if not orderId:
            DlUtil.makeJsonResponse("缺少必填项！")
        orderInfo = OrderInfo.objects.filter(guid=orderId).first()

        if not orderInfo:
            DlUtil.makeJsonResponse("订单信息错误！")

        # 订单存在时查找订单总价，根据支付方式执行不同的发放
        totalprice = orderInfo.payGoods + orderInfo.payTraffic
        payUtil = PayUtil(orderInfo.payWay, totalprice, orderInfo.tradeNo)
        payUtil.handlePay()
        # print(reverse('order:simulation'))
        return DlUtil.makeJsonResponse(1, "支付请求成功！", {"payAddress": reverse('order:simulation')})


def openPaySimulation(request):
    return render(request, 'paysimulation.html')


class checkPay(View):
    def post(self, request):
        '''检查订单状态'''
        post = request.POST
        user = request.user
        orderId = orderId = post.get("orderId")

        if not orderId:
            DlUtil.makeJsonResponse("缺少必填项！")
        orderInfo = OrderInfo.objects.filter(guid=orderId).first()
        if not orderInfo:
            DlUtil.makeJsonResponse("订单信息错误！")

        # 调用支付宝接口检查支付结果
        return DlUtil.makeJsonResponse(1, "支付结果检查请求成功！", {"result": random()})
