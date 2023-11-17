from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('select/<int:card_id>', views.select)
]
