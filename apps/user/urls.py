from django.urls import path
from apps.user import views as userViews

urlpatterns = [
    # path('register', userViews.userRegister)
    path('register', userViews.userRegisterView.as_view()),
    path('login', userViews.userLogin.as_view(), name='login'),
    path('active/<str:token>', userViews.userActive.as_view(), name="active")
]
