from django.contrib import admin
from .models import Watchlist, Notification


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
