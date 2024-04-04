from django.db import models
from django.utils.translation import gettext_lazy as _
from django.templatetags.static import static


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
    EPISODE_EVENT = [(500 + i, f"EV{i}") for i in range(0, 11)]

    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=20)
    name_us = models.CharField(max_length=20)
    category = models.IntegerField()
    rarity = models.IntegerField()
    theme = models.IntegerField()
    tag = models.CharField(max_length=30)  # list of string
    tag_us = models.CharField(max_length=30)  # list of string
    episode = models.IntegerField()
    point = models.IntegerField()
    size = models.IntegerField()
    atk = models.IntegerField()
    defs = models.IntegerField()
    hp = models.IntegerField()
    limit = models.IntegerField()
    enhance = models.IntegerField()
    frame = models.CharField(max_length=30)  # image file name
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
    link = models.CharField(max_length=40)  # list of id
    producible = models.BooleanField()
    enh_prev = models.IntegerField()  # card id
    enh_next = models.IntegerField()  # card id

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
        if type(card) == dict:
            card["category"] = Card.category_map[card["category"]]
            card["rarity"] = Card.rarity_map[card["rarity"]]
            card["theme"] = Card.theme_map[card["theme"]]
            episode = card["episode"]
            prefix = "EP" if episode // 100 == 1 else "EV"
            card["episode"] = prefix + str(card["episode"] % 100)
        else:
            card.category = Card.category_map[card.category]
            card.rarity = Card.rarity_map[card.rarity]
            card.theme = Card.theme_map[card.theme]
            episode = card.episode
            prefix = "EP" if episode // 100 == 1 else "EV"
            card.episode = prefix + str(card.episode % 100)

    @staticmethod
    def parse_static_url(card):
        if type(card) == dict:
            card["url"] = static(
                f"card/Texture2D/CARD_{int(card['id'] // 10 * 10)}.png"
            )
            card["frame"] = static(f"card/Texture2D/{card['frame']}.png")
            card["frame_enh"] = static(f"card/Texture2D/UI_Layout_enhance.png")
        else:
            card.url = static(f"card/Texture2D/CARD_{int(card.id // 10 * 10)}.png")
            card.frame = static(f"card/Texture2D/{card.frame}.png")
            card.frame_enh = static(f"card/Texture2D/UI_Layout_enhance.png")

    class Meta:
        ordering = ["category", "theme", "episode", "point"]
