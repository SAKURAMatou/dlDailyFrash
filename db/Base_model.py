from django.db import models


class BaseModel(models.Model):
    '''
    所有数据表对象model对象使用的父类，
    '''
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    is_delete = models.BooleanField(default=False, verbose_name='是否删除')

    class Meta:
        # 说明是一个抽象模型类
        abstract = True


class ImgFile(BaseModel):
    '''图片信息表'''
    status_choice = ((0, '下架'), (1, '上架'))
    imgUrl = models.CharField(max_length=100, verbose_name='图片地址')
    status = models.SmallIntegerField(choices=status_choice, default=1)

    class Meta:
        db_table='img_file'
        verbose_name = '图片附件表'
        verbose_name_plural = verbose_name
