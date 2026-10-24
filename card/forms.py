from django import forms
from django.utils.translation import gettext_lazy as _

from core.text import Text

from .models import SIZE_RANGE, Card


class CardSearchForm(forms.Form):
    SEARCH_CHOICES = [
        ("name", _("이름")),
        ("tag", _("태그")),
        ("skill", _("효과")),
    ]
    ETC_CHOICES = [
        ("uncollectable", _("수집 불가 포함")),
        ("producible", _("제작 가능만")),
    ]

    category = forms.MultipleChoiceField(
        choices=Card.Category,
        widget=forms.CheckboxSelectMultiple(
            attrs={"class": "search-filter__checkboxes"}
        ),
        required=False,
        label="category",
    )
    rarity = forms.MultipleChoiceField(
        choices=Card.Rarity,
        widget=forms.CheckboxSelectMultiple(
            attrs={"class": "search-filter__checkboxes"}
        ),
        required=False,
        label="rarity",
    )
    theme = forms.MultipleChoiceField(
        choices=Card.Theme,
        widget=forms.CheckboxSelectMultiple(
            attrs={"class": "search-filter__checkboxes"}
        ),
        required=False,
        label="theme",
    )
    size_min = forms.IntegerField(
        min_value=SIZE_RANGE.start,
        max_value=SIZE_RANGE.stop - 1,
        required=False,
        label="size_min",
    )
    size_max = forms.IntegerField(
        min_value=SIZE_RANGE.start,
        max_value=SIZE_RANGE.stop - 1,
        required=False,
        label="size_max",
    )
    search_type = forms.ChoiceField(
        choices=SEARCH_CHOICES, widget=forms.Select, label="search_type"
    )
    search_text = forms.CharField(label="search_text", required=False)

    episode_season1 = forms.MultipleChoiceField(
        choices=Card.EPISODE_SEASON1,
        widget=forms.CheckboxSelectMultiple(
            attrs={"class": "search-filter__checkboxes"}
        ),
        required=False,
        label="season1",
    )
    episode_season2 = forms.MultipleChoiceField(
        choices=Card.EPISODE_SEASON2,
        widget=forms.CheckboxSelectMultiple(
            attrs={"class": "search-filter__checkboxes"}
        ),
        required=False,
        label="season2",
    )
    episode_season3 = forms.MultipleChoiceField(
        choices=Card.EPISODE_SEASON3,
        widget=forms.CheckboxSelectMultiple(
            attrs={"class": "search-filter__checkboxes"}
        ),
        required=False,
        label="season3",
    )
    episode_event = forms.MultipleChoiceField(
        choices=Card.EPISODE_EVENT,
        widget=forms.CheckboxSelectMultiple(
            attrs={"class": "search-filter__checkboxes"}
        ),
        required=False,
        label="event",
    )
    episode_extra = forms.MultipleChoiceField(
        choices=Card.EPISODE_EXTRA,
        widget=forms.CheckboxSelectMultiple(
            attrs={"class": "search-filter__checkboxes"}
        ),
        required=False,
        label="extra",
    )

    etc = forms.MultipleChoiceField(
        choices=ETC_CHOICES,
        widget=forms.CheckboxSelectMultiple(
            attrs={"class": "search-filter__checkboxes"}
        ),
        required=False,
        label="etc",
    )

    # 검색 필터 화면 배치: (필드 이름, 행 제목)
    EPISODE_ROWS = [
        ("episode_season1", Text(_("시즌"), "1")),
        ("episode_season2", Text(_("시즌"), "2")),
        ("episode_season3", Text(_("시즌"), "3")),
        ("episode_event", _("이벤트")),
        ("episode_extra", _("엑스트라")),
    ]
    DETAIL_ROWS = [
        ("category", _("종류")),
        ("rarity", _("등급")),
        ("theme", _("소속")),
    ]

    def _rows(self, rows):
        """[{"label", "field", "toggle_id"}] - toggle_id: 전체 선택 체크박스 id"""
        return [
            {
                "label": label,
                "field": self[name],
                "toggle_id": "toggle-all-" + name.replace("_", "-"),
            }
            for name, label in rows
        ]

    def episode_rows(self):
        return self._rows(self.EPISODE_ROWS)

    def detail_rows(self):
        return self._rows(self.DETAIL_ROWS)
