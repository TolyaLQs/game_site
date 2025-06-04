from django.urls import path
from . import views

name = 'mainapp'

urlpatterns = [
    path('', views.index, name='index'),
]

