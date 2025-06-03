from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User


class News(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    game = models.ForeignKey('games.Game', null=True, blank=True, on_delete=models.SET_NULL)
    is_featured = models.BooleanField(default=False)
    image = models.ImageField(upload_to='news_images/')
    views = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title

