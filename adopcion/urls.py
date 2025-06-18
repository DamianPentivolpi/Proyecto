from django.urls import path
from .views import registro,index,lista



urlpatterns = [
    path('', index),
    path('registro/', registro),
    path('lista/', lista)

]