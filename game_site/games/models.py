from django.db import models
from django.urls import reverse
# Create your models here.


class Genre(models.Model):
    """
    Модель для представления игровых жанров.
    Используется для категоризации игр.
    """
    name = models.CharField(
        max_length=50,
        verbose_name="Название жанра",
        help_text="Введите название жанра (например, RPG, Шутер)"
    )
    slug = models.SlugField(
        max_length=60,
        unique=True,
        verbose_name="URL-идентификатор",
        help_text="Уникальная часть URL для этого жанра (только латиница, цифры, дефисы и подчеркивания)"
    )

    # Метаданные модели
    class Meta:
        verbose_name = "Жанр"  # Человекочитаемое имя в единственном числе
        verbose_name_plural = "Жанры"  # Человекочитаемое имя во множественном числе
        ordering = ['name']  # Сортировка по умолчанию

    def __str__(self):
        """Строковое представление объекта (для админки и консоли)"""
        return self.name

    def get_absolute_url(self):
        """Возвращает абсолютный URL для доступа к списку игр этого жанра"""
        return reverse('games_by_genre', args=[self.slug])


# Модель: Игра
class Game(models.Model):
    """
    Основная модель для представления видеоигр в каталоге.
    Содержит основную информацию об игре.
    """

    # Константы для выбора платформы
    PC = 'PC'
    PS5 = 'PS5'
    XBOX = 'XBOX'
    SWITCH = 'SWITCH'
    MOBILE = 'MOBILE'

    PLATFORM_CHOICES = [
        (PC, 'PC'),
        (PS5, 'PlayStation 5'),
        (XBOX, 'Xbox Series X/S'),
        (SWITCH, 'Nintendo Switch'),
        (MOBILE, 'Mobile'),
    ]

    # Поля модели
    title = models.CharField(
        max_length=200,
        verbose_name="Название игры",
        help_text="Полное официальное название игры"
    )
    slug = models.SlugField(
        max_length=210,
        unique=True,
        verbose_name="URL-идентификатор",
        help_text="Уникальная часть URL для этой игры (формируется автоматически из названия)"
    )
    developer = models.CharField(
        max_length=100,
        verbose_name="Разработчик",
        help_text="Компания-разработчик игры"
    )
    publisher = models.CharField(
        max_length=100,
        verbose_name="Издатель",
        help_text="Компания-издатель игры",
        blank=True  # Не обязательно к заполнению
    )
    release_date = models.DateField(
        verbose_name="Дата выхода",
        help_text="Дата официального релиза игры"
    )
    platforms = models.CharField(
        max_length=50,
        choices=PLATFORM_CHOICES,
        verbose_name="Платформы",
        help_text="Основная платформа игры"
    )
    # Связь многие-ко-многим с моделью Genre
    genres = models.ManyToManyField(
        Genre,
        related_name='games',
        verbose_name="Жанры",
        help_text="Выберите жанры для этой игры"
    )
    description = models.TextField(
        verbose_name="Описание",
        help_text="Подробное описание игры, сюжета и особенностей"
    )
    cover = models.ImageField(
        upload_to='game_covers/%Y/%m/%d/',
        verbose_name="Обложка",
        help_text="Загрузите изображение обложки игры (рекомендуемый размер 600x800)"
    )
    trailer_url = models.URLField(
        max_length=200,
        blank=True,
        verbose_name="Ссылка на трейлер",
        help_text="URL трейлера игры на YouTube"
    )
    # Рейтинг игры (вычисляемое поле, по умолчанию 0.0)
    rating = models.FloatField(
        default=0.0,
        verbose_name="Рейтинг",
        help_text="Средняя оценка игры на основе пользовательских рецензий"
    )
    # Дата добавления в каталог (автоматически при создании)
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата добавления"
    )
    # Дата последнего обновления (автоматически при изменении)
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления"
    )

    class Meta:
        verbose_name = "Игра"
        verbose_name_plural = "Игры"
        ordering = ['-release_date']  # Сортировка по дате выхода (новые сначала)
        indexes = [
            models.Index(fields=['title']),  # Индекс для ускорения поиска по названию
            models.Index(fields=['-release_date']),  # Индекс для сортировки по дате
        ]

    def __str__(self):
        return f"{self.title} ({self.release_date.year})"

    def get_absolute_url(self):
        """Возвращает URL для страницы детальной информации об игре"""
        return reverse('game_detail', args=[self.slug])

    def get_platform_display_name(self):
        """Возвращает читаемое название платформы"""
        return dict(self.PLATFORM_CHOICES).get(self.platforms, self.platforms)

    def update_rating(self):
        """Пересчитывает рейтинг игры на основе всех обзоров"""
        reviews = self.reviews.all()  # Связанные обзоры через related_name
        if reviews.exists():
            total = sum(review.rating for review in reviews)
            self.rating = round(total / reviews.count(), 1)
            self.save(update_fields=['rating'])
