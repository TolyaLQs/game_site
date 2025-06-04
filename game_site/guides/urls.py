from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

name = 'guides'

urlpatterns = [
    path('', views.GuideListView.as_view(), name='list'),
    path('<int:pk>/', views.GuideDetailView.as_view(), name='detail'),
]

