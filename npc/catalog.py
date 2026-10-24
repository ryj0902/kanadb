"""NPC 목록 페이지와 상세 페이지 탐색(난이도/층 이동)의 단일 출처

목록 표와 탐색은 모두 이 데이터로 만들어진다. id 규칙으로 계산하지 않으므로
규칙이 다른 이벤트도 데이터만 추가하면 목록과 탐색이 함께 동작한다.

- 던전 추가/복각: 해당 Section의 Block에 Dungeon 한 줄 추가 (복각은 복사)
- 숨김: 해당 줄을 주석 처리 (목록과 탐색에서 함께 빠진다)
- 층 id가 연속이 아니면 floors() 대신 [Floor(id, 표시 이름), ...]로 직접 나열
- 카탈로그에 없는 NPC id는 상세 페이지에서 덱만 표시하고 탐색 UI를 숨긴다

배치(Block.layout)
- ROWS    : 열 = 던전, 행 = 난이도 (시즌, 이벤트 등)
- COLUMNS : 블록 = 던전 하나, 열 = 난이도 (요일 던전, 파이트, 차원의 탑)
"""

from dataclasses import dataclass, field

from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

ROWS = "rows"
COLUMNS = "columns"

FLOOR_LABELS = [
    _("1층"),
    _("2층"),
    _("3층"),
    _("4층"),
    _("5층"),
    _("6층"),
    _("7층"),
    _("8층"),
    _("9층"),
    _("10층"),
    _("11층"),
    _("12층"),
    _("13층"),
    _("14층"),
    _("15층"),
    _("16층"),
    _("17층"),
    _("18층"),
    _("19층"),
    _("20층"),
]


class Text:
    """여러 조각(번역 문자열 포함)을 이어 붙인 표시 문자열"""

    def __init__(self, *parts, sep=" "):
        self.parts = parts
        self.sep = sep

    def __html__(self):
        return mark_safe(self.sep.join(conditional_escape(part) for part in self.parts))

    def __str__(self):
        return str(self.__html__())


@dataclass(frozen=True)
class Floor:
    id: int
    label: object  # 목록에 표시되는 이름


@dataclass
class Difficulty:
    label: object  # 상세 페이지 난이도 선택(및 ROWS 배치의 난이도 행)에 표시
    floors: list
    header: object = None  # COLUMNS 배치의 열 머리글 (없으면 label)

    @property
    def column_header(self):
        return self.header if self.header is not None else self.label


@dataclass
class Dungeon:
    name: object  # ROWS 배치의 열 머리글 (모두 None이면 머리글 행 생략)
    difficulties: list
    continuous_floors: bool = False  # 난이도 경계를 넘어 이전/다음 층 이동


@dataclass
class Block:
    dungeons: list  # None은 빈 칸
    layout: str = ROWS
    title: object = None
    show_difficulty: bool = True  # ROWS 배치에서 난이도 행 표시

    @property
    def has_header(self):
        return any(
            dungeon is not None and dungeon.name is not None
            for dungeon in self.dungeons
        )

    @property
    def difficulty_rows(self):
        """ROWS 배치: 난이도 순서별로 열(던전)마다의 난이도 (없으면 None)"""
        count = max((len(d.difficulties) for d in self.dungeons if d), default=0)
        return [
            [
                d.difficulties[i] if d and i < len(d.difficulties) else None
                for d in self.dungeons
            ]
            for i in range(count)
        ]


@dataclass
class Section:
    title: object
    blocks: list = field(default_factory=list)
    note: object = None


def floors(first_id, count, first_label=1):
    """id가 연속인 층들 (표시 이름: N층)"""
    return [
        Floor(first_id + i, FLOOR_LABELS[first_label - 1 + i]) for i in range(count)
    ]


def standard_difficulties(first_id, floor_count):
    """이지/노말/하드 (난이도마다 id 천의 자리 +1)"""
    labels = [_("이지"), _("노말"), _("하드")]
    return [
        Difficulty(label, floors(first_id + i * 1000, floor_count))
        for i, label in enumerate(labels)
    ]


def single(floor_list):
    """난이도 구분이 없는 던전"""
    return [Difficulty(_("이지"), floor_list)]


# fmt: off
SEASON_1 = Section(Text(_("시즌"), "1"), blocks=[
    Block([
        Dungeon(Text("EP0", _("시공관리국")), standard_difficulties(11001101, 5)),
        Dungeon(Text("EP1", _("변경 유적")), standard_difficulties(11011101, 5)),
        Dungeon(Text("EP2", _("마녀의 탑")), standard_difficulties(11021101, 5)),
        Dungeon(Text("EP3", _("죽림향")), standard_difficulties(11031101, 5)),
        Dungeon(Text("EP4", _("크룩스 훈련소")), standard_difficulties(11041101, 5)),
        Dungeon(Text("EP5", _("리니아관")), standard_difficulties(11051101, 5)),
        Dungeon(Text("EP6", _("흡혈귀의 땅")), standard_difficulties(11061101, 5)),
        Dungeon(Text("EP7", _("비타 학교")), standard_difficulties(11071101, 5)),
        Dungeon(Text("EP8", _("심상 세계")), standard_difficulties(11081101, 5)),
    ]),
])

