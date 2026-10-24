"""카드 -> 화면/JSON 표시용 데이터 변환 (단일 지점)"""

import re

from django.forms.models import model_to_dict
from django.utils.html import escape, format_html
from django.utils.safestring import mark_safe
from django.utils.translation import get_language

# 줄바꿈을 <br>로 바꾸는 텍스트 필드
MULTILINE_FIELDS = [
    "skill_turn",
    "skill_instance",
    "skill_attack",
    "skill_defend",
    "desc",
]
SKILL_FIELDS = MULTILINE_FIELDS[:4]


def card_data(card):
    """카드 필드 + 이미지 URL + 표시 문자열"""
    data = model_to_dict(card)
    product1, product2 = card.products
    data.update(
        {
            "url": card.image_url,
            "frame": card.frame_url,
            "frame_enh": card.frame_enhance_url,
            "d_url": card.deck_image_url,
            "d_frame": card.deck_frame_url,
            "d_frame_size": card.deck_frame_size_url,
            "product1_url": product1.image_url,
            "product2_url": product2.image_url,
            "product1": product1.label,
            "product1_us": product1.label_us,
            "product2": product2.label,
            "product2_us": product2.label_us,
            "category": card.get_category_display(),
            "rarity": card.get_rarity_display(),
            "theme": card.get_theme_display(),
            "episode": card.episode_label,
        }
    )
    return data


def format_multiline(text):
    """줄바꿈 -> <br> (◈ 제목 줄은 앞뒤 줄바꿈을 <br>로). 원문은 이스케이프한다"""
    text = escape(text)
    text = text.replace("◈\n", "◈<br>")
    text = text.replace("\n◈", "<br>◈")
    return mark_safe(text.replace("\n", "<br>"))


def format_dialogue(text):
    """'◈제목◈\\n내용' 블록들을 문단으로. 원문은 이스케이프한다"""
    pattern = r"(◈.*?◈)\s*\n(.*?)(?=\n◈|\Z)"
    paragraphs = [
        format_html(
            '<p class="card-detail__paragraph">{}<br>{}</p>',
            title,
            mark_safe(escape(content.strip()).replace("\n", "<br>")),
        )
        for title, content in re.findall(pattern, text, re.DOTALL)
    ]
    return mark_safe("\n".join(paragraphs))


def card_detail_data(card):
    """카드 상세 패널용 데이터 (양 언어)"""
    data = card_data(card)
    data["tag"] = card.tag.replace(",", ", ")
    data["tag_us"] = card.tag_us.replace(",", ", ")
    for field in MULTILINE_FIELDS:
        data[field] = format_multiline(data[field])
        data[f"{field}_us"] = format_multiline(data[f"{field}_us"])
    data["dial"] = format_dialogue(card.dial)
    data["dial_us"] = format_dialogue(card.dial_us)
    return data


def card_detail_context(card):
    """카드 상세 패널 템플릿 컨텍스트 (현재 언어)"""
    data = card_detail_data(card)
    suffix = "" if get_language() == "ko" else "_us"
    products = [
        {"image_url": product.image_url, "label": getattr(product, f"label{suffix}")}
        for product in card.products
        if product.exists
    ]
    return {
        "card": card,
        "name": data[f"name{suffix}"],
        "tag": data[f"tag{suffix}"],
        "skills": [data[f"{field}{suffix}"] for field in SKILL_FIELDS],
        "story": data[f"desc{suffix}"],
        "dialogue": data[f"dial{suffix}"],
        "episode": data["episode"],
        "rarity": data["rarity"],
        "products": products,
    }


def card_detail_state(card):
    """카드 상세 패널의 JS 상태 (링크/강화 이동, 상품 버튼)"""
    return {
        "id": card.id,
        "link_ids": card.link_ids,
        "enh_prev": card.enh_prev,
        "enh_next": card.enh_next,
        "enh_orig": card.enh_orig,
        "has_product": card.products[0].exists,
    }
