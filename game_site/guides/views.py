from django.shortcuts import render

# Create your views here.
from django.views.generic import ListView, DetailView
from .models import Guide


class GuideListView(ListView):
    model = Guide
    template_name = 'guides/guide_list.html'
    paginate_by = 10
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        game_slug = self.request.GET.get('game')
        if game_slug:
            queryset = queryset.filter(game__slug=game_slug)
        difficulty = self.request.GET.get('difficulty')
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)
        return queryset


class GuideDetailView(DetailView):
    model = Guide
    template_name = 'guides/guide_detail.html'

    def get(self, request, *args, **kwargs):
        # Увеличиваем счетчик просмотров
        self.object = self.get_object()
        self.object.views += 1
        self.object.save()
        return super().get(request, *args, **kwargs)