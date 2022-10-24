from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from itsdangerous import URLSafeTimedSerializer

from commonUtil import DlUtil
from db.MinioClientUtil import MinioClient
from .models import Address
import re

from apps.user.models import User

# Create your views here.
from ..goods.models import GoodsSKU
from ..order.models import OrderInfo, OrderGoods


@transaction.atomic
def userRegister(request):
    if request.method == 'GET':
        print(reverse('goods:index'))
        return returnRegister(request, None)
    else:
        return postUserRegister(request)


def postUserRegister(request):
    user_name = request.POST.get("user_name")
    pwd = request.POST.get("pwd")
    email = request.POST.get("email")
    allow = request.POST.get("allow")
    # 验证必填项
    if not all([user_name, pwd, email]):
        return returnRegister(request, "缺少必填项！")
    # 验证邮箱格式，
    if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
        return returnRegister(request, "邮箱格式不正确")
    # 验证是否同意
    if 'on' != allow:
        return returnRegister(request, "请先同意隐私政策")
    # 校验用户名称是否重复
    user = User.objects.filter(username=user_name).first()
    # User.objects.get(username=user_name)
    if user:
        return returnRegister(request, "用户名已存在，请重新设置用户名！")
    user = User.objects.create_user(user_name, email, pwd)
    user.is_active = 0
    user.save()
    # 发送邮件
    # senActiveEmail(user)
    print(user_name, pwd, email, allow)

    return redirect(reverse('user:login'))


def senActiveEmail(user):
    serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
    token = serializer.dumps({"userid": user.id})
    url = 'http://127.0.0.1:8000/user/active/'
    htmlMsg = f'<h1>欢迎注册{user.username}，点击下方链接激活账号,链接有效期10分钟</h1><br/><a href="{url}{token}">{url}{token}</a>'
    sender = settings.EMAIL_FROM
    send_mail('激活邮件', '', sender, [user.email], html_message=htmlMsg)


def returnRegister(request, msg):
    '''
    用于返回register.html的页面视图
    '''
    if msg is not None:
        return render(request, 'register.html', {'errorMsg': msg})
    else:
        return render(request, 'register.html')


class userRegisterView(View):
    '''
    类视图，继承django的View类，根据不同的请求方式定义对应的函数即可把对应的请求分发
    '''

    def get(self, request):
        print(reverse('goods:index'))
        return returnRegister(request, None)

    def post(self, request):
        return postUserRegister(request)


# 用户激活模块
class userActive(View):
    @transaction.atomic
    def get(self, request, token):
        # 解密
        serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
        print(settings.SECRET_KEY)
        try:
            token = serializer.loads(token, max_age=600)
            # token = {"userid": 1}
            # token的格式{"userid": user.id}
            user = User.objects.filter(id=token['userid']).first()
            if user:
                # 激活用户
                user.is_active = 1
                user.save()
                # 跳转到商品首页
                return redirect(reverse('goods:index'))
            else:
                return HttpResponse('激活连接已过期或用户不存在')
        except Exception as e:
            print(e)
            return HttpResponse('激活连接已过期')


class userLogin(View):
    def get(self, request):
        print(request.COOKIES)
        if 'username' in request.COOKIES:
            username = request.COOKIES.get("username")
            return render(request, "login.html", {"username": username, "checked": "checked"})
        return render(request, "login.html")

    def post(self, request):
        # 登陆成功返回商品首页
        username = request.POST.get("username")
        pwd = request.POST.get("pwd")
        # 校验用户
        if not all([username, pwd]):
            return render(request, "login.html", {"error": "缺少必填项"})
        # 验证用户是否存在;直接使用django提供的校验方法
        user = authenticate(username=username, password=pwd)
        if user is not None:
            login(request, user)
            user.car_count = DlUtil.getUserCountInCar(user.id)
            # 判断是否需要记录用户名
            remember = request.POST.get('remember')
            # 获取登录后所要跳转到的地址
            # 默认跳转到首页,request.GET.get()第二个入参是默认值，获取不到key时候返回
            next_url = request.GET.get('next', reverse('goods:index'))
            # 跳转到登陆成功之后的地址，并获取响应对象
            response = redirect(next_url)
            # 记住用户名
            if remember == 'on':
                # 给响应设置cookie
                response.set_cookie('username', username, max_age=7 * 24 * 3600)
            else:
                response.delete_cookie('username')

            return response
        return redirect(reverse('goods:index'))


