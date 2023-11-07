from django.contrib import admin

from .models import Category, Location, Post


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'pub_date',
        'author',
        'category'
    )
    search_fields = ['title']
    list_filter = ('is_published', 'created_at')


class LocationAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ['name']
    list_filter = ('is_published', 'created_at')


class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'slug'
    )
    search_fields = ['slug', 'title']
    list_filter = ('is_published', 'created_at')


admin.site.register(Category, CategoryAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Post, PostAdmin)
