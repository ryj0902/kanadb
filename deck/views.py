import json

import numpy as np
from django.core.paginator import Paginator
from django.forms.models import model_to_dict
from django.http import HttpResponse, JsonResponse
from django.http.request import MultiValueDict, QueryDict
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils.encoding import force_str
from django.utils.functional import Promise
from django.utils.translation import get_language
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from card.forms import CardSearchForm
from card.models import Card
from npc.views import calculate_statistics


class LazyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Promise):
            return force_str(obj)
        return super().default(obj)


def index(request):
    if request.method == "POST" and "page" in request.POST:
        # stack overflow solution: https://stackoverflow.com/a/31166557/14739100
        session_data = request.session.get("post_data", {})
        session_data = MultiValueDict(session_data)
        post_data = QueryDict("", mutable=True)
        post_data.update(session_data)
    else:
        post_data = request.POST
    form = CardSearchForm(post_data or None)

    try:
        if form.is_valid():
            cards = form.filter_cards()
        else:
            cards = Card.objects.all().filter(collect=True)
    except Card.DoesNotExist:
        cards = None

    tab = request.POST.get("tab", "detail")
    deck_tab = request.POST.get("deck_tab", "view")

    cards = cards.filter(enhance=0)

    paginator = Paginator(cards, 12)
    page_total = paginator.num_pages
    page_number = request.POST.get("page", 1)
    cards = paginator.get_page(page_number)

    # update url value to static url
    for card in cards:
        Card.parse_static_url(card)
        Card.parse_to_string(card)

    context = {
        "card_list": cards,
        "page": page_number,
        "page_total": page_total,
        "selected_card": None,
        "form": form,
        "tab": tab,
        "deck_tab": deck_tab,
        "horizontal_layout": _("가로 모드"),
        "vertical_layout": _("세로 모드"),
    }

    if request.method == "POST" and "page" in request.POST:
        for card in cards:
            card = model_to_dict(card)
            Card.parse_static_url(card)

        return HttpResponse(render(request, "deck/index.html", context))

    # QueryDict is immutable, so save it as native dictionary
    request.session["post_data"] = dict(request.POST)
    # reset deck preview
    request.session["deck_card_ids"] = []
    return render(request, "deck/index.html", context)


def deck_from_url(request):
    ids = request.GET.get("card", "")
    title = request.GET.get("title", "None")
    summary = request.GET.get("summary", "None")
    description = request.GET.get("description", "None")

    try:
        card_ids = [int(cid) for cid in ids.split(",") if cid.isdigit()]
    except ValueError:
        card_ids = []

    card_ids, counts = np.unique(card_ids, return_counts=True)
    cards_ = []
    for card_id, count in zip(card_ids, counts):
        card = Card.objects.get(id=card_id)
        card.count = int(count)
        cards_.append(card)

    cards_ = sorted(cards_, key=lambda card: (card.category, card.size))

    statistics = calculate_statistics(cards_)

    deck_points, num_cards = 0, 0
    cards = []
    for card in cards_:
        count = card.count
        card = model_to_dict(card)
        Card.parse_static_url(card)
        Card.parse_to_string(card)
        card["count"] = count

        cards.append(card)

        deck_points += card["point"] * card["count"]
        num_cards += card["count"]

    if len(cards) != 0 and cards[0]["category"] == "캐릭터":
        card_character = cards[0]
        deck_card_list = cards[1:]
        num_cards -= 1
    else:
        card_character = None
        deck_card_list = cards

    context = {
        "card_character": card_character,
        "deck_card_list": deck_card_list,
        "chapter_name": title,
        "chapter_name_us": title,
        "loading_name": summary,
        "loading_name_us": summary,
        "loading_desc": description,
        "loading_desc_us": description,
    }

    context |= statistics

    rendered_html = render_to_string(
        "npc/npc_deck.html",
        context,
        request=request,
    )

    return JsonResponse(
        {
            "card_character": card_character,
            "deck_card_list": deck_card_list,
            "num_cards": num_cards,
            "deck_points": deck_points,
            "html": rendered_html,
        },
        json_dumps_params={"ensure_ascii": False},
        encoder=LazyEncoder,
    )


def get_valid_card_ids(current_ids: list, card_id):
    cards = [Card.objects.filter(id=cid)[0] for cid in current_ids]
    target_card = Card.objects.filter(id=card_id)[0]
    # character check
    if target_card.category == 1:
        for card in cards:
            if card.category == 1:
                current_ids.remove(card.id)
                current_ids = [card_id] + current_ids
                return current_ids

    # card limit check
    count = 0
    for card in cards:
        if card.enh_orig == target_card.enh_orig:
            count += 1

    if target_card.limit <= count:
        return current_ids

    current_ids.append(card_id)

    # sorting
    cards = [Card.objects.filter(id=cid)[0] for cid in current_ids]
    cards = sorted(cards, key=lambda card: (card.category, card.size))
    current_ids = [card.id for card in cards]

    return current_ids


@require_POST
def check_deck_modification(request):
    try:
        data = json.loads(request.body)
        card_id = int(data["card_id"])
        action = data["action"]  # 'add' or 'remove'
        current_ids = [int(i) for i in data["current_card_ids"]]
    except (KeyError, ValueError, json.JSONDecodeError):
        return JsonResponse({"error": "Invalid request"}, status=400)

    if action == "add":
        current_ids = get_valid_card_ids(current_ids, card_id)
    elif action == "remove":
        current_ids.remove(card_id)

    language_code = get_language()
    new_url = f"/{language_code}/deck/?card=" + ",".join(map(str, current_ids))
    return JsonResponse({"redirect_url": new_url})
