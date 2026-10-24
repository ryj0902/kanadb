from django.urls import path

from . import views

app_name = "guide"

urlpatterns = [
    path("", views.index, name="index"),
    path("vote", views.vote, name="vote"),
    path("<str:guide_name>", views.guide_detail, name="detail"),
]
