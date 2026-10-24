from django.urls import path

from . import views

app_name = "deck"

urlpatterns = [
    path("", views.index, name="index"),
    path("set/", views.deck_from_url, name="set"),
    path("check/", views.check_deck_modification, name="check"),
]
