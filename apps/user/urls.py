from django.urls import path
from apps.user import views as userViews

urlpatterns = [
    # path('register', userViews.userRegister)
    path('register', userViews.userRegisterView.as_view()),
    path('login', userViews.userLogin.as_view(), name='login'),
    path('active/<str:token>', userViews.userActive.as_view(), name="active"),
    path("", userViews.userSite.as_view(), name="user"),  # 进入用户中心映射
    path("info", userViews.userInfo.as_view(), name='userInfo'),  # 用户信息
    path("order", userViews.userOrder.as_view, name="userOrder")  # 用户订单
]
