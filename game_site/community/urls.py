from django.urls import path
from . import views

name = 'community'

urlpatterns = [
    path('', views.index, name='list'),
]

