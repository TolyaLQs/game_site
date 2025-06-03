from django.shortcuts import render

# Create your views here.
from django.views.generic import ListView, DetailView
from .models import News


class NewsListView(ListView):
    model = News
    template_name = 'news/news_list.html'
    paginate_by = 10
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        game_slug = self.request.GET.get('game')
        if game_slug:
            queryset = queryset.filter(game__slug=game_slug)
        return queryset


class NewsDetailView(DetailView):
    model = News
    template_name = 'news/news_detail.html'

    def get(self, request, *args, **kwargs):
        # Увеличиваем счетчик просмотров
        self.object = self.get_object()
        self.object.views += 1
        self.object.save()
        return super().get(request, *args, **kwargs)

