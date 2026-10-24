"""게임 데이터(TextAsset JSON) -> card_card / npc_npc 행 변환

manage.py build_gamedata 가 사용한다. DB와 무관한 순수 변환이라 테스트하기 쉽다.
"""

import json
from pathlib import Path

from card.models import Card

NO_ID = -1

# 카드 분류별 대사 종류
DIALOGUE_KINDS = {
    Card.Category.CHARACTER: ["START", "COIN", "SPELL", "SKILL_T", "SKILL_D"],
    Card.Category.SPELL: [],
    Card.Category.FOLLOWER: [
        "ATTACK",
        "COUNTER",
        "DIRECT",
        "SKILL_T",
        "SKILL_A",
        "SKILL_D",
    ],
}

# 대사 제목 (한국어, 영어)
DIALOGUE_TITLES = {
    "START": ("시작시", "Initial"),
    "COIN": ("선공시", "Coin"),
    "SPELL": ("스펠사용시", "Spell"),
    "ATTACK": ("추종자 공격전", "F.Offensive"),
    "COUNTER": ("추종자 반격전", "F.Counter"),
    "DIRECT": ("캐릭터 공격전", "C.Offensive"),
    "SKILL_T": ("턴개시시", "Initial"),
    "SKILL_A": ("공격전", "Offensive"),
    "SKILL_D": ("방어전", "Defensive"),
}

SKILL_KINDS = ["TURN", "INSTANCE", "ATTACK", "DEFEND"]

# 데이터 예외 처리
ALWAYS_COLLECTIBLE = {2100330}  # 탈리티아 몬스터즈: 수집 불가로 되어 있지만 수집 가능
LOADING_OVERRIDES = {99050110: 100100}  # EV5 10층: 로딩 id가 잘못되어 있음

# PVE 챕터 테이블 (일반, 쉐도우랜드, 이벤트, 이벤트 보스) / PVP
PVE_CHAPTERS = ["T_CHAPTER", "S_CHAPTER", "E_CHAPTER", "B_CHAPTER"]
PVP_CHAPTER = "P_CHAPTER"


def load_table(directory, name):
    path = Path(directory) / f"{name}.txt"
    return json.loads(path.read_text(encoding="utf-8-sig"))


class GameData:
    """TextAsset 디렉터리의 표들과 조회 도우미"""

    def __init__(self, directory):
        self.directory = Path(directory)
        self.card_table = load_table(directory, "CARD_TABLE")
        self.cards2 = {
            row["CARD_ID"]: row for row in load_table(directory, "CARD_TABLE2")
        }
        self.products = {
            row["PRODUCT_ID"]: row for row in load_table(directory, "PRODUCT_TABLE")
        }
        # 재료 id는 문자열로 들어 있다 ("-1", "3011")
        for product in self.products.values():
            for key in ["PRODUCT_MATERIAL1", "PRODUCT_MATERIAL2"]:
                product[key] = int(product[key])
        self.loadings = {
            row["LOADING_ID"]: row for row in load_table(directory, "LOADING_TABLE")
        }
        self.setups = {row["SETUP_ID"]: row for row in load_table(directory, "SETUP")}
        self.chapters = {
            name: load_table(directory, name) for name in [*PVE_CHAPTERS, PVP_CHAPTER]
        }

        # 같은 STRING_NAME이 여러 번 나오는 경우가 있어 모두 보관한다
        self.strings = {}
        for row in load_table(directory, "STRING"):
            self.strings.setdefault(row["STRING_NAME"], []).append(row)

    def text(self, key):
        """(한국어, 영어) - 키가 하나뿐이어야 한다"""
        rows = self.strings[key]
        if len(rows) != 1:
            raise ValueError(f"문자열 키가 중복됨: {key}")
        return rows[0]["STRING_KR"], rows[0]["STRING_US"]

    def first_text(self, key):
        """(한국어, 영어) - 중복 키면 첫 번째"""
        row = self.strings[key][0]
        return row["STRING_KR"], row["STRING_US"]


# --- 카드 ---


