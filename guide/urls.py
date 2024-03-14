from django.urls import path
from . import views

urlpatterns = [
    path("", views.index),
    path("<str:guide_name>", views.guide_detail, name="guide_detail"),
]