SEASON_2 = Section(Text(_("시즌"), "2"), blocks=[
    Block([
        Dungeon(Text("EP9", _("카타콤")), standard_difficulties(11091101, 5)),
        Dungeon(Text("EP10", _("고대 성역")), standard_difficulties(11101101, 5)),
        Dungeon(Text("EP11", _("SS흥신소")), standard_difficulties(11111101, 5)),
        Dungeon(Text("EP12", _("비타 도서관")), standard_difficulties(11121101, 5)),
        Dungeon(Text("EP13", _("매장 도서관")), standard_difficulties(11131101, 5)),
        Dungeon(Text("EP14", _("로일 시티")), standard_difficulties(11141101, 5)),
        Dungeon(Text("EP15", _("뮤지시터랜드")), standard_difficulties(11151101, 5)),
        Dungeon(Text("EP16", _("카나의 제단")), standard_difficulties(11161101, 5)),
    ]),
])

SEASON_3 = Section(Text(_("시즌"), "3"), blocks=[
    Block([
        Dungeon(Text("EP17", _("묘족의 유적")), standard_difficulties(11171101, 5)),
    ]),
])

EVENT = Section(_("이벤트"), blocks=[
    Block([
        Dungeon(Text("EV1", _("겨울의 숲")), standard_difficulties(99011101, 5)),
        Dungeon(Text("EV2", _("화신의 저택")), standard_difficulties(99021101, 5)),
        Dungeon(Text("EV3", _("소녀의 방")), standard_difficulties(99031101, 5)),
        Dungeon(Text("EV4", _("사탕 공장")), standard_difficulties(99041101, 5)),
        Dungeon(Text("EV5", _("이상한 나라")), standard_difficulties(99051101, 5)),
        Dungeon(Text("EV6", _("꿈의 바다")), standard_difficulties(99061101, 5)),
        Dungeon(Text("EV7", _("할로윈랜드")), standard_difficulties(99071101, 5)),
        Dungeon(Text("EV8", _("드림 월드")), standard_difficulties(99081101, 5)),
    ]),
    Block([
        Dungeon(Text("EV9", _("크룩스 리조트")), standard_difficulties(99091101, 5)),
        Dungeon(Text("EV10", _("시니아의 별장")), standard_difficulties(99101101, 5)),
        Dungeon(Text("EV11", _("화신의 마을")), standard_difficulties(99111101, 5)),
        None,  # 빈 칸
        None,  # 빈 칸
        None,  # 빈 칸
        None,  # 빈 칸
        Dungeon(Text("EV18", _("꿈의 스테이지")), standard_difficulties(99181101, 5)),
    ]),
])

SHADOWLAND = Section(Text(_("쉐도우랜드"), "(work in progress)"), blocks=[
    Block([
        Dungeon(None, single([Floor(21001101, _("유령의 집"))])),
        Dungeon(None, single([Floor(21011101, _("회전 목마"))])),
        Dungeon(None, single([Floor(21021101, _("대관람차"))])),
        Dungeon(None, single([Floor(21031101, _("그림자 열차"))])),
        Dungeon(None, single([Floor(21041101, _("그림자 퍼레이드"))])),
    ], show_difficulty=False),
])

