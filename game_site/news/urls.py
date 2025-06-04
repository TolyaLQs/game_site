from django.urls import path
from . import views

name = 'news'

urlpatterns = [
    path('', views.NewsListView.as_view(), name='list'),
    path('<int:pk>/', views.NewsDetailView.as_view(), name='detail'),
]

