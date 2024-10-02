from django import forms
from django.db.models import Q
from django.utils.translation import get_language
from django.utils.translation import gettext_lazy as _

from .models import Card


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
        choices=Card.CATEGORY_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={"class": "checkbox-inline"}),
        required=False,
        label="category",
    )
    rarity = forms.MultipleChoiceField(
        choices=Card.RARITY_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={"class": "checkbox-inline"}),
        required=False,
        label="rarity",
    )
    theme = forms.MultipleChoiceField(
        choices=Card.THEME_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={"class": "checkbox-inline"}),
        required=False,
        label="theme",
    )
    size_min = forms.IntegerField(
        min_value=1, max_value=10, required=False, label="size_min"
    )
    size_max = forms.IntegerField(
        min_value=1, max_value=10, required=False, label="size_max"
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
    episode_event = forms.MultipleChoiceField(
        choices=Card.EPISODE_EVENT,
        widget=forms.CheckboxSelectMultiple(attrs={"class": "checkbox-inline"}),
        required=False,
        label="event",
    )

    etc = forms.MultipleChoiceField(
        choices=ETC_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={"class": "checkbox-inline"}),
        required=False,
        label="etc",
    )

    def filter_cards(self):
        cards = Card.objects.all()

        category = self.cleaned_data.get("category")
        rarity = self.cleaned_data.get("rarity")
        theme = self.cleaned_data.get("theme")
        size_min = self.cleaned_data.get("size_min")
        size_max = self.cleaned_data.get("size_max")
        search_type = self.cleaned_data.get("search_type")
        search_text = self.cleaned_data.get("search_text")

        episode_season1 = self.cleaned_data.get("episode_season1")
        episode_season2 = self.cleaned_data.get("episode_season2")
        episode_event = self.cleaned_data.get("episode_event")

        etc = self.cleaned_data.get("etc", [])

        language = get_language()
        if language == "ko":
            if search_type == "name":
                cards = cards.filter(name__icontains=search_text)
            elif search_type == "tag":
                multi_tags = search_text.split(",")
                for tag in multi_tags:
                    tag = tag.strip()
                    cards = cards.filter(tag__icontains=tag)
            elif search_type == "skill":
                cards = cards.filter(
                    Q(skill_turn__icontains=search_text)
                    | Q(skill_instance__icontains=search_text)
                    | Q(skill_attack__icontains=search_text)
                    | Q(skill_defend__icontains=search_text)
                )
        elif language == "en":
            if search_type == "name":
                cards = cards.filter(name_us__icontains=search_text)
            elif search_type == "tag":
                multi_tags = search_text.split(",")
                for tag in multi_tags:
                    tag = tag.strip()
                    cards = cards.filter(tag_us__icontains=tag)
            elif search_type == "skill":
                cards = cards.filter(
                    Q(skill_turn_us__icontains=search_text)
                    | Q(skill_instance_us__icontains=search_text)
                    | Q(skill_attack_us__icontains=search_text)
                    | Q(skill_defend_us__icontains=search_text)
                )

        if category:
            cards = cards.filter(category__in=category)
        if rarity:
            cards = cards.filter(rarity__in=rarity)
        if theme:
            cards = cards.filter(theme__in=theme)
        if size_min and size_max:
            cards = cards.filter(size__range=(size_min, size_max))

        episode_list = episode_season1 + episode_season2 + episode_event
        if episode_season1 or episode_season2 or episode_event:
            cards = cards.filter(episode__in=episode_list)

        if "uncollectable" not in etc:
            cards = cards.filter(collect=True)
        if "producible" in etc:
            cards = cards.filter(producible=True)

        return cards
