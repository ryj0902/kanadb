"""덱 규칙과 통계 (덱 페이지, NPC 상세 공용)"""

from collections import Counter, defaultdict

from card.models import Card

# 총 포인트 상한 -> 덱 등급 (30장 제한상 9999를 넘을 수 없음)
RANK_THRESHOLDS = [(200, "E"), (600, "D"), (1200, "C"), (2000, "B"), (9999, "A")]

THEME_KEYS = ["vita", "academy", "crux", "darklore", "sg"]
RARITY_KEYS = ["COMMON", "UNCOMMON", "SUPERIOR", "RARE", "DOUBLE_RARE", "UNIQUE"]


def parse_card_ids(text):
    """'1,2,x,3' -> [1, 2, 3] (숫자가 아닌 값은 무시)"""
    return [int(card_id) for card_id in text.split(",") if card_id.isdigit()]


def load_cards(card_ids):
    """카드 id 목록 -> 중복을 count로 묶은 카드 목록 (id 순, 없는 id 제외)"""
    counts = Counter(card_ids)
    card_map = Card.objects.in_bulk(list(counts))
    cards = []
    for card_id in sorted(counts):
        card = card_map.get(card_id)
        if card is None:
            continue
        card.count = counts[card_id]
        cards.append(card)
    return cards


def sort_cards(cards):
    return sorted(cards, key=lambda card: (card.category, card.size))


def add_card(current_ids, card_id):
    """덱에 카드 추가: 캐릭터는 교체, 같은 원본 카드는 limit장까지, 결과는 정렬"""
    card_map = Card.objects.in_bulk(set(current_ids) | {card_id})
    target = card_map[card_id]

    if target.is_character:
        for current_id in current_ids:
            if card_map[current_id].is_character:
                current_ids = list(current_ids)
                current_ids.remove(current_id)
                return [card_id, *current_ids]

    same_origin = sum(
        1
        for current_id in current_ids
        if card_map[current_id].enh_orig == target.enh_orig
    )
    if target.limit <= same_origin:
        return current_ids

    cards = sort_cards(card_map[current_id] for current_id in [*current_ids, card_id])
    return [card.id for card in cards]


def remove_card(current_ids, card_id):
    current_ids = list(current_ids)
    if card_id in current_ids:
        current_ids.remove(card_id)
    return current_ids


def _count_with_enhance(counter, label=str):
    """{key: [장수, 강화 합]} -> 'key: 장수(+강화) | ...' (key 순)"""
    parts = []
    for key, (count, enhance) in sorted(counter.items()):
        part = f"{label(key)}: {count}"
        if enhance != 0:
            part += f"(+{enhance})"
        parts.append(part)
    return " | ".join(parts)


def calculate_statistics(cards):
    """카드 목록(각 카드에 count 속성) -> 덱 통계"""
    stat_point = 0
    stat_category = [["amount", 0], ["char", 0], ["spell", 0]]
    stat_size = [0] * 10
    stat_theme = [[key, 0] for key in THEME_KEYS]
    stat_rarity = [[key, 0] for key in RARITY_KEYS]
    episode_stats = defaultdict(lambda: [0, 0])
    tag_stats = defaultdict(lambda: [0, 0])
    tag_us_stats = defaultdict(lambda: [0, 0])

    for card in cards:
        stat_point += card.count * card.point

        if not card.is_character:
            stat_category[0][1] += card.count
            stat_category[1 if card.is_follower else 2][1] += card.count

        # 캐릭터(size 0)는 인덱스 -1(사이즈 10 칸)에 집계된다 (기존 동작 유지)
        stat_size[card.size - 1] += card.count
        stat_theme[card.theme - 1][1] += card.count
        stat_rarity[card.rarity - 1][1] += card.count

        groups = [(episode_stats, [card.episode])]
        groups += [
            (tag_stats, card.tag.split(",")),
            (tag_us_stats, card.tag_us.split(",")),
        ]
        for stats, keys in groups:
            for key in keys:
                stats[key][0] += card.count
                stats[key][1] += card.count * card.enhance

    stat_rank_char = next(
        (rank for limit, rank in RANK_THRESHOLDS if stat_point <= limit), "E"
    )

    return {
        "stat_point": stat_point,
        "stat_rank_char": stat_rank_char,
        "stat_category": stat_category,
        "stat_size": stat_size,
        "stat_theme": stat_theme,
        "stat_rarity": stat_rarity,
        "ep_enh_str": _count_with_enhance(episode_stats, Card.get_episode_string),
        "tag_enh_str": _count_with_enhance(tag_stats),
        "tag_enh_str_us": _count_with_enhance(tag_us_stats),
    }
