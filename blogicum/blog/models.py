from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils.html import mark_safe
from django.contrib import admin

User = get_user_model()

NUMBER_OF_CHARACTERS_DISPLAYED = 25
TEXT_CONSTANT = 5


class PublishedAndCreated(models.Model):
    is_published = models.BooleanField(
        default=True,
        verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Добавлено',
    )

    class Meta:
        abstract = True


class Location(PublishedAndCreated):
    name = models.CharField('Название места', max_length=256)

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name[:NUMBER_OF_CHARACTERS_DISPLAYED]


class Category(PublishedAndCreated):
    title = models.CharField(max_length=256, verbose_name='Заголовок')
    description = models.TextField(verbose_name='Описание')
    slug = models.SlugField(
        unique=True,
        verbose_name='Идентификатор',
        help_text=(
            'Идентификатор страницы для URL;'
            ' разрешены символы латиницы, цифры, дефис и подчёркивание.'
        )
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title[:NUMBER_OF_CHARACTERS_DISPLAYED]


class Post(PublishedAndCreated):
    title = models.CharField(max_length=256, verbose_name='Заголовок')
    text = models.TextField(verbose_name='Текст')
    image = models.ImageField('Фото', upload_to='post_images', blank=False)
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        help_text=(
            'Если установить дату и время в будущем — '
            'можно делать отложенные публикации.'
        )
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации',
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Местоположение',
        blank=True

    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория',
    )

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        default_related_name = 'posts'
        ordering = ("-pub_date",)

    def __str__(self):
        return self.title[:NUMBER_OF_CHARACTERS_DISPLAYED]

    def get_absolute_url(self):
        return reverse('blog.detail', kwargs={'post_id': self.pk})

    @admin.display(description='Image')
    def image_tag(self):
        if self.image:
            return mark_safe(
                f'<img src="/{self.image}" width="150" height="150" />'
            )

    # image_tag.short_description = 'Image'


class Comment(models.Model):
    comment = models.TextField('Комментарий', max_length=550)
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('created_at',)

    def __str__(self):
        return f'{self.comment[:TEXT_CONSTANT]}, {self.author}'
