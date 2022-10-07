from django.urls import path
from apps.user import views as userViews
from django.contrib.auth.decorators import login_required

urlpatterns = [
    # path('register', userViews.userRegister)
    path('register', userViews.userRegisterView.as_view(), name="register"),
    path('login', userViews.userLogin.as_view(), name='login'),
    path('active/<str:token>', userViews.userActive.as_view(), name="active"),
    path("", login_required(userViews.userInfo.as_view()), name="user"),  # 进入用户中心映射
    path("info", login_required(userViews.userInfo.as_view()), name='userInfo'),  # 用户信息
    path("order", login_required(userViews.userOrder.as_view()), name="userOrder"),  # 用户订单
    path("address", login_required(userViews.userAddress.as_view()), name="userAddress"),  # 用户收货地址
    path("logout", userViews.userLogout, name="userLogout")
]
