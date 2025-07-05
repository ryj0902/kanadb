from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="deck_index"),
    path("set/", views.deck_from_url, name="deck_set"),
    path("check/", views.check_deck_modification, name="deck_check"),
]
