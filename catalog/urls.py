from django.urls import path

from . import views

app_name = 'catalog'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('search/', views.search_view, name='search'),
    path('browse/', views.browse_view, name='browse'),
    path('item/<str:code>/', views.item_detail_view, name='item_detail'),
    path('autocomplete/', views.autocomplete_view, name='autocomplete'),
    path('watchlist/', views.watchlist_view, name='watchlist'),
    path('watchlist/add/<str:code>/', views.watchlist_add, name='watchlist_add'),
    path('watchlist/remove/<str:code>/', views.watchlist_remove, name='watchlist_remove'),
    path('watchlist/toggle-favorite/<str:code>/', views.watchlist_toggle_favorite, name='watchlist_toggle_favorite'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('notifications/<int:pk>/read/', views.notification_mark_read, name='notification_mark_read'),
    path('notifications/mark-all-read/', views.notification_mark_all_read, name='notification_mark_all_read'),
]
