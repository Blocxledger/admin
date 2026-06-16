from django.urls import path
from .views import ingest_set, brickeconomy_links

urlpatterns = [
    path("ingest-set/", ingest_set),
    path("brickeconomy-links/", brickeconomy_links, name="brickeconomy_links"),
]