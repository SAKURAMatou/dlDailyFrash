from django.shortcuts import render
from django.http import HttpResponse


# Create your views here.
def initPage(request):
    return HttpResponse("欢迎来到商品主页！")
