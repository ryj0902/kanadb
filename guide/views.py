import os
from glob import glob

from django.shortcuts import render
from django.utils.translation import get_language
from django.utils.translation import gettext as _
from markdown import markdown


def index(request):
    language_code = get_language()
    context = {"contents": []}

    for file in sorted(glob(f"templates/guide/{language_code}/*.md")):
        with open(file, "r", encoding="utf-8") as f:
            line = f.readline()

        title = line.rstrip()
        title = title.split("# ")[1]

        context["contents"].append([os.path.basename(file), title])

    return render(request, "guide/index.html", context)


def guide_detail(request, guide_name):
    language_code = get_language()
    markdown_path = f"templates/guide/{language_code}/{guide_name}"
    with open(markdown_path, "r", encoding="utf-8") as file:
        markdown_content = file.read()

    html_content = markdown(markdown_content)

    context = {
        "html_content": html_content,
        "horizontal_layout": _("가로 모드"),
        "vertical_layout": _("세로 모드"),
    }

    return render(request, "guide/guide_detail.html", context)
