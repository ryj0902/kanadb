import json
import math
import os
from collections import Counter
from glob import glob

from django.http import HttpRequest, JsonResponse
from django.shortcuts import render
from django.utils.safestring import mark_safe
from django.utils.translation import get_language
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST
from markdown import markdown

from card.models import Card, Vote
from guide.templatetags.guide_filters import card_filter


def index(request):
    language_code = get_language()
    context = {"contents": []}

    for file in sorted(glob(f"templates/guide/{language_code}/*.md")):
        with open(file, "r", encoding="utf-8") as f:
            line = f.readline()

        title = line.rstrip()
        title = title.split("# ")[1]

        context["contents"].append([os.path.basename(file), title])

    return render(request, "guide/index.html", context)


def guide_detail(request, guide_name):
    language_code = get_language()
    markdown_path = f"templates/guide/{language_code}/{guide_name}"

    with open(markdown_path, "r", encoding="utf-8") as file:
        markdown_content = file.read()

    if guide_name == "guide3.md":  # 유니크 티어 리스트
        content = guide_vote(request, "unique")
        markdown_content += content
    elif guide_name == "guide4.md":  # 제국 DR 추종자 티어 리스트
        content = guide_vote(request, "empire_dr")
        markdown_content += content

    html_content = markdown(markdown_content, extensions=["extra"])

    context = {
        "html_content": html_content,
        "horizontal_layout": _("가로 모드"),
        "vertical_layout": _("세로 모드"),
    }

    return render(request, "guide/guide_detail.html", context)


def get_client_ip(request: HttpRequest):
    """사용자의 IP 주소 가져오기"""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


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
    user_votes = Vote.objects.filter(ip=user_ip, mode=mode, **vote_filter)
    user_voted_cards = {vote.card.id: vote.tier for vote in user_votes}

    for card in cards:
        votings = Vote.objects.filter(card=card.id, mode=mode, **vote_filter)
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
    data = json.loads(request.body)
    card_id = data.get("cardId")
    tier = data.get("tier")
    category = data.get("category")
    mode = int(data.get("mode", 0))  # 별도 전달값이 없으면 기본값 0(PVP) 사용
    ip_address = get_client_ip(request)

    card = Card.objects.filter(id=card_id).first()

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
    language_code = get_language()
    guide_name = os.path.basename(request.META.get("HTTP_REFERER", "").strip("/"))
    markdown_path = f"templates/guide/{language_code}/{guide_name}"

    with open(markdown_path, "r", encoding="utf-8") as file:
        markdown_content = file.read()

    updated_content = guide_vote(request, category)
    full_content = markdown_content + updated_content
    html_content = markdown(full_content, extensions=["extra"])
    filtered_html = card_filter(html_content)

    return JsonResponse({"html_content": filtered_html})
