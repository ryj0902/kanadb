from django.urls import path

from . import views

app_name = "card"

urlpatterns = [
    path("", views.index, name="index"),
    path("select/<int:card_id>", views.select, name="select"),
]
