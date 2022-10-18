from django.views import View
from commonUtil import DlUtil
from apps.goods.models import GoodsSKU
from django_redis import get_redis_connection


# Create your views here.


class CarView(View):
    '''添加购物车的视图方法'''

    def post(self, request):
        post = request.POST
        goodId = post.get('goodId')
        goodCount = int(post.get('goodCount'))
        # 数据校验
        if not all([goodId, goodCount]):
            return DlUtil.makeJsonResponse('0', '缺少必填')
        # 获取商品
        good = GoodsSKU.objects.filter(id=goodId).first()
        # 商品不存在时返回错误
        if good is None:
            return DlUtil.makeJsonResponse('0', '商品唯一标识错误！')
        # 判断商品库存是否够
        if goodCount > good.stock:
            return DlUtil.makeJsonResponse('0', '商品库存不足！')
        # 添加购物车；现获取redis连接
        redisConn = get_redis_connection('default')
        carKey = f'car_user_{request.user.id}'
        # 先判断当前商品是否在购物车中有，有的话数量相加，没有的话添加记录
        checkGoodInCarCount = redisConn.hget(carKey, goodId)
        if checkGoodInCarCount is not None:
            goodCount += int(checkGoodInCarCount)
        redisConn.hset(carKey, goodId, goodCount)
        countInCar = DlUtil.getUserCountInCar(request.user.id)
        return DlUtil.makeJsonResponse('1', '添加成功！', {"nowCount": countInCar})
