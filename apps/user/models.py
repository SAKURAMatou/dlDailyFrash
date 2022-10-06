from django.contrib.auth.models import AbstractUser
from django.db import models
from db.Base_model import BaseModel


# Create your models here.

class User(AbstractUser, BaseModel):
    class Meta:
        db_table = 'dl_user'  # 指定表表名
        verbose_name = '用户'
        verbose_name_plural = verbose_name


class Address(BaseModel):
    userID = models.ForeignKey("User", verbose_name="地址所属用户", on_delete=models.CASCADE)  # 外键需要指定删除之后的操作
    receiver = models.CharField(max_length=50, verbose_name="收件人")
    re_address = models.CharField(max_length=50, verbose_name="收件地址")
    re_phone = models.CharField(max_length=20, verbose_name="收件人号码")
    is_defalut = models.BooleanField(default=True, verbose_name="是否是默认收货地址")
    zip_code = models.CharField(max_length=6, null=True, verbose_name='邮政编码')

    class Meta:
        db_table = 'dl_address'
        verbose_name = '收货地址'
        verbose_name_plural = verbose_name
