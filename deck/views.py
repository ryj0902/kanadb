import json

from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.decorators.http import require_POST

from card.models import DECK_SIZE, Card
from card.views import search_cards

from .services import (
    add_card,
    calculate_statistics,
    load_cards,
    parse_card_ids,
    remove_card,
    sort_cards,
)

DECK_TABS = ("view", "edit")
# 덱 상태를 담는 쿼리 파라미터 (검색 폼 제출 시에도 유지)
DECK_PARAMS = ("card", "title", "summary", "description")


def index(request):
    context = search_cards(request)

    deck_tab = request.GET.get("deck_tab", "view")
    if deck_tab not in DECK_TABS:
        deck_tab = "view"

    context |= {
        "deck_tab": deck_tab,
        "deck_params": [
            (key, request.GET[key]) for key in DECK_PARAMS if key in request.GET
        ],
    }
    return render(request, "deck/index.html", context)


def deck_from_url(request):
    """?card=1,2,2,3&title=... -> 덱 요약 HTML + 편집 화면의 덱 미리보기 HTML"""
    title = request.GET.get("title", "None")
    summary = request.GET.get("summary", "None")
    description = request.GET.get("description", "None")

    cards = sort_cards(load_cards(parse_card_ids(request.GET.get("card", ""))))
    statistics = calculate_statistics(cards)

    deck_points = sum(card.point * card.count for card in cards)
    num_cards = sum(card.count for card in cards)

    if cards and cards[0].is_character:
        card_character, deck_cards = cards[0], cards[1:]
        num_cards -= 1
    else:
        card_character, deck_cards = None, cards

    context = {
        "card_character": card_character,
        "deck_card_list": deck_cards,
        "chapter_name": title,
        "chapter_name_us": title,
        "loading_name": summary,
        "loading_name_us": summary,
        "loading_desc": description,
        "loading_desc_us": description,
        **statistics,
    }
    preview_context = {
        "card_character": card_character,
        "deck_card_list": deck_cards,
        "num_cards": num_cards,
        "deck_points": deck_points,
        "deck_size": DECK_SIZE,
    }

    return JsonResponse(
        {
            "summary_html": render_to_string(
                "deck/_deck_summary.html", context, request=request
            ),
            "preview_html": render_to_string(
                "deck/_deck_preview.html", preview_context, request=request
            ),
            "num_cards": num_cards,
            "deck_points": deck_points,
        }
    )


@require_POST
def check_deck_modification(request):
    """드래그로 카드 추가/제거 -> 새 덱 URL"""
    try:
        data = json.loads(request.body)
        card_id = int(data["card_id"])
        action = data["action"]  # 'add' or 'remove'
        current_ids = [int(i) for i in data["current_card_ids"]]
    except (KeyError, TypeError, ValueError):
        return JsonResponse({"error": "Invalid request"}, status=400)

    # 존재하지 않는 카드 id는 무시
    existing_ids = set(
        Card.objects.filter(id__in=current_ids).values_list("id", flat=True)
    )
    current_ids = [cid for cid in current_ids if cid in existing_ids]

    if action == "add":
        if not Card.objects.filter(id=card_id).exists():
            return JsonResponse({"error": "Invalid request"}, status=400)
        current_ids = add_card(current_ids, card_id)
    elif action == "remove":
        current_ids = remove_card(current_ids, card_id)

    new_url = reverse("deck:index") + "?card=" + ",".join(map(str, current_ids))
    return JsonResponse({"redirect_url": new_url})
