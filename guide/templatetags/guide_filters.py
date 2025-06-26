import re

from django import template
from django.templatetags.static import static

from card.models import Vote

register = template.Library()


@register.filter()
def card_filter(value):
    def replace_vote(text, num, voted_tier="-1", tier_votes="", category="unique"):
        """투표 UI를 생성하는 함수"""
        link = (
            f'<a href="javascript:void(0);" onclick="selectCard({num}, 0)">{text}</a>'
        )
        images = ""

        # 티어별 투표 수를 딕셔너리로 변환
        vote_counts = (
            dict(item.split(":") for item in tier_votes.split(","))
            if tier_votes
            else {}
        )

        for index, tier in Vote.TIER_MAP.items():
            deactive_class = "deactive" if str(voted_tier) != str(index) else ""
            vote_count = vote_counts.get(str(index), "0")

            images += (
                f'<img src="{static(f"card/Texture2D/result_{tier}.webp")}" '
                f'alt="{tier}" class="vote-tier-img {deactive_class}" '
                f"onclick=\"voteTier({num}, '{category}', {index})\" "
                f'id="vote-img-{num}-{index}">'
                f'<span class="vote-count" id="vote-count-{num}-{index}"> {vote_count} </span>'
            )

        return f'{link}&nbsp;&nbsp;&nbsp;&nbsp;{images} <span id="vote-result-{num}"></span>'

    def replace_card(match):
        """일반 카드 링크 생성"""
        text, num = match.group(1), match.group(2)
        return (
            f'<a href="javascript:void(0);" onclick="selectCard({num}, 0)">{text}</a>'
        )

    # parse {str}(int)(category: str)(vote: int)(votes: str) pattern (이미 투표한 경우)
    value = re.sub(
        r"\{(.+?)\}\((\d+)\)\(category: (.+?)\)\(vote: (\d+)\)\(votes: ([\d:,]*)\)",
        lambda m: replace_vote(
            m.group(1), m.group(2), m.group(4), m.group(5), m.group(3)
        ),
        value,
    )

    # parse {str}(int)(category: str)(vote)(votes: str) pattern (투표하지 않은 경우)
    value = re.sub(
        r"\{(.+?)\}\((\d+)\)\(category: (.+?)\)\(vote\)\(votes: ([\d:,]*)\)",
        lambda m: replace_vote(m.group(1), m.group(2), "-1", m.group(4), m.group(3)),
        value,
    )

    # parse {str}(int) pattern (단순 카드 링크)
    value = re.sub(r"\{(.+?)\}\((\d+)\)", replace_card, value)

    return value
