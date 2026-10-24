from django.contrib import admin

from card.admin import ReadOnlyAdmin

from .models import Npc


@admin.register(Npc)
class NpcAdmin(ReadOnlyAdmin):
    list_display = ["id", "chapter_name", "loading_name"]
    search_fields = ["id", "chapter_name", "loading_name"]
