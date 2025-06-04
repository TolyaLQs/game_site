from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.core import validators
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
# Create your models here.


class UnicodeEmailValidator(validators.RegexValidator):
    regex = r'^[-\w\.]+@([-\w]+\.)+[-\w]{2,4}$'
    message = 'Enter a valid email. This value may contain only letters,' \
              ' numbers, and @/./+/-/_ characters.'
    flags = 0


class CustomUserManager(BaseUserManager):
    """
    Кастомный менеджер для модели пользователя, где email является
    уникальным идентификатором для аутентификации вместо username.
    """

    def create_user(self, email, username, password=None, **extra_fields):
        """
        Создает и сохраняет пользователя с указанным email, username и паролем.
        """
        if not email:
            raise ValueError('Пользователь должен иметь email адрес')
        if not username:
            raise ValueError('Пользователь должен иметь username')

        # Нормализация email (приведение к нижнему регистру)
        email = self.normalize_email(email)

        # Создание объекта пользователя
        user = self.model(
            email=email,
            username=username,
            **extra_fields
        )

        # Установка пароля (автоматическое хеширование)
        user.set_password(password)

        # Сохранение в базе данных (для multi-database используем using=self._db)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password, **extra_fields):
        """
        Создает и сохраняет суперпользователя с указанным email, username и паролем.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Суперпользователь должен иметь is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Суперпользователь должен иметь is_superuser=True.')

        return self.create_user(email, username, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Кастомная модель пользователя, поддерживающая авторизацию по email и username.
    Заменяет стандартную модель django.contrib.auth.models.User.
    """
    # Основные поля
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
    username = models.CharField(
        verbose_name='имя пользователя',
        max_length=30,
        unique=True
    )

    # Дополнительные поля
    date_joined = models.DateTimeField(
        verbose_name='дата регистрации',
        default=timezone.now
    )
    avatar = models.ImageField(
        verbose_name='аватар',
        upload_to='avatars/',
        blank=True,
        null=True
    )
    bio = models.TextField(
        verbose_name='о себе',
        max_length=500,
        blank=True
    )
    # Флаги статуса пользователя
    is_active = models.BooleanField(
        verbose_name='активный',
        default=True,
        help_text='Указывает, активен ли пользователь. Вместо удаления аккаунта'
    )
    is_staff = models.BooleanField(
        verbose_name='сотрудник',
        default=False,
        help_text='Указывает, может ли пользователь войти в админ-панель'
    )

    # Связь с менеджером объектов
    objects = CustomUserManager()

    # Поле для аутентификации (вместо username по умолчанию)
    USERNAME_FIELD = 'email'

    # Обязательные поля при создании пользователя (USERNAME_FIELD и пароль уже включены)
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'
        ordering = ['-date_joined']

    def __str__(self):
        return self.username

    def get_full_name(self):
        """Возвращает имя пользователя (в кастомной модели без имени/фамилии)"""
        return self.username

    def get_short_name(self):
        """Возвращает короткое имя (username)"""
        return self.username

    @property
    def avatar_url(self):
        """Возвращает URL аватара или стандартное изображение"""
        if self.avatar and hasattr(self.avatar, 'url'):
            return self.avatar.url
        return '/static/images/default_avatar.png'


class Profile(models.Model):
    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)
    sex = models.CharField(max_length=6, blank=True, null=True)
    link = models.URLField(blank=True, null=True)
    about_me = models.TextField(blank=True, null=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.user.get_full_name()

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



