from django.db import models
from django.templatetags.static import static
from django.utils.translation import get_language
from django.utils.translation import gettext_lazy as _

from .querysets import CardQuerySet

DECK_SIZE = 30  # 캐릭터를 제외한 덱 최대 장수
PAGE_SIZE = 12  # 검색 결과 페이지당 카드 수
FILTER_ROW_SIZE = 9  # 검색 필터 한 줄당 체크박스 수
SIZE_RANGE = range(1, 11)  # 카드 사이즈 (캐릭터는 0)

NO_ID = -1  # 강화/링크/상품이 없음을 나타내는 값


def texture_url(name):
    return static(f"card/Texture2D/{name}.webp")


class Product:
    """카드 제작 재료 (상품 아이콘 + 수량)"""

    def __init__(self, product_id, count, name, name_us):
        self.id = product_id
        self.count = count
        self.name = name
        self.name_us = name_us

    @property
    def exists(self):
        return self.id != str(NO_ID)

    @property
    def image_url(self):
        return texture_url(f"CASH_{self.id}_I") if self.exists else str(NO_ID)

    @property
    def label(self):
        return f"{self.name} x {self.count}"

    @property
    def label_us(self):
        return f"{self.name_us} x {self.count}"


class Card(models.Model):
    # 멤버 이름은 게임 데이터(CARD_TABLE)의 값과 같다
    class Category(models.IntegerChoices):
        CHARACTER = 1, _("캐릭터")
        SPELL = 2, _("스펠")
        FOLLOWER = 3, _("추종자")

    # 멤버 이름은 게임 데이터(CARD_TABLE)의 값과 같다
    class Rarity(models.IntegerChoices):
        COMMON = 1, _("커먼")
        UNCOMMON = 2, _("언커먼")
        SUPERIOR = 3, _("슈페리어")
        RARE = 4, _("레어")
        DOUBLE_RARE = 5, _("더블레어")
        UNIQUE = 6, _("유니크")

    # 멤버 이름은 게임 데이터(CARD_TABLE)의 값과 같다
    class Theme(models.IntegerChoices):
        PUBLIC = 1, _("공립")
        PRIVATE = 2, _("사립")
        CRUX = 3, _("크룩스")
        DARK_LORE = 4, _("다크로어")
        INDEPENDENCE = 5, _("무소속")

    # 에피소드 값: 1xx 에피소드(EP), 5xx 이벤트(EV), 8xx 명계 등(MH), 901/902 엑스트라
    EPISODE_SEASON1 = [(100 + i, f"EP{i}") for i in range(9)]
    EPISODE_SEASON2 = [(100 + i, f"EP{i}") for i in range(9, 17)]
    EPISODE_SEASON3 = [(100 + i, f"EP{i}") for i in range(17, 18)]
    EPISODE_EVENT = (
        [(500 + i, f"EV{i}") for i in range(12)] + [(516, "EV16")] + [(518, "EV18")]
    )
    EPISODE_EXTRA = [
        (901, _("쉐도우랜드")),
        (902, _("제국")),
        (800, _("명계")),
        (829, _("차원의 틈")),
        (830, _("재료")),
    ]

    id = models.BigIntegerField(primary_key=True)
    name = models.TextField()
    name_us = models.TextField()
    category = models.IntegerField(choices=Category.choices)
    rarity = models.IntegerField(choices=Rarity.choices)
    theme = models.IntegerField(choices=Theme.choices)
    tag = models.TextField()
    tag_us = models.TextField()
    episode = models.IntegerField()
    point = models.IntegerField()
    size = models.IntegerField()
    atk = models.IntegerField()
    defs = models.IntegerField()
    hp = models.IntegerField()
    limit = models.IntegerField()
    enhance = models.IntegerField()
    frame = models.TextField()  # image file name
    collect = models.BooleanField()
    desc = models.TextField()
    dial = models.TextField()
    skill_turn = models.TextField()
    skill_instance = models.TextField()
    skill_attack = models.TextField()
    skill_defend = models.TextField()
    desc_us = models.TextField()
    dial_us = models.TextField()
    skill_turn_us = models.TextField()
    skill_instance_us = models.TextField()
    skill_attack_us = models.TextField()
    skill_defend_us = models.TextField()
    link = models.TextField()  # list of id
    producible = models.BooleanField()
    product = models.TextField()  # id,count,name,name_us x 2
    enh_prev = models.IntegerField()  # card id
    enh_next = models.IntegerField()  # card id
    enh_orig = models.IntegerField()  # card id

    objects = CardQuerySet.as_manager()

    class Meta:
        # 마지막 id: 같은 순위끼리도 순서가 고정되어 페이지 이동 시 중복/누락이 없다
        ordering = ["category", "theme", "episode", "point", "id"]

    def __str__(self):
        return self.name

    @staticmethod
    def get_episode_string(episode):
        """에피소드 값 -> 표시 문자열 (101 -> EP1, 503 -> EV3, 829 -> MH29, 901 -> SH)"""
        if episode // 100 < 9:
            prefix = {1: "EP", 5: "EV"}.get(episode // 100, "MH")
            return prefix + str(episode % 100)
        return {901: "SH", 902: "EM"}.get(episode, episode)

    @staticmethod
    def episode_from_code(code):
        """게임 데이터의 에피소드 코드 -> 저장 값 (EP1 -> 101, EV3 -> 503, MH29 -> 829, SH -> 901)"""
        prefixes = {"EP": 100, "EV": 500, "MH": 800}
        if code[:2] in prefixes:
            return prefixes[code[:2]] + int(code[2:])
        extras = {"SH": 901, "EM": 902}
        if code in extras:
            return extras[code]
        raise ValueError(f"알 수 없는 에피소드 코드: {code}")

    def localized(self, field):
        """현재 언어에 맞는 필드 값 (영어면 <field>_us)"""
        return getattr(self, field if get_language() == "ko" else f"{field}_us")

    @property
    def localized_name(self):
        return self.localized("name")

    # --- 분류 ---

    @property
    def is_character(self):
        return self.category == self.Category.CHARACTER

    @property
    def is_spell(self):
        return self.category == self.Category.SPELL

    @property
    def is_follower(self):
        return self.category == self.Category.FOLLOWER

    @property
    def episode_label(self):
        return self.get_episode_string(self.episode)

    # --- 이미지 ---

    @property
    def image_url(self):
        return texture_url(f"CARD_{self.id // 10 * 10}")

    @property
    def deck_image_url(self):
        """덱 미리보기용 가로형 이미지"""
        return texture_url(f"D_CARD_{self.id // 10 * 10}")

    @property
    def frame_url(self):
        return texture_url(self.frame)

    @property
    def frame_enhance_url(self):
        return texture_url("UI_Layout_enhance")

    @property
    def deck_frame_url(self):
        return texture_url("UI_card_frame")

    @property
    def deck_frame_size_url(self):
        return texture_url("UI_icon_cost")

    # --- 연관 데이터 ---

    @property
    def products(self):
        """제작 재료 2종 (없으면 id가 -1)"""
        values = self.product.split(",")
        return [Product(*values[0:4]), Product(*values[4:8])]

    @property
    def link_ids(self):
        return [] if self.link == str(NO_ID) else [int(i) for i in self.link.split(",")]


class Vote(models.Model):
    """가이드 티어 리스트 투표 (IP당 카드/카테고리/모드별 1표)"""

    TIER_MAP = {0: "S", 1: "A", 2: "B", 3: "C", 4: "D", 5: "E"}
    MODE_MAP = {0: "PVP", 1: "PVE"}

    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    ip = models.GenericIPAddressField()
    tier = models.IntegerField()
    category = models.TextField()
    mode = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["card", "ip", "category", "mode"],
                name="unique_card_ip_category_mode",
            )
        ]

    def __str__(self):
        return (
            f"Vote(id={self.card_id}, ip={self.ip}, "
            f"mode={self.MODE_MAP.get(self.mode)}, tier={self.TIER_MAP.get(self.tier)})"
        )
