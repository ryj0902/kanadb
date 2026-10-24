from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe


class Text:
    """여러 조각(번역 문자열 포함)을 이어 붙인 표시 문자열

    번역은 화면에 그릴 때 이루어지므로 모듈 수준 상수에 써도 언어가 맞게 나온다.
    """

    def __init__(self, *parts, sep=" "):
        self.parts = parts
        self.sep = sep

    def __html__(self):
        return mark_safe(self.sep.join(conditional_escape(part) for part in self.parts))

    def __str__(self):
        return str(self.__html__())
