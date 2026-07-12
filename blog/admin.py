from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Article, Subscriber


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'article_count']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']

    def article_count(self, obj):
        return obj.articles.filter(is_published=True).count()
    article_count.short_description = 'Published Articles'


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'author', 'is_published', 'published_at', 'created_at']
    list_filter = ['is_published', 'category', 'created_at']
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ['author']
    date_hierarchy = 'created_at'
    list_editable = ['is_published']
    list_per_page = 25

    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'author', 'category')
        }),
        ('Content', {
            'fields': ('excerpt', 'content', 'featured_image'),
        }),
        ('Publishing', {
            'fields': ('is_published', 'published_at'),
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.author:
            obj.author = request.user
        super().save_model(request, obj, form, change)


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ['email', 'is_active', 'subscribed_at']
    list_filter = ['is_active', 'subscribed_at']
    search_fields = ['email']
    list_per_page = 50
