import numpy as np
from django.shortcuts import render
from django.utils.translation import gettext as _

from card.models import Card

from .models import Deck

deck_total = Deck.objects.all()


# Create your views here.
def index(request):
    decks = Deck.objects.all()

    context = {"deck_list": decks}

    return render(request, "deck/index.html", context)


def deck_detail(request, deck_id):
    # deck = Deck.objects.all().filter(id=deck_id)[0]
    deck = deck_total.filter(id=deck_id)[0]
    setup = list(map(lambda x: int(x), deck.setup.split(",")))

    card_ids, counts = np.unique(setup, return_counts=True)

    cards = list()
    for card_id, count in zip(card_ids, counts):
        card = Card.objects.all().filter(id=card_id)[0]
        card.count = count
        cards.append(card)

    sorted_cards = sorted(cards[1:], key=lambda card: (card.category, card.size))

    # parse string after sorting
    for card in cards:
        Card.parse_static_url(card)
        Card.parse_to_string(card)

    context = {
        "chapter_name": deck.chapter_name,
        "chapter_name_us": deck.chapter_name_us,
        "loading_name": deck.loading_name,
        "loading_name_us": deck.loading_name_us,
        "loading_desc": deck.loading_desc,
        "loading_desc_us": deck.loading_desc_us,
        "card_character": cards[0],
        "card_list": sorted_cards,
        "horizontal_layout": _("가로 모드"),
        "vertical_layout": _("세로 모드"),
    }

    return render(request, "deck/deck_detail.html", context)
