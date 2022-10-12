from django.db import models
from db.Base_model import BaseModel
import uuid


# Create your models here.


class OrderInfo(BaseModel):
    '''订单信息表'''
    payWay_chioce = ((1, '支付宝'), (2, '微信支付'), (3, '信用卡'))
    OrderInfo_status = ((0, '提交订单'), (1, '未支付'), (2, '已支付'), (3, '已发货'), (4, '待评价'), (5, '已完成'))
    guid = models.CharField(primary_key=True, default=uuid.uuid4(), verbose_name='订单主键，使用UUID')
    userId = models.ForeignKey('User', on_delete=models.CASCADE, verbose_name='用户主键')
    payWay = models.SmallIntegerField(choices=payWay_chioce, default=1, verbose_name='支付方式')
    goodsCount = models.SmallIntegerField(default=0, verbose_name='订单内商品总数')
    payGoods = models.DecimalField(default=0.00, max_digits=10, decimal_places=2, verbose_name="订单商品总金额")
    payTraffic = models.DecimalField(default=0.00, max_digits=10, decimal_places=2, verbose_name="订单运费")
    status = models.SmallIntegerField(choices=OrderInfo_status, default=0, verbose_name='订单状态')

    class Meta:
        db_table = 'dl_order_info'
        verbose_name = '订单信息表'
        verbose_name_plural = verbose_name


class OrderGoods(BaseModel):
    '''订单商品表'''
    guid = models.CharField(primary_key=True, default=uuid.uuid4(), verbose_name='订单中的商品信息主键，使用UUID')
    orderGuid = models.ForeignKey(OrderInfo, on_delete=models.CASCADE, verbose_name='对应订单主键')
    skuCount = models.IntegerField(default=0, verbose_name='商品数量')
    skuPrice = models.DecimalField(decimal_places=2, max_digits=10, verbose_name='商品单价')
    comment = models.CharField(max_length=500, verbose_name='商品评论')

    class Meta:
        db_table = 'dl_order_goods'
        verbose_name = '订单商品表'
        verbose_name_plural = verbose_name
