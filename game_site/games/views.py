from django.shortcuts import render

# Create your views here.
from django.views.generic import ListView, DetailView
from .models import Game, Genre


class GameListView(ListView):
    model = Game
    template_name = 'games/game_list.html'
    paginate_by = 12

    def get_queryset(self):
        queryset = super().get_queryset()
        # Фильтрация по платформе
        platform = self.request.GET.get('platform')
        if platform:
            queryset = queryset.filter(platforms=platform)
        # Фильтрация по жанру
        genre_slug = self.request.GET.get('genre')
        if genre_slug:
            queryset = queryset.filter(genre__slug=genre_slug)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['genres'] = Genre.objects.all()
        return context


class GameDetailView(DetailView):
    model = Game
    template_name = 'games/game_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['guides'] = self.object.guide_set.all()[:5]
        context['reviews'] = self.object.review_set.all()[:5]
        return context