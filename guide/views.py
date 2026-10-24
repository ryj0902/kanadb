import json

from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
from markdown import markdown

from card.models import Card, Vote
from core.http import get_client_ip

from .registry import VOTE_GUIDES, guide_files, guide_title, read_guide, vote_category
from .services import tier_columns


def index(request):
    contents = [[path.name, guide_title(path)] for path in guide_files()]
    return render(request, "guide/index.html", {"contents": contents})


def guide_body_context(request, guide_name):
    """가이드 본문(마크다운 -> HTML) + 티어 리스트"""
    category = vote_category(guide_name)
    return {
        "html_content": markdown(read_guide(guide_name), extensions=["extra"]),
        "category": category,
        "tier_columns": tier_columns(category, get_client_ip(request))
        if category
        else None,
    }


def guide_detail(request, guide_name):
    return render(
        request, "guide/guide_detail.html", guide_body_context(request, guide_name)
    )


@require_POST
def vote(request):
    """티어 투표: 같은 티어를 다시 누르면 취소, 다른 티어면 변경"""
    try:
        data = json.loads(request.body)
        card_id = int(data["cardId"])
        category = str(data["category"])
        mode = int(data.get("mode", 0))  # 별도 전달값이 없으면 기본값 0(PVP) 사용
        tier = int(data["tier"])
    except (KeyError, TypeError, ValueError):
        return JsonResponse({"error": "Invalid request"}, status=400)

    if (
        category not in VOTE_GUIDES
        or mode not in Vote.MODE_MAP
        or tier not in Vote.TIER_MAP
    ):
        return JsonResponse({"error": "Invalid request"}, status=400)

    card = Card.objects.filter(id=card_id).first()
    if card is None:
        return JsonResponse({"error": "Invalid request"}, status=400)

    ip_address = get_client_ip(request)
    existing_vote = Vote.objects.filter(
        card=card, category=category, mode=mode, ip=ip_address
    ).first()

    if existing_vote is None:
        Vote.objects.create(
            card=card, category=category, mode=mode, tier=tier, ip=ip_address
        )
    elif existing_vote.tier == tier:
        existing_vote.delete()
    else:
        existing_vote.tier = tier
        existing_vote.save()

    context = guide_body_context(request, VOTE_GUIDES[category])
    html_content = render_to_string("guide/_guide_body.html", context, request=request)
    return JsonResponse({"html_content": html_content})
