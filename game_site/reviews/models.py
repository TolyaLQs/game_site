from django.db import models

# Create your models here.
from django.db import models
from userapp.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Review(models.Model):
    game = models.ForeignKey('games.Game', on_delete=models.CASCADE)
    author = models.ForeignKey(User, related_name='review_user', on_delete=models.CASCADE)
    content = models.TextField()
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    pros = models.TextField()
    cons = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Обзор {self.game.title} от {self.author.username}"

