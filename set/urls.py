from django.urls import path
from .views import ingest_set

urlpatterns = [
    path("ingest-set/", ingest_set),
]