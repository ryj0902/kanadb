from django.urls import path

from . import views

urlpatterns = [
    path("", views.index),
    path("<int:npc_id>", views.npc_detail, name="npc_detail"),
]
