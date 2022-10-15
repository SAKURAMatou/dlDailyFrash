# Generated by Django 3.2.16 on 2022-10-15 12:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='ordergoods',
            name='skuGuid',
            field=models.CharField(default=None, max_length=50, null=True, verbose_name='订单对应的商品guid'),
        ),
        migrations.AlterField(
            model_name='ordergoods',
            name='comment',
            field=models.CharField(default=None, max_length=500, null=True, verbose_name='商品评论'),
        ),
        migrations.AlterField(
            model_name='ordergoods',
            name='orderGuid',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='order.orderinfo', verbose_name='对应订单主键'),
        ),
        migrations.AlterField(
            model_name='ordergoods',
            name='skuCount',
            field=models.IntegerField(default=0, null=True, verbose_name='商品数量'),
        ),
        migrations.AlterField(
            model_name='ordergoods',
            name='skuPrice',
            field=models.DecimalField(decimal_places=2, default=None, max_digits=10, null=True, verbose_name='商品单价'),
        ),
    ]
