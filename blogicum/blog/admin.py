from django.contrib import admin

from .models import Category, Location, Post, Comment


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'pub_date',
        'author',
        'category',
        'image_tag',
    )
    fieldsets = (
        (None, {
            'fields': (
                'title',
                'pub_date',
                'author',
                'category',
            )
        }),
        ('Image', {
            'classes': ('collapse',),
            'fields': ('image',),
        }),
    )
    search_fields = ('title',)
    list_filter = ('is_published', 'created_at')


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    list_filter = ('is_published', 'created_at')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'slug'
    )
    search_fields = ['slug', 'title']
    list_filter = ('is_published', 'created_at')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'comment',
        'post',
        'author',
    )
    search_fields = ['author', 'comment']
    list_filter = ('created_at',)
