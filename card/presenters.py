"""카드 -> 화면/JSON 표시용 데이터 변환 (단일 지점)"""

import re

from django.forms.models import model_to_dict

# 줄바꿈을 <br>로 바꾸는 텍스트 필드
MULTILINE_FIELDS = [
    "skill_turn",
    "skill_instance",
    "skill_attack",
    "skill_defend",
    "desc",
]


def card_data(card):
    """카드 필드 + 이미지 URL + 표시 문자열 (덱 미리보기, 상세 공용)"""
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
    """줄바꿈 -> <br> (◈ 제목 줄은 앞뒤 줄바꿈을 <br>로)"""
    text = text.replace("◈\n", "◈<br>")
    text = text.replace("\n◈", "<br>◈")
    return text.replace("\n", "<br>")


def format_dialogue(text):
    """'◈제목◈\\n내용' 블록들을 문단으로"""
    pattern = r"(◈.*?◈)\s*\n(.*?)(?=\n◈|\Z)"
    paragraphs = [
        f'<p class="p-skill">{title}<br>{content.strip().replace(chr(10), "<br>")}</p>'
        for title, content in re.findall(pattern, text, re.DOTALL)
    ]
    return "\n".join(paragraphs)


def card_detail_data(card):
    """카드 상세 패널용 데이터"""
    data = card_data(card)
    data["tag"] = card.tag.replace(",", ", ")
    data["tag_us"] = card.tag_us.replace(",", ", ")
    for field in MULTILINE_FIELDS:
        data[field] = format_multiline(data[field])
        data[f"{field}_us"] = format_multiline(data[f"{field}_us"])
    data["dial"] = format_dialogue(card.dial)
    data["dial_us"] = format_dialogue(card.dial_us)
    return data
