from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.utils.translation import get_language
from django.utils.translation import gettext_lazy as _

from .forms import CardSearchForm
from .models import PAGE_SIZE, Card
from .presenters import card_detail_context, card_detail_state

SEARCH_TABS = ("detail", "episode", "etc")
# 검색 필터 탭 버튼 (표시 순서)
SEARCH_TAB_LABELS = [
    ("episode", _("에피소드")),
    ("detail", _("상세")),
    ("etc", _("기타")),
]


def search_cards(request):
    """GET 쿼리스트링으로 카드 검색 (카드/덱 페이지 공용 컨텍스트)"""
    # 덱 페이지의 card/title 등 검색과 무관한 파라미터만 있으면 검색 전 상태(오류 없는 빈 폼)
    searched = any(name in request.GET for name in CardSearchForm.base_fields)
    form = CardSearchForm(request.GET if searched else None)
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
        "search_tabs": SEARCH_TAB_LABELS,
    }


def index(request):
    context = search_cards(request)
    # 페이지 이동(AJAX)은 카드 목록 부분만 돌려준다
    if request.headers.get("X-Partial") == "card-grid":
        return render(request, "card/_card_grid.html", context)
    return render(request, "card/index.html", context)


def select(request, card_id):
    """카드 상세 패널 HTML + JS 상태"""
    card = get_object_or_404(Card, id=card_id)
    html = render_to_string(
        "components/card_detail_body.html", card_detail_context(card), request=request
    )
    return JsonResponse({"html": html, "state": card_detail_state(card)})
