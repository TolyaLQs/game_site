from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.core import validators
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from ..guides.models import Guide

# Create your models here.


class UnicodeEmailValidator(validators.RegexValidator):
    regex = r'^[-\w\.]+@([-\w]+\.)+[-\w]{2,4}$'
    message = 'Enter a valid email. This value may contain only letters,' \
              ' numbers, and @/./+/-/_ characters.'
    flags = 0


class CustomUserManager(BaseUserManager):

    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('Пользователь должен иметь email адрес')
        if not username:
            raise ValueError('Пользователь должен иметь username')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Суперпользователь должен иметь is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Суперпользователь должен иметь is_superuser=True.')

        return self.create_user(email, username, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email_validator = UnicodeEmailValidator()
    email = models.EmailField(verbose_name='Email',
                              max_length=150, unique=True,
                              help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.',
                              validators=[email_validator],
                              error_messages={'unique': 'Пользователь с этой почтой зарегистрирован.',
                                              'unique_email': 'Пользователь с этой почтой зарегистрирован.',
                                              'invalid': 'Некорректная почта.',
                                              'required': 'Это поле обязательно для заполнения.',
                                              'blank': 'Это поле обязательно для заполнения.',
                                              'IntegrityError': 'Пользователь с этой почтой зарегистрирован.'})
    username = models.CharField(verbose_name='имя пользователя', max_length=30, unique=True)
    first_name = None
    last_name = None
    date_joined = models.DateTimeField(verbose_name='дата регистрации', default=timezone.now)
    avatar = models.ImageField(verbose_name='аватар', upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(verbose_name='о себе', max_length=500, blank=True)
    is_active = models.BooleanField(verbose_name='активный', default=True,
                                    help_text='Указывает, активен ли пользователь. Вместо удаления аккаунта')
    is_staff = models.BooleanField(verbose_name='сотрудник', default=False,
                                   help_text='Указывает, может ли пользователь войти в админ-панель')
    objects = CustomUserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'
        ordering = ['-date_joined']

    def __str__(self):
        return self.username

    def get_short_name(self):
        return self.username

    @property
    def avatar_url(self):
        if self.avatar and hasattr(self.avatar, 'url'):
            return self.avatar.url
        return '/static/images/default_avatar.png'


class Profile(models.Model):
    SEX_CHOICES = [
        ('men', 'Мужской'),
        ('women', 'Женский'),
    ]
    birthday = models.DateField(blank=True, null=True, verbose_name="Дата рождения")
    first_name = models.CharField(max_length=30, blank=True, null=True, verbose_name='Имя')
    last_name = models.CharField(max_length=30, blank=True, null=True, verbose_name='Фамилия')
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    gaming_platforms = models.CharField(max_length=100, blank=True, verbose_name="Любимые платформы")
    favorite_genres = models.ManyToManyField('games.Genre', blank=True, verbose_name="Любимые жанры")
    achievements = models.JSONField(default=dict, blank=True, verbose_name="Достижения на сайте")
    last_activity = models.DateTimeField(auto_now=True, verbose_name="Последняя активность")
    age = models.IntegerField(blank=True, null=True, verbose_name="Возраст")
    sex = models.CharField(max_length=6, choices=SEX_CHOICES, blank=True, verbose_name="Пол")
    link = models.URLField(blank=True, null=True)
    status = models.BooleanField(default=True)

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'

    def __str__(self):
        return self.get_full_name()

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()

    def get_absolute_url(self):
        return f"/user/{self.user.username}/"

    def get_avatar(self):
        if self.avatar:
            return self.avatar.url
        else:
            return '/media/avatars/default.png'

    def img_tag(self):
        return mark_safe('<img src="%s" width="50" height="50" />' % self.get_img())

    def save(self, *args, **kwargs):
        if not self.avatar:
            self.avatar = '/media/avatars/default.png'
        super().save(*args, **kwargs)


class FriendUser(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='friend_user')
    friend = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='user_friend')
    date_add = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.friend.get_full_name()

    class Meta:
        verbose_name = 'Друг'
        verbose_name_plural = 'Друзья'
        ordering = ['-friend']


class Comment(models.Model):
    user = models.ForeignKey(User, related_name='comment_user', on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    link = models.URLField(blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class UserRating(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)

    def update_score(self):
        comments = Comment.objects.filter(user=self.user).count()
        guides = Guide.objects.filter(author=self.user).count()
        likes = LikeDislike.objects.filter(user=self.user, vote=1).count()
        self.score = comments * 1 + guides * 5 + likes * 2
        self.save()