def card_tags(data, card):
    """태그 (한국어, 영어) - 문자열이 없는 태그는 건너뛴다"""
    tags_ko, tags_us = [], []
    for tag in card["CARD_TAG"]:
        try:
            ko, us = data.text(tag)
        except KeyError, ValueError:
            continue
        tags_ko.append(ko)
        tags_us.append(us)
    return ",".join(tags_ko), ",".join(tags_us)


def card_skill(data, card_id, kind):
    """스킬 설명 (한국어, 영어) - -1 또는 문자열이 없는 스킬에서 멈춘다"""
    skills_ko, skills_us = [], []
    for skill in data.cards2[card_id][f"CARD_SKILL_{kind}"]:
        if skill == NO_ID:
            break
        try:
            ko, us = data.text(f"SKILL_TEXT_{skill}")
        except KeyError, ValueError:
            break
        skills_ko.append(ko)
        skills_us.append(us)
    return "\n".join(skills_ko), "\n".join(skills_us)


def card_dialogue(data, card_id, category):
    """대사 (한국어, 영어): '◈ 제목 ◈\\n대사' 블록들"""
    dialogues_ko, dialogues_us = [], []
    for kind in DIALOGUE_KINDS[category]:
        rows = data.strings.get(f"CARD_DIALOGUE_{kind}_{card_id}")
        if not rows:
            continue
        # 키가 중복된 경우(예: 3004070)도 첫 번째 대사를 쓴다
        title_ko, title_us = DIALOGUE_TITLES[kind]
        dialogues_ko.append(f"◈ {title_ko} ◈\n{rows[0]['STRING_KR']}")
        dialogues_us.append(f"◈ {title_us} ◈\n{rows[0]['STRING_US']}")
    return "\n".join(dialogues_ko), "\n".join(dialogues_us)


def card_product(data, card_id):
    """제작 재료 2종: 'id,수량,이름,영어 이름' x 2 (없으면 -1,-1,-1,-1)"""
    product = data.products[card_id]
    parts = []
    for i in [1, 2]:
        product_id = product[f"PRODUCT_MATERIAL{i}"]
        if product_id == NO_ID:
            parts.append("-1,-1,-1,-1")
            continue
        name_ko, name_us = data.text(f"CASH_NAME_{product_id}")
        parts.append(f"{product_id},{product[f'PRODUCT_VALUE{i}']},{name_ko},{name_us}")
    return ",".join(parts)


def build_cards(data, texture_dir):
    """card_card 행 목록

    - 이미지가 없는 기본 카드(id 끝자리 0)는 제외
    - 강화 카드는 바로 앞 카드와 강화 단계로 연결 (특수 추종자 Ver.가 아니면 원본 이미지가 있어야 함)
    """
    texture_dir = Path(texture_dir)
    cards = []
    enh_orig = None

    for card in data.card_table:
        card_id = card["CARD_ID"]
        if card_id % 10 == 0 and not (texture_dir / f"CARD_{card_id}.webp").is_file():
            continue

        card2 = data.cards2[card_id]
        name, name_us = data.text(card2["CARD_NAME"])
        desc, desc_us = data.text(card2["CARD_DESC"])
        tag, tag_us = card_tags(data, card)
        row = {
            "id": card_id,
            "name": name,
            "name_us": name_us,
            "category": Card.Category[card["CARD_CATEGORY"]].value,
            "rarity": Card.Rarity[card["CARD_RARITY"]].value,
            "theme": Card.Theme[card["CARD_THEME"]].value,
            "tag": tag,
            "tag_us": tag_us,
            "episode": Card.episode_from_code(card["CARD_EPISODE"]),
            "point": card["CARD_POINT"],
            "size": card["CARD_SIZE"],
            "atk": card["CARD_ATK"],
            "defs": card["CARD_DEF"],
            "hp": card["CARD_HP"],
            "limit": card["CARD_LIMIT"],
            "enhance": card["CARD_ENHANCE"],
            "frame": card["CARD_FRAME"],
            "collect": card_id in ALWAYS_COLLECTIBLE or card["CARD_COLLECT"],
            "desc": desc,
            "desc_us": desc_us,
            "link": ",".join(str(link_id) for link_id in card2["CARD_LINK"]),
            "producible": data.products[card_id]["PRODUCT_MATERIAL1"] != NO_ID,
            "product": card_product(data, card_id),
            "enh_prev": NO_ID,
            "enh_next": NO_ID,
        }
        for kind in SKILL_KINDS:
            field = f"skill_{kind.lower()}"
            row[field], row[f"{field}_us"] = card_skill(data, card_id, kind)

        if row["enhance"] == 0:
            enh_orig = card_id
        else:
            original_image = texture_dir / f"CARD_{card_id - row['enhance']}.webp"
            if not original_image.is_file() and "Ver" not in name:
                continue
            previous = cards[-1]
            previous["enh_next"] = card_id
            row["producible"] = previous["producible"]
            row["enh_prev"] = previous["id"]
        row["enh_orig"] = enh_orig
        row["dial"], row["dial_us"] = card_dialogue(data, enh_orig, row["category"])

        cards.append(row)
    return cards


