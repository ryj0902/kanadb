import json

from django.core.paginator import Paginator
from django.forms.models import model_to_dict
from django.http import HttpResponse
from django.http.request import MultiValueDict, QueryDict
from django.shortcuts import render
from django.utils.encoding import force_str
from django.utils.functional import Promise
from django.utils.translation import gettext as _

from .forms import CardSearchForm
from .models import Card


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
        "horizontal_layout": _("가로 모드"),
        "vertical_layout": _("세로 모드"),
    }

    if request.method == "POST" and "page" in request.POST:
        for card in cards:
            card = model_to_dict(card)
            Card.parse_static_url(card)

        return HttpResponse(render(request, "card/index.html", context))

    # QueryDict is immutable, so save it as native dictionary
    request.session["post_data"] = dict(request.POST)
    return render(request, "card/index.html", context)


def select(request, card_id):
    card = Card.objects.get(id=card_id)
    card = model_to_dict(card)
    Card.parse_static_url(card)
    Card.parse_to_string(card)
    # make space between tag
    card["tag"] = card["tag"].replace(",", ", ")
    card["tag_us"] = card["tag_us"].replace(",", ", ")

    # change text to adjust indent + newline
    for key in [
        "skill_turn",
        "skill_instance",
        "skill_attack",
        "skill_defend",
        "desc",
        "skill_turn_us",
        "skill_instance_us",
        "skill_attack_us",
        "skill_defend_us",
        "desc_us",
    ]:
        card[key] = card[key].replace("◈\n ", "◈<br/>&nbsp;")
        card[key] = card[key].replace("\n◈", "<br/>◈")
        card[key] = card[key].replace("\n ", "<br/>&nbsp;")

    return HttpResponse(
        json.dumps({"selected_card": card}, ensure_ascii=False, cls=LazyEncoder)
    )