EMPIRE_LAB = Section(_("제국 연구소"), blocks=[
    Block([
        Dungeon(None, [
            Difficulty(_("월"), [
                Floor(98011101, _("연구소 A동")),
                Floor(98012101, _("연구소 B동")),
                Floor(98013101, _("연구소 C동")),
                Floor(98014101, _("연구소 D동")),
                Floor(98015101, _("연구소 E동")),
            ]),
            Difficulty(_("화"), [
                Floor(98021101, _("연구소 A동")),
                Floor(98022101, _("연구소 B동")),
                Floor(98023101, _("연구소 C동")),
                Floor(98024101, _("연구소 D동")),
                Floor(98025101, _("연구소 E동")),
            ]),
            Difficulty(_("수"), [
                Floor(98031101, _("연구소 A동")),
                Floor(98032101, _("연구소 B동")),
                Floor(98033101, _("연구소 C동")),
                Floor(98034101, _("연구소 D동")),
                Floor(98035101, _("연구소 E동")),
            ]),
            Difficulty(_("목"), [
                Floor(98041101, _("연구소 A동")),
                Floor(98042101, _("연구소 B동")),
                Floor(98043101, _("연구소 C동")),
                Floor(98044101, _("연구소 D동")),
                Floor(98045101, _("연구소 E동")),
            ]),
            Difficulty(_("금"), [
                Floor(98051101, _("연구소 A동")),
                Floor(98052101, _("연구소 B동")),
                Floor(98053101, _("연구소 C동")),
                Floor(98054101, _("연구소 D동")),
                Floor(98055101, _("연구소 E동")),
            ]),
            Difficulty(_("토"), [
                Floor(98061101, _("연구소 A동")),
                Floor(98062101, _("연구소 B동")),
                Floor(98063101, _("연구소 C동")),
                Floor(98064101, _("연구소 D동")),
                Floor(98065101, _("연구소 E동")),
            ]),
            Difficulty(_("일"), [
                Floor(98071101, _("연구소 A동")),
                Floor(98072101, _("연구소 B동")),
                Floor(98073101, _("연구소 C동")),
                Floor(98074101, _("연구소 D동")),
                Floor(98075101, _("연구소 E동")),
            ]),
        ]),
    ], layout=COLUMNS),
])

MUSPELHEIM = Section(_("무스펠헤임"), blocks=[
    Block([
        Dungeon(_("명계의 왕"), single(floors(97001101, 4))),
        Dungeon(_("괴한 습격 사건"), single(floors(97011101, 4))),
        Dungeon(_("메이드 밴드 파티"), single(floors(97021101, 4))),
        Dungeon(_("막내의 일기"), single(floors(97031101, 4))),
        Dungeon(_("새로운 만월"), single(floors(97041101, 4))),
        Dungeon(_("테니스 체험"), single(floors(97051101, 4))),
    ], show_difficulty=False),
    Block([
        Dungeon(_("시타 빌로사"), single(floors(97061101, 4))),
        Dungeon(_("시니아 퍼시피카"), single(floors(97071101, 4))),
        Dungeon(_("루티카 프리벤터"), single(floors(97081101, 4))),
        Dungeon(_("아이리 플리나"), single(floors(97091101, 4))),
        Dungeon(_("문의 저편으로"), single(floors(97101101, 4))),
        Dungeon(_("코발트색 추억"), single(floors(97111101, 4))),
    ], show_difficulty=False),
])

RIFT = Section(_("차원의 틈"), blocks=[
    Block([
        Dungeon("NORMAL", single([
            Floor(95001101, _("시작의 관찰자")),
            Floor(95001102, _("은둔형 관찰자")),
            Floor(95001103, _("수집형 관찰자")),
            Floor(95001104, _("게임광 관찰자")),
        ])),
        Dungeon("BOSS", single([Floor(96001101, _("초월의 관찰자"))])),
    ], show_difficulty=False),
])

