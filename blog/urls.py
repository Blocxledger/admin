from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.article_list, name='list'),
    path('category/<slug:slug>/', views.category_detail, name='category'),
    path('<slug:slug>/', views.article_detail, name='detail'),
    path('subscribe/', views.subscribe, name='subscribe'),
    path('unsubscribe/<str:token>/', views.unsubscribe, name='unsubscribe'),
]
