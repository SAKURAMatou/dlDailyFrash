from django.urls import path, include
from apps.order import views as OrderView

urlpatterns = [
    path("commitOrder", OrderView.commitOrder.as_view(), name="commitOrder"),  # 订单提交页面
    path("commit", OrderView.commit.as_view(), name="commit"),  # 订单提交的方法
    path('payForOrder', OrderView.payForOrder.as_view(), name="payForOrder"),  # 具体支付的方法

]
