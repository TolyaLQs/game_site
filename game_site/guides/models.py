from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User


class Guide(models.Model):
    DIFFICULTY_CHOICES = [
        ('beginner', 'Для новичков'),
        ('intermediate', 'Средний уровень'),
        ('advanced', 'Для экспертов'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    game = models.ForeignKey('games.Game', on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    featured_image = models.ImageField(upload_to='guide_images/')
    views = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.title} для {self.game.title}"