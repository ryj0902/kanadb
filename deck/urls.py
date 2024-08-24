from django.urls import path

from . import views

urlpatterns = [
    path("", views.index),
    path("<int:deck_id>", views.deck_detail, name="deck_detail"),
]
