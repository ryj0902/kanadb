from django import forms
from django.utils.translation import gettext_lazy as _

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
        choices=Card.Category.choices,
        widget=forms.CheckboxSelectMultiple(attrs={"class": "checkbox-inline"}),
        required=False,
        label="category",
    )
    rarity = forms.MultipleChoiceField(
        choices=Card.Rarity.choices,
        widget=forms.CheckboxSelectMultiple(attrs={"class": "checkbox-inline"}),
        required=False,
        label="rarity",
    )
    theme = forms.MultipleChoiceField(
        choices=Card.Theme.choices,
        widget=forms.CheckboxSelectMultiple(attrs={"class": "checkbox-inline"}),
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
        widget=forms.CheckboxSelectMultiple(attrs={"class": "checkbox-inline"}),
        required=False,
        label="season1",
    )
    episode_season2 = forms.MultipleChoiceField(
        choices=Card.EPISODE_SEASON2,
        widget=forms.CheckboxSelectMultiple(attrs={"class": "checkbox-inline"}),
        required=False,
        label="season2",
    )
    episode_season3 = forms.MultipleChoiceField(
        choices=Card.EPISODE_SEASON3,
        widget=forms.CheckboxSelectMultiple(attrs={"class": "checkbox-inline"}),
        required=False,
        label="season3",
    )
    episode_event = forms.MultipleChoiceField(
        choices=Card.EPISODE_EVENT,
        widget=forms.CheckboxSelectMultiple(attrs={"class": "checkbox-inline"}),
        required=False,
        label="event",
    )
    episode_extra = forms.MultipleChoiceField(
        choices=Card.EPISODE_EXTRA,
        widget=forms.CheckboxSelectMultiple(attrs={"class": "checkbox-inline"}),
        required=False,
        label="extra",
    )

    etc = forms.MultipleChoiceField(
        choices=ETC_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={"class": "checkbox-inline"}),
        required=False,
        label="etc",
    )
