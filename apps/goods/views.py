from django.shortcuts import render
from django.views import View
from django_redis import get_redis_connection

from apps.goods import models as GoodsModels


# Create your views here.
def initPage(request):
    '''用户首页'''
    return render(request, 'index_goods.html')


class indexView(View):
    '''首页view视图类'''

    def get(self, request):
        # 获取首页商品种类信息
        goodsType = GoodsModels.GoodsType.objects.all()
        # 获取首页轮播商品信息
        goodsBanner = GoodsModels.IndexGoodsBanner.objects.all().order_by("index")
        # 获取活动信息
        promotionBanner = GoodsModels.IndexPromotionBanner.objects.all().order_by("index")
        # 每种商品下的子类
        # typeGoodsBanner = GoodsModels.IndexTypeGoodsBanner.objects.all()
        for type in goodsType:
            textBanner = GoodsModels.IndexTypeGoodsBanner.objects.filter(type=type, display_type=0)
            imgBanner = GoodsModels.IndexTypeGoodsBanner.objects.filter(type=type, display_type=1)
            type.textBanner = textBanner
            type.imgBanner = imgBanner
        car_count = 0
        # 判断用户是否登录
        user = request.user
        if user.is_authenticated:
            redisConn = get_redis_connection('default')
            car_count = redisConn.hlen(f'car_{user.id}')

        context = {
            'goodsType': goodsType,
            'goodsBanner': goodsBanner,
            'promotionBanner': promotionBanner,
            'car_count': car_count
        }
        return render(request, 'index_goods.html', context)


class goodsDetail(View):
    '''商品详情页面'''

    def get(self, request, goodId):
        user = request.user
        if user.is_authenticated:
            #     设置本次浏览历史
            redisConn = get_redis_connection('default')
            historyKey = f'history_{user.id}'
            # 先把当前商品删除，防止多次出现
            redisConn.lrem(historyKey, 0, goodId)
            # 再添加进列表
            redisConn.lpush(historyKey, goodId)
            # 防止数据过多需要限制列表的长度
            redisConn.ltrim(historyKey, 0, 4)

        return render(request, 'detail_goods.html')
