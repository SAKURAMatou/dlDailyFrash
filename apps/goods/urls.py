from django.urls import path
from apps.goods import views as goodsView

urlpatterns = [
    path('', goodsView.indexView.as_view()),
    path("index", goodsView.indexView.as_view(), name='index'),
    path('detail/<str:goodId>', goodsView.goodsDetail.as_view(), name='detail'),
    path('list/<str:goodType>', goodsView.goodsList.as_view(), name='list'),
]
