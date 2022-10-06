from django.urls import path
from .views import initPage

urlpatterns = [
    path('', initPage),
    path("index", initPage, name='index')
]
