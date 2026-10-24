from django.urls import path

from . import views

app_name = "npc"

urlpatterns = [
    path("", views.index, name="index"),
    path("<int:npc_id>", views.npc_detail, name="detail"),
]
