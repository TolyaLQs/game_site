from django.urls import path
from . import views

urlpatterns = [
    path('', views.GameListView.as_view(), name='game_list'),
    path('game/<slug:slug>/', views.GameDetailView.as_view(), name='game_detail'),
    # path('genre/<slug:slug>/', views.GameByGenreView.as_view(), name='games_by_genre'),
]