FIGHT = Section("Fight", blocks=[
    Block([
        Dungeon(None, [
            Difficulty("E", [
                Floor(9101, Text(_("해변의"), _("시타"))),
                Floor(9102, Text(_("해변의"), _("시니아"))),
                Floor(9103, Text(_("해변의"), _("루티카"))),
                Floor(9104, Text(_("해변의"), _("아이리"))),
                Floor(9105, Text(_("해변의"), _("아스미스"))),
                Floor(9106, Text(_("해변의"), _("리누스"))),
                Floor(9107, Text(_("해변의"), _("로자리아"))),
                Floor(9108, Text(_("해변의"), _("헬레나"))),
                Floor(9109, Text(_("어린이"), _("이리나"))),
                Floor(9110, Text(_("어린이"), _("마리메"))),
                Floor(9111, Text(_("어린이"), _("아우디레"))),
                Floor(9112, Text(_("어린이"), _("라임"))),
            ], header=Text("E", _("시작의 관찰자"), sep='<br>')),
            Difficulty("D", [
                Floor(9201, Text(_("수영복의"), _("베르니카"))),
                Floor(9202, Text(_("수영복의"), _("로제"))),
                Floor(9203, Text(_("수영복의"), _("제이나"))),
                Floor(9204, Text(_("수영복의"), _("앤즈"))),
                Floor(9205, Text(_("수영복의"), _("레이나"))),
                Floor(9206, Text(_("수영복의"), _("세븐"))),
                Floor(9207, Text(_("수영복의"), _("핀테일"))),
                Floor(9208, Text(_("수영복의"), _("몽쉘"))),
                Floor(9209, Text(_("어린이"), _("베르니카"))),
                Floor(9210, Text(_("어린이"), _("리니아"))),
                Floor(9211, Text(_("어린이"), _("제이나"))),
                Floor(9212, Text(_("어린이"), _("시온 리온"))),
            ], header=Text("D", _("은둔형 관찰자"), sep='<br>')),
            Difficulty("C", [
                Floor(9301, Text(_("수영복의"), _("시타"))),
                Floor(9302, Text(_("수영복의"), _("시니아"))),
                Floor(9303, Text(_("수영복의"), _("루티카"))),
                Floor(9304, Text(_("수영복의"), _("아이리"))),
                Floor(9305, Text(_("수영복의"), _("아스미스"))),
                Floor(9306, Text(_("수영복의"), _("리누스"))),
                Floor(9307, Text(_("수영복의"), _("로자리아"))),
                Floor(9308, Text(_("수영복의"), _("헬레나"))),
                Floor(9309, Text(_("피오나"), _("센트리버"))),
                Floor(9310, Text(_("엔프레스"), _("퍼시피카"))),
                Floor(9311, Text(_("클라라"), _("알트하임"))),
                Floor(9312, Text(_("루나"), _("플리나"))),
            ], header=Text("C", _("수집형 관찰자"), sep='<br>')),
            Difficulty("B", [
                Floor(9401, Text(_("수영복의"), _("리안나"))),
                Floor(9402, Text(_("수영복의"), _("리니아"))),
                Floor(9403, Text(_("수영복의"), _("클라리스"))),
                Floor(9404, Text(_("수영복의"), _("시온 리온"))),
                Floor(9405, Text(_("한여름의"), _("시타"))),
                Floor(9406, Text(_("한여름의"), _("시니아"))),
                Floor(9407, Text(_("한여름의"), _("루티카"))),
                Floor(9408, Text(_("한여름의"), _("아이리"))),
                Floor(9409, Text(_("어린이"), _("아스미스"))),
                Floor(9410, Text(_("어린이"), _("리누스"))),
                Floor(9411, Text(_("어린이"), _("로자리아"))),
                Floor(9412, Text(_("어린이"), _("헬레나"))),
            ], header=Text("B", _("매니저 관찰자"), sep='<br>')),
            Difficulty("A", [
                Floor(9501, Text(_("수영복의"), _("리안나"))),
                Floor(9502, Text(_("수영복의"), _("리니아"))),
                Floor(9503, Text(_("수영복의"), _("클라리스"))),
                Floor(9504, Text(_("수영복의"), _("시온 리온"))),
                Floor(9505, Text(_("한여름의"), _("시타"))),
                Floor(9506, Text(_("한여름의"), _("시니아"))),
                Floor(9507, Text(_("한여름의"), _("루티카"))),
                Floor(9508, Text(_("한여름의"), _("아이리"))),
                Floor(9509, Text(_("어린이"), _("아스미스"))),
                Floor(9510, Text(_("어린이"), _("리누스"))),
                Floor(9511, Text(_("어린이"), _("로자리아"))),
                Floor(9512, Text(_("어린이"), _("헬레나"))),
            ], header=Text("A", _("게임광 관찰자"), sep='<br>')),
        ]),
    ], layout=COLUMNS),
])

TOWER = Section(_("차원의 탑"), note=_("20층 단위 반복"), blocks=[
    Block([
        Dungeon(None, [
            Difficulty("E", floors(81307100, 4)),
            Difficulty("D", floors(81307104, 4, first_label=5)),
            Difficulty("C", floors(81307108, 4, first_label=9)),
            Difficulty("B", floors(81307112, 4, first_label=13)),
            Difficulty("A", floors(81307116, 4, first_label=17)),
        ], continuous_floors=True),
    ], layout=COLUMNS, title=_("여름의 탑")),
    Block([
        Dungeon(None, [
            Difficulty("E", floors(81327100, 4)),
            Difficulty("D", floors(81327104, 4, first_label=5)),
            Difficulty("C", floors(81327108, 4, first_label=9)),
            Difficulty("B", floors(81327112, 4, first_label=13)),
            Difficulty("A", floors(81327116, 4, first_label=17)),
        ], continuous_floors=True),
    ], layout=COLUMNS, title=_("어린이의 탑")),
    Block([
        Dungeon(None, [
            Difficulty("E", floors(81337100, 4)),
            Difficulty("D", floors(81337104, 4, first_label=5)),
            Difficulty("C", floors(81337108, 4, first_label=9)),
            Difficulty("B", floors(81337112, 4, first_label=13)),
            Difficulty("A", floors(81337116, 4, first_label=17)),
        ], continuous_floors=True),
    ], layout=COLUMNS, title=_("바다의 탑")),
])
# fmt: on

CATALOG = [
    SEASON_1,
    SEASON_2,
    SEASON_3,
    EVENT,
    SHADOWLAND,
    EMPIRE_LAB,
    MUSPELHEIM,
    RIFT,
    FIGHT,
    TOWER,
]
