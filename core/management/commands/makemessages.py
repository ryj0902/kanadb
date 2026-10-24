from django.core.management.commands import makemessages


class Command(makemessages.Command):
    """비슷한 문자열로 번역을 추측해 fuzzy로 넣지 않는다 (fuzzy 항목은 화면에 쓰이지 않아 혼란만 준다)"""

    msgmerge_options = [*makemessages.Command.msgmerge_options, "--no-fuzzy-matching"]
