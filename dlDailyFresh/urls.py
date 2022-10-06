"""dlDailyFresh URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path

''' 
   django2.0使用include方法时，指定了namespace的情况下第一个入参必须是一个元祖;如下的代码决定元祖第一个数据是映射，第二个是appname和namespace相同
    if isinstance(arg, tuple):
       # Callable returning a namespace hint.
       try:
           urlconf_module, app_name = arg
   '''
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('goods.urls')),
    re_path(r'^tinymce/', include('tinymce.urls')),
    path('user/', include(('user.urls', 'user'), namespace='user')),  # 用户模块
    path('car/', include(('car.urls', 'car'), namespace='car')),  # 购物车模块
    path('order/', include(('order.urls', 'order'), namespace='order')),  # 订单模块
    path('goods/', include(('goods.urls', 'goods'), namespace='goods'))  # 商品模块
]
