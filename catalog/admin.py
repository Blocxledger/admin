from django.contrib import admin
from .models import Watchlist, Notification, HomeSection, HomeSectionItem


class HomeSectionItemInline(admin.TabularInline):
    model = HomeSectionItem
    extra = 1
    raw_id_fields = ['set_obj']
    ordering = ['order']


@admin.register(HomeSection)
class HomeSectionAdmin(admin.ModelAdmin):
    list_display = ['name', 'order', 'is_active', 'item_count']
    list_editable = ['order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']
    inlines = [HomeSectionItemInline]

    def item_count(self, obj):
        return obj.items.count()
    item_count.short_description = 'Items'


@admin.register(Watchlist)
class WatchlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'set_obj', 'is_favorite', 'created_at']
    list_filter = ['is_favorite', 'created_at']
    search_fields = ['user__username', 'set_obj__set_id']
    raw_id_fields = ['user', 'set_obj']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'set_obj', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    raw_id_fields = ['user', 'set_obj']