# --- NPC ---


def setup_id(chapter):
    """'..._<setup id>' -> setup id"""
    return int(chapter["CHAPTER_NPC"].split("_")[-1])


def pve_npc(data, chapter):
    """PVE 챕터 -> npc_npc 행 (로딩 정보가 없으면 None)"""
    if chapter["CHAPTER_LOADING"] not in data.loadings:
        return None
    loading_id = LOADING_OVERRIDES.get(
        chapter["CHAPTER_ID"], chapter["CHAPTER_LOADING"]
    )
    loading = data.loadings[loading_id]
    chapter_name, chapter_name_us = data.text(chapter["CHAPTER_TITLE"])
    loading_name, loading_name_us = data.text(loading["LOADING_DESC1"])
    loading_desc, loading_desc_us = data.text(loading["LOADING_DESC2"])
    return {
        "id": chapter["CHAPTER_ID"],
        "chapter_name": chapter_name,
        "chapter_name_us": chapter_name_us,
        "loading_name": loading_name,
        "loading_name_us": loading_name_us,
        "loading_desc": loading_desc,
        "loading_desc_us": loading_desc_us,
        "setup": ",".join(map(str, data.setups[setup_id(chapter)]["SETUP_CARD"])),
    }


def pvp_npc(data, chapter):
    """PVP 챕터 -> npc_npc 행 (이름: NPC 이름, 부제: 캐릭터 카드 이름, 설명 없음)"""
    setup_card = data.setups[setup_id(chapter)]["SETUP_CARD"]
    chapter_name, chapter_name_us = data.text(chapter["CHAPTER_NPC"])
    character_name, character_name_us = data.text(
        f"CARD_NAME_{setup_card[0] // 10 * 10}"
    )
    return {
        "id": chapter["CHAPTER_ID"],
        "chapter_name": chapter_name,
        "chapter_name_us": chapter_name_us,
        "loading_name": character_name,
        "loading_name_us": character_name_us,
        "loading_desc": "",
        "loading_desc_us": "",
        "setup": ",".join(map(str, setup_card)),
    }


def build_npcs(data):
    npcs = []
    for name in PVE_CHAPTERS:
        for chapter in data.chapters[name]:
            npc = pve_npc(data, chapter)
            if npc is not None:
                npcs.append(npc)
    for chapter in data.chapters[PVP_CHAPTER]:
        npcs.append(pvp_npc(data, chapter))
    return npcs


# --- 이미지 ---


def fix_swapped_card_images(texture_dir, log=print):
    """'CARD_<id> #<n>.webp'가 원래 크기(높이 480)인 경우 기본 파일과 이름을 맞바꾼다"""
    from PIL import Image  # 파이프라인 전용 의존성

    for path in sorted(Path(texture_dir).glob("CARD_*#*.webp")):
        with Image.open(path) as image:
            _, height = image.size
        if height != 480:
            continue
        base = path.parent / f"{path.stem.split(' #')[0]}.webp"
        if not base.exists():
            log(f"[error] 짝이 되는 기본 파일({base.name})이 존재하지 않습니다.")
            continue
        temp = path.with_name(path.name + ".temp")
        path.rename(temp)
        base.rename(path)
        temp.rename(base)
        log(f"[done] {path.name} <-> {base.name}")
