from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils.translation import get_language

from .forms import CardSearchForm
from .models import PAGE_SIZE, Card
from .presenters import card_detail_data

SEARCH_TABS = ("detail", "episode", "etc")


def search_cards(request):
    """GET 쿼리스트링으로 카드 검색 (카드/덱 페이지 공용 컨텍스트)"""
    form = CardSearchForm(request.GET or None)
    if form.is_valid():
        cards = Card.objects.search(form.cleaned_data, get_language())
    else:
        cards = Card.objects.collectible()

    paginator = Paginator(cards.base_forms(), PAGE_SIZE)
    page = paginator.get_page(request.GET.get("page", 1))

    tab = request.GET.get("tab", "detail")
    if tab not in SEARCH_TABS:
        tab = "detail"

    return {
        "card_list": page,
        "page": page.number,
        "page_total": paginator.num_pages,
        "form": form,
        "tab": tab,
    }


def index(request):
    return render(request, "card/index.html", search_cards(request))


def select(request, card_id):
    card = get_object_or_404(Card, id=card_id)
    return JsonResponse(
        {"selected_card": card_detail_data(card)},
        json_dumps_params={"ensure_ascii": False},
    )
