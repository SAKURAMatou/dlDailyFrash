from django.urls import path, include
from apps.car import views as CarViews

urlpatterns = [
    path('addCar', CarViews.CarView.as_view(), name='addCar'),
    path("myCar", CarViews.myCar.as_view(), name='myCar')  # 我的购物车页面
]
