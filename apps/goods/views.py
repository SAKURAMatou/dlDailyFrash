from django.shortcuts import render
from django.views import View
from apps.goods.models import GoodsType


# Create your views here.
def initPage(request):
    '''用户首页'''
    return render(request, 'index.html')


class indexView(View):
    '''首页view视图类'''

    def get(self, request):
        # 获取首页商品种类信息
        goodsType = GoodsType.objects.all()
        # 获取首页轮播商品信息

        # 获取活动信息
        # 获取购物车中商品数量
        return render(request, 'index.html')
