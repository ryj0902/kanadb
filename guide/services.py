"""티어 리스트 투표 집계"""

import math
from collections import Counter, defaultdict

from django.db.models import Count, Min

from card.models import Card, Vote

# 투표 카테고리별 대상 카드
CATEGORY_CARDS = {
    "unique": {"collect": True, "rarity": Card.Rarity.UNIQUE},
    "empire_dr": {
        "category": Card.Category.FOLLOWER,
        "rarity": Card.Rarity.DOUBLE_RARE,
        "tag__icontains": "제국",
        "enhance": 5,
    },
}

# 카테고리별로 보여 줄 모드 (PVP/PVE 2열 또는 PVP 1열)
CATEGORY_MODES = {
    "unique": [0, 1],
    "empire_dr": [0],
}

DEFAULT_TIER = 5  # 투표가 없는 카드


def decide_tier(tier_counts):
    """최다 득표 티어. 1, 2위가 동률이면 두 티어의 평균(올림)"""
    if not tier_counts:
        return DEFAULT_TIER
    top = tier_counts.most_common(2)
    if len(top) == 1 or top[0][1] != top[1][1]:
        return top[0][0]
    return math.ceil((top[0][0] + top[1][0]) / 2)


def sort_key(card_id, tier_counts, tier):
    """같은 티어 안 정렬: 해당 티어 이상 득표가 많고, 아래 티어 득표가 적은 순"""
    upper = [-tier_counts.get(t, 0) for t in range(tier + 1)]
    lower = [tier_counts.get(t, 0) for t in range(tier + 1, len(Vote.TIER_MAP))]
    return (*upper, *lower, card_id)


def tier_list(category, mode, ip):
    """[{"tier": 0, "label": "S", "entries": [{card, my_vote, votes}, ...]}, ...]"""
    votes = Vote.objects.filter(category=category, mode=mode, tier__in=Vote.TIER_MAP)

    # 티어별 득표 (Counter 동률 순서가 기존과 같도록 티어별 첫 투표 순)
    counts = defaultdict(Counter)
    rows = (
        votes.values("card_id", "tier")
        .annotate(count=Count("id"), first=Min("id"))
        .order_by("first")
    )
    for row in rows:
        counts[row["card_id"]][row["tier"]] = row["count"]

    my_votes = dict(votes.filter(ip=ip).values_list("card_id", "tier"))

    table = [[] for _ in Vote.TIER_MAP]
    for card in Card.objects.filter(**CATEGORY_CARDS[category]):
        tier_counts = counts[card.id]
        table[decide_tier(tier_counts)].append(
            {
                "card": card,
                "my_vote": my_votes.get(card.id),
                "votes": [
                    {"tier": t, "label": label, "count": tier_counts.get(t, 0)}
                    for t, label in Vote.TIER_MAP.items()
                ],
                "tier_counts": tier_counts,
            }
        )

    result = []
    for tier, label in Vote.TIER_MAP.items():
        entries = sorted(
            table[tier], key=lambda e: sort_key(e["card"].id, e["tier_counts"], tier)
        )
        result.append({"tier": tier, "label": label, "entries": entries})
    return result


def tier_columns(category, ip):
    """카테고리의 모드별 티어 리스트 [{"mode": 0, "label": "PVP", "tiers": [...]}, ...]"""
    return [
        {
            "mode": mode,
            "label": Vote.MODE_MAP[mode],
            "tiers": tier_list(category, mode, ip),
        }
        for mode in CATEGORY_MODES[category]
    ]
