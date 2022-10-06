from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.conf import settings
from django.core.mail import send_mail
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
import re

from apps.user.models import User


# Create your views here.

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
    #
    senActiveEmail(user)
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
            # 判断是否需要记录用户名
            remember = request.POST.get('remember')
            # 获取登录后所要跳转到的地址
            # 默认跳转到首页
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


class userInfo(View):
    '''
    进入用户信息
    '''

    def get(self, request):
        return render(request, 'user_center_info.html')


class userOrder(View):
    '''
    进入用户订单
    '''

    def get(self, request):
        return render(request, 'user_center_order.html')


class userSite(View):
    '''
    用户中心
    '''
    def get(self, request):
        return render(request, 'user_center_site.html')
