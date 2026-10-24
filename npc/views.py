from django.shortcuts import get_object_or_404, render

from deck.services import calculate_statistics, load_cards, parse_card_ids, sort_cards

from .catalog import CATALOG
from .models import Npc
from .services import navigation


def index(request):
    return render(request, "npc/index.html", {"catalog": CATALOG})


def npc_detail(request, npc_id):
    npc = get_object_or_404(Npc, id=npc_id)

    # 덱의 첫 카드(가장 작은 id)가 캐릭터
    cards = load_cards(parse_card_ids(npc.setup))

    context = {
        "chapter_name": npc.chapter_name,
        "chapter_name_us": npc.chapter_name_us,
        "loading_name": npc.loading_name,
        "loading_name_us": npc.loading_name_us,
        "loading_desc": npc.loading_desc,
        "loading_desc_us": npc.loading_desc_us,
        "card_character": cards[0] if cards else None,
        "deck_card_list": sort_cards(cards[1:]),
        "navigation": navigation(npc_id),
        **calculate_statistics(cards),
    }
    return render(request, "npc/npc_detail.html", context)
