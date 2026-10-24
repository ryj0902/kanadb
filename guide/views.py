import json
import math
from collections import Counter

from django.conf import settings
from django.http import Http404, HttpRequest, JsonResponse
from django.shortcuts import render
from django.utils.safestring import mark_safe
from django.utils.translation import get_language
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST
from markdown import markdown

from card.models import Card, Vote
from guide.templatetags.guide_filters import card_filter

GUIDE_DIR = settings.BASE_DIR / "templates" / "guide"

# 투표 카테고리 -> 티어 리스트가 붙는 가이드 파일
VOTE_GUIDES = {
    "unique": "guide3.md",  # 유니크 티어 리스트
    "empire_dr": "guide4.md",  # 제국 DR 추종자 티어 리스트
}


def get_guide_files():
    """현재 언어의 가이드 마크다운 파일 목록"""
    return sorted((GUIDE_DIR / get_language()).glob("*.md"))


def read_guide(guide_name):
    """가이드 마크다운 원문 읽기 (목록에 없는 파일이면 404)"""
    for file in get_guide_files():
        if file.name == guide_name:
            return file.read_text(encoding="utf-8")
    raise Http404


def index(request):
    context = {"contents": []}

    for file in get_guide_files():
        with open(file, "r", encoding="utf-8") as f:
            line = f.readline()

        title = line.rstrip()
        title = title.split("# ")[1]

        context["contents"].append([file.name, title])

    return render(request, "guide/index.html", context)


def guide_detail(request, guide_name):
    markdown_content = read_guide(guide_name)

    for category, vote_guide_name in VOTE_GUIDES.items():
        if guide_name == vote_guide_name:
            markdown_content += guide_vote(request, category)

    html_content = markdown(markdown_content, extensions=["extra"])

    context = {
        "html_content": html_content,
        "horizontal_layout": _("가로 모드"),
        "vertical_layout": _("세로 모드"),
    }

    return render(request, "guide/guide_detail.html", context)


def get_client_ip(request: HttpRequest):
    """사용자의 IP 주소 가져오기

    X-Forwarded-For의 앞쪽 값은 클라이언트가 임의로 넣을 수 있으므로,
    신뢰하는 프록시(NUM_PROXIES개)가 덧붙인 뒤쪽 값을 사용한다.
    """
    num_proxies = getattr(settings, "NUM_PROXIES", 1)
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if num_proxies and x_forwarded_for:
        ips = [ip.strip() for ip in x_forwarded_for.split(",")]
        return ips[max(len(ips) - num_proxies, 0)]
    return request.META.get("REMOTE_ADDR")


def guide_vote_mode(request, guide_category, mode=0):
    """지정한 mode (0: PVP/기본값, 1: PVE)에 대한 티어 리스트 마크다운 생성"""
    if guide_category == "unique":
        card_filter = {"collect": True, "rarity": 6}
        vote_filter = {"category": "unique"}
    elif guide_category == "empire_dr":
        card_filter = {
            "category": 3,  # 추종자
            "rarity": 5,  # 더블레어
            "tag__icontains": "제국",
            "enhance": 5,
        }
        vote_filter = {"category": "empire_dr"}

    user_ip = get_client_ip(request)
    language_code = get_language()

    cards = Card.objects.filter(**card_filter)

    tier_table = [[] for _ in range(len(Vote.TIER_MAP))]
    # 범위를 벗어난 tier 값이 저장되어 있어도 집계가 깨지지 않도록 제외
    valid_votes = Vote.objects.filter(
        tier__in=Vote.TIER_MAP, mode=mode, **vote_filter
    )
    user_votes = valid_votes.filter(ip=user_ip)
    user_voted_cards = {vote.card.id: vote.tier for vote in user_votes}

    for card in cards:
        votings = valid_votes.filter(card=card.id)
        tier_counts = Counter(votings.values_list("tier", flat=True))
        already_voted = user_voted_cards.get(card.id, None)

        if tier_counts:
            most_common_tiers = tier_counts.most_common(2)
            if (
                len(most_common_tiers) == 1
                or most_common_tiers[0][1] != most_common_tiers[1][1]
            ):
                most_common_tier = most_common_tiers[0][0]
            else:
                most_common_tier = math.ceil(
                    (most_common_tiers[0][0] + most_common_tiers[1][0]) / 2
                )
        else:
            most_common_tier = 5

        tier_table[most_common_tier].append(
            [card.id, card.name, card.name_us, already_voted, dict(tier_counts)]
        )

    def get_sort_key(card_entry, target_tier):
        counts = card_entry[4]
        key = []

        for t in range(target_tier + 1):
            key.append(-counts.get(t, 0))

        for t in range(target_tier + 1, len(Vote.TIER_MAP)):
            key.append(counts.get(t, 0))

        key.append(card_entry[0])
        return tuple(key)

    for tier, card_list in enumerate(tier_table):
        card_list.sort(key=lambda entry: get_sort_key(entry, tier))

    content = "\n\n"
    for index, value in Vote.TIER_MAP.items():
        content += f"## {value}\n\n"
        for id, name, name_us, voted_tier, tier_votes in tier_table[index]:
            name = name if language_code == "ko" else name_us
            votes_str = ",".join(f"{k}:{v}" for k, v in tier_votes.items())

            if voted_tier is not None:
                content += f"* {{{name}}}({id})(category: {guide_category})(mode: {mode})(vote: {voted_tier})(votes: {votes_str})  \n"
            else:
                content += f"* {{{name}}}({id})(category: {guide_category})(mode: {mode})(vote)(votes: {votes_str})  \n"

    return content


def guide_vote(request, guide_category):
    """가이드 카테고리에 맞춰 2열(유니크) 또는 단일열(제국 DR 등) 레이아웃 생성"""
    if guide_category == "unique":
        # 1. PVP(mode=0), PVE(mode=1) 마크다운 텍스트 각각 생성
        pvp_md = guide_vote_mode(request, guide_category, mode=0)
        pve_md = guide_vote_mode(request, guide_category, mode=1)

        # 2. div 태그에 넣기 전 미리 마크다운 -> HTML 변환 실행 (깨짐 방지 핵심)
        pvp_html = markdown(f"# PVP\n\n{pvp_md}")
        pve_html = markdown(f"# PVE\n\n{pve_md}")

        # 3. HTML로 변환된 결과를 2열 Flex 레이아웃 컨테이너로 감싸기
        container = f"""
<div class="tier-flex-container" style="display: flex; gap: 24px; width: 100%;">
  <div class="tier-column pvp-column" style="flex: 1; min-width: 0;">
    {pvp_html}
  </div>
  <div class="tier-column pve-column" style="flex: 1; min-width: 0;">
    {pve_html}
  </div>
</div>
"""
        return mark_safe(container)
    else:
        # 단일 열 가이드(제국 DR 등)도 마크다운 -> HTML 변환 후 반환
        single_md = guide_vote_mode(request, guide_category, mode=0)
        return mark_safe(markdown(single_md))


@require_POST
def vote(request):
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

    if existing_vote:
        if existing_vote.tier == tier:
            existing_vote.delete()
        else:
            existing_vote.tier = tier
            existing_vote.save()
    else:
        Vote.objects.create(
            card=card, category=category, mode=mode, tier=tier, ip=ip_address
        )

    # reload title
    markdown_content = read_guide(VOTE_GUIDES[category])

    updated_content = guide_vote(request, category)
    full_content = markdown_content + updated_content
    html_content = markdown(full_content, extensions=["extra"])
    filtered_html = card_filter(html_content)

    return JsonResponse({"html_content": filtered_html})
