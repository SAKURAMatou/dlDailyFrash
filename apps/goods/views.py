from django.shortcuts import render, redirect
from django.views import View
from django_redis import get_redis_connection
from  django.core.paginator import Paginator

from apps.goods import view_method as viewMethod
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
        # 根据id获取商品详情
        goodDetail = GoodsModels.GoodsSKU.objects.filter(id=goodId).first()
        if goodDetail is None:
            # 当id对应的数据不存在时返回首页
            return redirect('goods:index')

        user = request.user
        # 设置用户的浏览记录
        viewMethod.setUserLookHistory(user, goodId)
        # 获取类别
        goodsType = GoodsModels.GoodsType.objects.all()
        # 尝试自己查询数据
        goodDetail.imgUrl = GoodsModels.GoodsSKU.objects.get_imgUrl(goodDetail.imgGuid.guid)

        # 商品详情页的推荐使用相同类型的新添加商品
        newSku = GoodsModels.GoodsSKU.objects.get_new(goodDetail)
        # 手动获取商品对应的大类spu的详情、
        goodDetail.detail1 = GoodsModels.GoodsSKU.objects.get_detail(goodDetail)
        return render(request, 'detail.html', {'types': goodsType, 'goodDetail': goodDetail, 'newSku': newSku})


class goodsList(View):

    def get(self, request, goodType):
        # 获取类别
        goodsType = GoodsModels.GoodsType.objects.all()
        pageIndex = 0 if request.GET.get("pageIndex") is None else request.Get.get("pageIndex")
        pageSize = 0 if request.GET.get("pageSize") is None else request.Get.get("pageSize")
        orderType = 0 if request.GET.get("orderType") is None else request.Get.get("orderType")
        sortType = viewMethod.getSortType(request.Get.get("sortType"))



        return render(request, 'list_goods.html')
