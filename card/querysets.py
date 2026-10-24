from django.db import models
from django.db.models import Q

# 텍스트 검색 종류별 대상 필드 (영어는 각 필드의 _us 버전)
SEARCH_FIELDS = {
    "name": ["name"],
    "tag": ["tag"],
    "skill": ["skill_turn", "skill_instance", "skill_attack", "skill_defend"],
}

EPISODE_FIELDS = [
    "episode_season1",
    "episode_season2",
    "episode_season3",
    "episode_event",
    "episode_extra",
]


class CardQuerySet(models.QuerySet):
    def collectible(self):
        return self.filter(collect=True)

    def base_forms(self):
        """강화되지 않은 원본 카드"""
        return self.filter(enhance=0)

    def search_text(self, search_type, text, lang):
        """이름은 전체 문자열, 태그/효과는 쉼표로 나눈 모든 단어를 포함하는 카드"""
        fields = SEARCH_FIELDS.get(search_type)
        if not fields:
            return self
        if lang != "ko":
            fields = [f"{field}_us" for field in fields]

        terms = (
            [text] if search_type == "name" else [t.strip() for t in text.split(",")]
        )
        queryset = self
        for term in terms:
            condition = Q()
            for field in fields:
                condition |= Q(**{f"{field}__icontains": term})
            queryset = queryset.filter(condition)
        return queryset

    def search(self, data, lang):
        """CardSearchForm.cleaned_data 조건으로 검색"""
        queryset = self.search_text(
            data.get("search_type"), data.get("search_text") or "", lang
        )

        for field in ["category", "rarity", "theme"]:
            if data.get(field):
                queryset = queryset.filter(**{f"{field}__in": data[field]})

        if data.get("size_min") is not None:
            queryset = queryset.filter(size__gte=data["size_min"])
        if data.get("size_max") is not None:
            queryset = queryset.filter(size__lte=data["size_max"])

        episodes = [
            episode for field in EPISODE_FIELDS for episode in data.get(field) or []
        ]
        if episodes:
            queryset = queryset.filter(episode__in=episodes)

        etc = data.get("etc") or []
        if "uncollectable" not in etc:
            queryset = queryset.collectible()
        if "producible" in etc:
            queryset = queryset.filter(producible=True)

        return queryset
