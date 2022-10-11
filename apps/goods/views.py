from django.shortcuts import render
from django.views import View


# Create your views here.
def initPage(request):
    '''用户首页'''
    return render(request, 'index.html')


class indexView(View):
    '''首页view视图类'''

    def get(self, request):
        return render(request, 'index.html')
