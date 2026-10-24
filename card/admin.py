from django.contrib import admin

from .models import Card, Vote


class ReadOnlyAdmin(admin.ModelAdmin):
    """게임 데이터는 card.sql로만 갱신하므로 관리 화면에서는 조회만 한다"""

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Card)
class CardAdmin(ReadOnlyAdmin):
    list_display = ["id", "name", "category", "rarity", "theme", "episode", "enhance"]
    list_filter = ["category", "rarity", "theme", "collect"]
    search_fields = ["id", "name", "name_us"]


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ["card", "category", "mode", "tier", "ip", "timestamp"]
    list_filter = ["category", "mode", "tier"]
