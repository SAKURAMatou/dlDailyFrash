from django.urls import path
from apps.goods import views as goodsView

urlpatterns = [
    path('', goodsView.indexView.as_view()),
    path("index", goodsView.indexView.as_view(), name='index')
]