def userLogout(request):
    '''用户退回的方法，使用django自带的退出'''
    logout(request)
    return redirect(reverse('goods:index'))


class userSite(View):
    '''
    用户中心(任何页面跳转user模块)
    '''

    def get(self, request):
        return render(request, 'user_center_info.html', {"page": "info"})


class userInfo(View):
    '''
    进入用户信息，默认打开“个人信息tab”
    '''

    def get(self, request):
        # print(request.user.is_authenticated())
        # 获取用户的默认收货地
        user = request.user
        address = Address.objects.get_defult_address(user.id)
        if address is not None:
            user.receiver = address.receiver
            user.re_address = address.re_address
            user.re_phone = address.re_phone
        return render(request, 'user_center_info.html', {"page": "info"})


class userOrder(View):
    '''
    进入用户订单
    '''

    def get(self, request):
        '''订单列表页面'''
        user = request.user
        get = request.GET
        pageIndex = get.get("pageIndex")
        if not pageIndex:
            # 当没有传当前页码时默认第一页
            pageIndex = 1
        # 查询订单表获取用户订单信息
        allOrder = OrderInfo.objects.filter(userId=user).order_by("create_time")
        if allOrder:
            paginator = Paginator(allOrder, 2)
            # 分页之后的对象
            page = paginator.get_page(pageIndex)
            # 获取订单中的每一个商品信息
        for order in page.object_list:
            orderGoods = OrderGoods.objects.filter(orderGuid=order)
            # 根据订单商品表中的商品主键找到商品；一个订单对应多个商品，应该循环
            if orderGoods:
                orderGoods = list(orderGoods)
                for orderGood in orderGoods:
                    good = GoodsSKU.objects.filter(id=orderGood.skuGuid).first()
                    if good:
                        orderGood.good = good
                        # 计算订单内每个商品的小计
                    orderGood.amount = orderGood.skuCount * orderGood.skuPrice
            # 把订单商品添加给每一个订单
            order.orderGoods = orderGoods
            order.statusText = getTextFromChoice(OrderInfo.OrderInfo_status, order.status)

        # 对页码进行渲染；总页数小于5展示全部
        # 如果当前页码小于3展示1-5
        num_pages = paginator.num_pages
        pageList = []
        if num_pages < 5:
            pageList = range(1, num_pages + 1)
        elif page.number:
            pageList = range(1, 6)
        elif num_pages - page.number < 3:
            # 当前是后3页，则展示最后5页
            pageList = range(num_pages - 4, num_pages + 1)
        else:
            pageList = range(page.number - 2, page.number + 3)
        page.has_previous()
        context = {
            "orderList": page.object_list,
            "pageList": pageList,
            "pager": page
        }
        return render(request, 'user_center_order.html', context)


def getTextFromChoice(choiceTruple, key):
    for i in choiceTruple:
        if key == i[0]:
            return i[1]


class userAddress(View):
    '''
    用户收货地管理
    '''

    def get(self, request):
        # 查询所有的收货地址
        resAddress = getAllAddress()
        return render(request, 'user_center_site.html', {"page": "address", "allAddress": resAddress})

    @transaction.atomic
    def post(self, request):
        re_phone = request.POST.get("re_phone")
        zip_code = request.POST.get("zip_code")
        re_address = request.POST.get("re_address")
        receiver = request.POST.get("receiver")
        # 校验必填
        if not all([re_phone, re_address, receiver]):
            resAddress = getAllAddress()
            return render(request, 'user_center_site.html',
                          {"page": "address", "errorMsg": "缺少必填项！", "allAddress": resAddress})
        # 创建新的收货地址
        user = request.user
        defaultAddress = Address.objects.get_defult_address(user.id)
        is_defalut = defaultAddress is None
        Address.objects.create(userID=user, re_phone=re_phone, zip_code=zip_code, re_address=re_address,
                               receiver=receiver, is_defalut=is_defalut)
        # 返回页面所有的收货地址
        resAddress = getAllAddress()
        return render(request, 'user_center_site.html', {"page": "address", "allAddress": resAddress})


def getAllAddress():
    allAddress = Address.objects.all()
    resAddress = []
    for address in allAddress:
        resAddress.append(
            f"{address.re_address}（{address.receiver} 收）{address.re_phone[0:3]}***{address.re_phone[-4:]}")
    return resAddress


@transaction.atomic()
def uploadFile(request):
    file = request.FILES.get("upload_file_form")
    client = MinioClient()
    url = client.upLoadFile(file.name, file)
    print("FILES:", request.FILES)
    print(url)
