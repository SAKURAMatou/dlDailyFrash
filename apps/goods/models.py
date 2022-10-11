from django.db import models
from db.Base_model import BaseModel


# Create your models here.

class GoodsType(models):
    '''商品类型模型类'''
    name = models.CharField(max_length=20, verbose_name="种类名称")
    logo = models.CharField(max_length=50, verbose_name="logo图片地址")
    image = models.ImageField(upload_to='type', verbose_name='商品类型图片')
    imgurl = models.CharField(max_length=100, verbose_name="商品种类图片地址")

    class Meta:
        db_table = 'dl_goodsType'
        verbose_name = '商品种类'
        verbose_name_plural = verbose_name


class GoodsSKU(models):
    '''具体的商品表实体类'''
    status_choice = ((0, '下架'), (1, '上架'))
    priceUnit_choice = ((1, '元'), (2, '美元'), (3, '港币'))
    goodName = models.CharField(max_length=50, verbose_name='商品名称')
    goodIntorduction = models.CharField(max_length=500, verbose_name='商品简介')
    price = models.DecimalField(decimal_places=2, max_digits=8, verbose_name='价格')
    priceUnit = models.SmallIntegerField(choices=priceUnit_choice, default=1, verbose_name='价格单位')
    stock = models.IntegerField(default=1, verbose_name='库存')
    status = models.SmallIntegerField(default=1, choices=status_choice, verbose_name='商品状态')
    goodType = models.ForeignKey('GoodsType', on_delete=models.DO_NOTHING, verbose_name='商品种类')
    sealeCount = models.IntegerField(default=0, verbose_name='商品销量')
    img = models.ForeignKey('imgFile', on_delete=models.DO_NOTHING, verbose_name='图片id')  # 一个商品可以由多个图片；同一个id关联图片信息表


class imgFile(models):
    '''图片信息表'''
    status_choice = ((0, '下架'), (1, '上架'))
    imgUrl = models.CharField(max_length=100, verbose_name='图片地址')
    status = models.SmallIntegerField(choices=status_choice, default=1)
