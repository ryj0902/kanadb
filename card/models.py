from django.db import models
from django.templatetags.static import static
from django.utils.translation import gettext_lazy as _


class Card(models.Model):
    CATEGORY_CHOICES = [(1, _("캐릭터")), (2, _("스펠")), (3, _("추종자"))]
    RARITY_CHOICES = [
        (1, _("커먼")),
        (2, _("언커먼")),
        (3, _("슈페리어")),
        (4, _("레어")),
        (5, _("더블레어")),
        (6, _("유니크")),
    ]
    THEME_CHOICES = [
        (1, _("공립")),
        (2, _("사립")),
        (3, _("크룩스")),
        (4, _("다크로어")),
        (5, _("무소속")),
    ]
    EPISODE_SEASON1 = [(100 + i, f"EP{i}") for i in range(0, 9)]
    EPISODE_SEASON2 = [(100 + i, f"EP{i}") for i in range(9, 17)]
    EPISODE_EVENT = (
        [(500 + i, f"EV{i}") for i in range(0, 12)] + [(516, "EV16")] + [(518, "EV18")]
    )
    EPISODE_EXTRA = [
        (901, _("쉐도우랜드")),
        (902, _("제국")),
        (800, _("명계")),
        (829, _("차원의 틈")),
        (830, _("재료")),
    ]

    id = models.IntegerField(primary_key=True)
    name = models.TextField()
    name_us = models.TextField()
    category = models.IntegerField()
    rarity = models.IntegerField()
    theme = models.IntegerField()
    tag = models.TextField()  # list of string
    tag_us = models.TextField()  # list of string
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
    skill_turn = models.TextField()
    skill_instance = models.TextField()
    skill_attack = models.TextField()
    skill_defend = models.TextField()
    desc_us = models.TextField()
    skill_turn_us = models.TextField()
    skill_instance_us = models.TextField()
    skill_attack_us = models.TextField()
    skill_defend_us = models.TextField()
    link = models.TextField()  # list of id
    producible = models.BooleanField()
    product = models.TextField()
    enh_prev = models.IntegerField()  # card id
    enh_next = models.IntegerField()  # card id
    enh_orig = models.IntegerField()  # card id

    # parsing variable
    category_map = dict()
    for value in CATEGORY_CHOICES:
        category_map[value[0]] = value[1]

    rarity_map = dict()
    for value in RARITY_CHOICES:
        rarity_map[value[0]] = value[1]

    theme_map = dict()
    for value in THEME_CHOICES:
        theme_map[value[0]] = value[1]

    def __str__(self):
        return self.name

    @staticmethod
    def parse_to_string(card):
        def get_episode_string(int_episode):
            episode = int_episode
            if episode // 100 < 9:
                if episode // 100 == 1:
                    prefix = "EP"
                elif episode // 100 == 5:
                    prefix = "EV"
                else:  # 8
                    prefix = "MH"

                episode = prefix + str(int_episode % 100)
            else:
                if episode == 901:
                    episode = "SH"
                elif episode == 902:
                    episode = "EM"

            return episode

        if isinstance(card, dict):
            card["category"] = Card.category_map[card["category"]]
            card["rarity"] = Card.rarity_map[card["rarity"]]
            card["theme"] = Card.theme_map[card["theme"]]
            card["episode"] = get_episode_string(card["episode"])

            product_split = card["product"].split(",")
            card["product1"] = f"{product_split[2]} x {product_split[1]}"
            card["product1_us"] = f"{product_split[3]} x {product_split[1]}"
            card["product2"] = f"{product_split[6]} x {product_split[5]}"
            card["product2_us"] = f"{product_split[7]} x {product_split[5]}"

        else:
            card.category = Card.category_map[card.category]
            card.rarity = Card.rarity_map[card.rarity]
            card.theme = Card.theme_map[card.theme]
            card.episode = get_episode_string(card.episode)

            product_split = card.product.split(",")
            card.product1 = f"{product_split[2]} x {product_split[1]}"
            card.product1_us = f"{product_split[3]} x {product_split[1]}"
            card.product2 = f"{product_split[6]} x {product_split[5]}"
            card.product2_us = f"{product_split[7]} x {product_split[5]}"

    @staticmethod
    def parse_static_url(card):
        if isinstance(card, dict):
            card["url"] = static(
                f"card/Texture2D/CARD_{int(card['id'] // 10 * 10)}.png"
            )
            card["frame"] = static(f"card/Texture2D/{card['frame']}.png")
            card["frame_enh"] = static("card/Texture2D/UI_Layout_enhance.png")

            product_split = card["product"].split(",")
            product1_id, product2_id = product_split[0], product_split[4]
            card["product1_url"] = (
                static(f"card/Texture2D/CASH_{product1_id}_I.png")
                if product1_id != "-1"
                else "-1"
            )
            card["product2_url"] = (
                static(f"card/Texture2D/CASH_{product2_id}_I.png")
                if product2_id != "-1"
                else "-1"
            )
        else:
            card.url = static(f"card/Texture2D/CARD_{int(card.id // 10 * 10)}.png")
            card.frame = static(f"card/Texture2D/{card.frame}.png")
            card.frame_enh = static("card/Texture2D/UI_Layout_enhance.png")

            product_split = card.product.split(",")
            product1_id, product2_id = product_split[0], product_split[4]
            card.product1_url = (
                static(f"card/Texture2D/CASH_{product1_id}_I.png")
                if product1_id != "-1"
                else "-1"
            )
            card.product2_url = (
                static(f"card/Texture2D/CASH_{product2_id}_I.png")
                if product2_id != "-1"
                else "-1"
            )

    class Meta:
        ordering = ["category", "theme", "episode", "point"]


class Vote(models.Model):
    card = models.ForeignKey(Card, on_delete=models.CASCADE, to_field="id")
    ip = models.GenericIPAddressField()
    tier = models.IntegerField()
    category = models.TextField()
    timestamp = models.DateTimeField(auto_now=True)

    TIER_MAP = {0: "S", 1: "A", 2: "B", 3: "C", 4: "D", 5: "E"}

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["card", "ip", "category"], name="unique_card_ip_category"
            )
        ]

    def __str__(self):
        return f"Vote(id={self.card.id}({self.card.name}), ip={self.ip}, tier={self.tier}({self.TIER_MAP[self.tier]}))"
