from django.urls import path, include
from apps.car.views import CarView

urlpatterns = [
    path('addCar', CarView.as_view(), name='addCar')
]
