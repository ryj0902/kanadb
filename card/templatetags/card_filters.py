from django import template

register = template.Library()


@register.filter
def split_by_9(value):
    return [value[i : i + 9] for i in range(0, len(value), 9)]
